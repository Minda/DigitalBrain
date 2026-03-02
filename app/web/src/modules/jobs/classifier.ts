import { generateObject } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { z } from "zod";
import { db } from "@/modules/jobs/db";
import { jobs, events, classificationRuns } from "@/modules/jobs/schema";
import { eq, sql } from "drizzle-orm";
import fs from "fs";
import path from "path";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const MODEL_ID = "claude-haiku-4-5-20251001";
const CONCURRENCY = 10;
const PROFILE_PATH = path.resolve(process.cwd(), "../../config/job-profile.md");

// ---------------------------------------------------------------------------
// Classification schema (structured output)
// ---------------------------------------------------------------------------
const ClassificationSchema = z.object({
  summary: z
    .string()
    .describe("2-3 sentence summary of the job posting"),
  relevance: z
    .number()
    .int()
    .describe(
      "Relevance to user profile (1-5): 1=poor match, 2=weak, 3=moderate, 4=good, 5=strong"
    ),
  breakdown: z.object({
    roleMatch: z
      .number()
      .int()
      .describe("How well the role matches target roles (1-5)"),
    techMatch: z
      .number()
      .int()
      .describe("How well tech stack matches interests (1-5)"),
    locationFit: z
      .number()
      .int()
      .describe("How well location matches preferences (1-5)"),
    dealbreakers: z
      .boolean()
      .describe("True if any dealbreakers are present"),
    reasoning: z
      .string()
      .describe("1-2 sentence explanation of the score"),
  }),
});

type ClassificationResult = z.infer<typeof ClassificationSchema>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

export function loadUserProfile(): string {
  if (!fs.existsSync(PROFILE_PATH)) {
    throw new Error(
      `Job profile not found at ${PROFILE_PATH}. Create config/job-profile.md with your preferences before classifying.`
    );
  }
  const content = fs.readFileSync(PROFILE_PATH, "utf-8").trim();

  // Check if it's still the template (has placeholder brackets)
  if (content.includes("[e.g.,")) {
    throw new Error(
      "Job profile still contains placeholder text. Edit config/job-profile.md with your actual preferences before classifying."
    );
  }

  return content;
}

interface FewShotExample {
  company: string;
  title: string | null;
  location: string | null;
  description: string;
  relevance: number;
}

async function loadFewShotExamples(): Promise<FewShotExample[]> {
  const corrections = await db
    .select({
      jobId: events.jobId,
      payload: events.payload,
    })
    .from(events)
    .where(eq(events.eventType, "relevance_corrected"))
    .orderBy(sql`${events.createdAt} DESC`)
    .limit(10);

  if (corrections.length === 0) return [];

  const examples: FewShotExample[] = [];

  for (const correction of corrections) {
    if (!correction.jobId || !correction.payload) continue;

    const payload = JSON.parse(correction.payload) as {
      newRelevance: number;
    };

    const [job] = await db
      .select({
        company: jobs.company,
        title: jobs.title,
        location: jobs.location,
        description: jobs.description,
      })
      .from(jobs)
      .where(eq(jobs.id, correction.jobId))
      .limit(1);

    if (job) {
      examples.push({
        ...job,
        relevance: payload.newRelevance,
      });
    }
  }

  return examples;
}

function buildFewShotBlock(examples: FewShotExample[]): string {
  if (examples.length === 0) return "";

  const lines = examples.map((ex) => {
    const label = ex.title ?? "Untitled";
    const loc = ex.location ? ` (${ex.location})` : "";
    const desc = ex.description.slice(0, 150).replace(/\n/g, " ");
    return `- ${ex.company} — ${label}${loc}: relevance=${ex.relevance}\n  "${desc}..."`;
  });

  return `\nHere are examples of how the user rated previous jobs (use these to calibrate):\n${lines.join("\n")}\n`;
}

// ---------------------------------------------------------------------------
// Single job classification
// ---------------------------------------------------------------------------

interface JobToClassify {
  id: number;
  company: string;
  title: string | null;
  location: string | null;
  description: string;
}

