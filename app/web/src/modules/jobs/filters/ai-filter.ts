import { anthropic } from "@ai-sdk/anthropic";
import { generateObject } from "ai";
import { z } from "zod";
import { readFileSync } from "fs";
import { join } from "path";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

const RelevanceSchema = z.object({
  isRelevant: z.boolean(),
  reason: z.string(),
  confidence: z.enum(["high", "medium", "low"]),
});

type RelevanceResult = z.infer<typeof RelevanceSchema>;

// ---------------------------------------------------------------------------
// Job Profile Loading
// ---------------------------------------------------------------------------

let cachedJobProfile: string | null = null;

function loadJobProfile(): string {
  if (cachedJobProfile) return cachedJobProfile;

  try {
    const profilePath = join(process.cwd(), "../..", "config", "job-profile.md");
    cachedJobProfile = readFileSync(profilePath, "utf-8");
    return cachedJobProfile;
  } catch (error) {
    console.error("Failed to load job profile:", error);
    // Fallback to basic profile if file not found
    return `
# Job Preferences

## Target roles
- AI/ML Engineer, AI Research Engineer, AI Observability Engineer, Full-Stack Engineer (AI-focused products)
- Seniority: Mid-level to Senior

## Dealbreakers
- Junior roles
- Pure frontend roles with no AI/ML component
- Marketing, sales, or office management positions
    `.trim();
  }
}

// ---------------------------------------------------------------------------
// AI Filter
// ---------------------------------------------------------------------------

export async function isJobRelevant(
  description: string,
  title: string | null,
  company: string
): Promise<RelevanceResult> {
  // Early exit if filter is disabled
  if (process.env.ENABLE_JOB_FILTER === "false") {
    return {
      isRelevant: true,
      reason: "Filter disabled",
      confidence: "high",
    };
  }

  // Check for API key
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn("ANTHROPIC_API_KEY not set, skipping AI filtering");
    return {
      isRelevant: true,
      reason: "API key not configured",
      confidence: "high",
    };
  }

  const jobProfile = loadJobProfile();

  const prompt = `You are a job relevance classifier. Given a candidate's job profile and a job posting, determine if the job is relevant to the candidate's background and interests.

# Candidate Profile
${jobProfile}

# Job Posting
Company: ${company}
Title: ${title ?? "Not specified"}
Description:
${description}

# Task
Analyze if this job is relevant to the candidate. Consider:
1. Does the role align with their target industries (AI/ML, AI safety, frontier AI)?
2. Does it match their technical skills and interests?
3. Is the seniority level appropriate (mid-level to senior)?
4. Does it avoid dealbreakers (pure frontend, marketing, office management, crypto, military)?

Be CONSERVATIVE - only mark as NOT relevant if the job is clearly unrelated (e.g., office manager, sales, marketing roles with no AI component, junior roles, etc.).

If the job has ANY AI/ML component or is at a frontier AI company, mark it as relevant even if the title seems generic.`;

  try {
    const result = await generateObject({
      model: anthropic("claude-3-5-haiku-20241022"),
      schema: RelevanceSchema,
      prompt,
      temperature: 0.3, // Low temperature for consistency
    });

    return result.object;
  } catch (error) {
    console.error("AI filtering failed:", error);
    // Fail open - don't filter out jobs if AI call fails
    return {
      isRelevant: true,
      reason: "Filter error, defaulting to relevant",
      confidence: "low",
    };
  }
}

// ---------------------------------------------------------------------------
// Batch filtering for efficiency
// ---------------------------------------------------------------------------

export async function filterJobsBatch(
  jobs: Array<{ description: string; title: string | null; company: string }>
): Promise<RelevanceResult[]> {
  // Process in parallel with a concurrency limit
  const BATCH_SIZE = 5;
  const results: RelevanceResult[] = [];

  for (let i = 0; i < jobs.length; i += BATCH_SIZE) {
    const batch = jobs.slice(i, i + BATCH_SIZE);
    const batchResults = await Promise.all(
      batch.map((job) =>
        isJobRelevant(job.description, job.title, job.company)
      )
    );
    results.push(...batchResults);
  }

  return results;
}