async function classifySingleJob(
  job: JobToClassify,
  profile: string,
  fewShotBlock: string
): Promise<{ jobId: number; result: ClassificationResult; usage: { input: number; output: number } }> {
  const { object, usage } = await generateObject({
    model: anthropic(MODEL_ID),
    schema: ClassificationSchema,
    system: `You are a job relevance classifier. Given a user's job preferences and a job posting, classify the job on a 1-5 relevance scale.

User Profile:
${profile}
${fewShotBlock}
Rate the job based on how well it matches the user's preferences. Be calibrated: most jobs should be 2-3, only exceptional matches should be 5.`,
    prompt: `Company: ${job.company}
Title: ${job.title ?? "Not specified"}
Location: ${job.location ?? "Not specified"}

Description:
${job.description}`,
  });

  // Clamp values to 1-5 range (in case model ignores instructions)
  const clampedResult = {
    ...object,
    relevance: Math.max(1, Math.min(5, object.relevance)),
    breakdown: {
      ...object.breakdown,
      roleMatch: Math.max(1, Math.min(5, object.breakdown.roleMatch)),
      techMatch: Math.max(1, Math.min(5, object.breakdown.techMatch)),
      locationFit: Math.max(1, Math.min(5, object.breakdown.locationFit)),
    },
  };

  return {
    jobId: job.id,
    result: clampedResult,
    usage: {
      input: usage.inputTokens ?? 0,
      output: usage.outputTokens ?? 0,
    },
  };
}

// ---------------------------------------------------------------------------
// Batch classification
// ---------------------------------------------------------------------------

export interface ClassifyOptions {
  batchSize?: number;
  force?: boolean;
}

export interface ClassifyResult {
  runId: number;
  classified: number;
  remaining: number;
  model: string;
  tokensUsed: { input: number; output: number };
}

export async function classifyJobs(
  options: ClassifyOptions = {}
): Promise<ClassifyResult> {
  const { batchSize = 50, force = false } = options;

  // Load profile (throws if missing or placeholder)
  const profile = loadUserProfile();

  // Load few-shot examples from user corrections
  const examples = await loadFewShotExamples();
  const fewShotBlock = buildFewShotBlock(examples);

  // Query jobs to classify
  const whereClause = force
    ? sql`1=1`
    : sql`${jobs.relevance} = 0 OR ${jobs.relevance} IS NULL`;

  const jobsToClassify: JobToClassify[] = await db
    .select({
      id: jobs.id,
      company: jobs.company,
      title: jobs.title,
      location: jobs.location,
      description: jobs.description,
    })
    .from(jobs)
    .where(whereClause)
    .limit(batchSize);

  if (jobsToClassify.length === 0) {
    return {
      runId: 0,
      classified: 0,
      remaining: 0,
      model: MODEL_ID,
      tokensUsed: { input: 0, output: 0 },
    };
  }

  // Count remaining (beyond this batch)
  const [totalUnclassified] = await db
    .select({ count: sql<number>`count(*)` })
    .from(jobs)
    .where(whereClause);
  const totalRemaining = (totalUnclassified?.count ?? 0) - jobsToClassify.length;

  // Create classification run record
  const now = new Date().toISOString();
  const [run] = await db
    .insert(classificationRuns)
    .values({
      startedAt: now,
      model: MODEL_ID,
      jobsTotal: jobsToClassify.length,
      status: "running",
    })
    .returning();

  let totalInput = 0;
  let totalOutput = 0;
  let classified = 0;

  try {
    // Process in concurrent batches
    for (let i = 0; i < jobsToClassify.length; i += CONCURRENCY) {
      const batch = jobsToClassify.slice(i, i + CONCURRENCY);

      const results = await Promise.allSettled(
        batch.map((job) => classifySingleJob(job, profile, fewShotBlock))
      );

      for (const result of results) {
        if (result.status === "rejected") {
          console.error("Classification failed for job:", result.reason);
          continue;
        }

        const { jobId, result: classification, usage } = result.value;
        totalInput += usage.input;
        totalOutput += usage.output;

        // Update the job record
        await db
          .update(jobs)
          .set({
            relevance: classification.relevance,
            score: classification.relevance, // use relevance as score for now
            scoreBreakdown: JSON.stringify(classification.breakdown),
            summary: classification.summary,
            updatedAt: new Date().toISOString(),
          })
          .where(eq(jobs.id, jobId));

        classified++;
      }
    }

    // Update run record
    await db
      .update(classificationRuns)
      .set({
        completedAt: new Date().toISOString(),
        jobsClassified: classified,
        jobsSkipped: jobsToClassify.length - classified,
        inputTokens: totalInput,
        outputTokens: totalOutput,
        status: "completed",
      })
      .where(eq(classificationRuns.id, run.id));
  } catch (error) {
    await db
      .update(classificationRuns)
      .set({
        completedAt: new Date().toISOString(),
        jobsClassified: classified,
        inputTokens: totalInput,
        outputTokens: totalOutput,
        status: "failed",
        error: error instanceof Error ? error.message : String(error),
      })
      .where(eq(classificationRuns.id, run.id));
    throw error;
  }

  return {
    runId: run.id,
    classified,
    remaining: Math.max(0, totalRemaining),
    model: MODEL_ID,
    tokensUsed: { input: totalInput, output: totalOutput },
  };
}
