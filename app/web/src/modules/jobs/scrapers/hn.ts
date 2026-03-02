import { db } from "@/modules/jobs/db";
import { jobs, scrapeRuns } from "@/modules/jobs/schema";
import type { NewJob } from "@/modules/jobs/schema";
import { eq, and } from "drizzle-orm";
import { isJobRelevant } from "@/modules/jobs/filters/ai-filter";
import { classifyJobs } from "@/modules/jobs/classifier";

// ---------------------------------------------------------------------------
// Algolia HN API types
// ---------------------------------------------------------------------------

interface AlgoliaSearchHit {
  objectID: string;
  title: string;
  story_text?: string | null;
  author: string;
  created_at: string;
  num_comments: number;
  [key: string]: unknown;
}

interface AlgoliaSearchResponse {
  hits: AlgoliaSearchHit[];
  nbHits: number;
  page: number;
  nbPages: number;
  hitsPerPage: number;
}

interface AlgoliaItemChild {
  id: number;
  type: string;
  text: string | null;
  author: string | null;
  created_at: string;
  children?: AlgoliaItemChild[];
}

interface AlgoliaItemResponse {
  id: number;
  title: string;
  type: string;
  text: string | null;
  author: string;
  created_at: string;
  children: AlgoliaItemChild[];
}

// ---------------------------------------------------------------------------
// Thread discovery
// ---------------------------------------------------------------------------

export async function findLatestHiringThread(): Promise<{
  storyId: string;
  title: string;
} | null> {
  const url =
    "https://hn.algolia.com/api/v1/search?query=%22Ask%20HN%3A%20Who%20is%20hiring%22&tags=story&hitsPerPage=5";

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Algolia search failed: ${res.status} ${res.statusText}`);
  }

  const data: AlgoliaSearchResponse = await res.json();

  const match = data.hits.find((hit) => {
    const lower = hit.title.toLowerCase();
    return (
      lower.includes("who is hiring") &&
      !lower.includes("who wants to be hired") &&
      !lower.includes("freelancer")
    );
  });

  if (!match) return null;

  return { storyId: match.objectID, title: match.title };
}

// ---------------------------------------------------------------------------
// Comment fetching
// ---------------------------------------------------------------------------

export async function fetchThreadComments(
  storyId: string
): Promise<AlgoliaItemChild[]> {
  const url = `https://hn.algolia.com/api/v1/items/${storyId}`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(
      `Algolia item fetch failed: ${res.status} ${res.statusText}`
    );
  }

  const data: AlgoliaItemResponse = await res.json();

  return (data.children ?? []).filter(
    (child) => child.type === "comment" && child.text != null
  );
}

// ---------------------------------------------------------------------------
// HTML / text helpers
// ---------------------------------------------------------------------------

const HTML_ENTITIES: Record<string, string> = {
  "&amp;": "&",
  "&lt;": "<",
  "&gt;": ">",
  "&quot;": '"',
  "&#x27;": "'",
  "&#39;": "'",
  "&apos;": "'",
  "&#x2F;": "/",
  "&nbsp;": " ",
};

export function stripHtml(html: string): string {
  let text = html;

  // Convert <p> tags to double newlines
  text = text.replace(/<p\s*\/?>/gi, "\n\n");

  // Convert <br> tags to single newlines
  text = text.replace(/<br\s*\/?>/gi, "\n");

  // Extract href from <a> tags, keep the URL
  text = text.replace(
    /<a\s[^>]*href=["']([^"']*)["'][^>]*>(.*?)<\/a>/gi,
    (_match, href: string, inner: string) => {
      // If the visible text IS the URL (or very similar), just show the URL
      const trimmedInner = inner.replace(/<[^>]*>/g, "").trim();
      if (
        trimmedInner === href ||
        trimmedInner === href.replace(/^https?:\/\//, "")
      ) {
        return href;
      }
      return `${trimmedInner} (${href})`;
    }
  );

  // Remove all remaining HTML tags
  text = text.replace(/<[^>]*>/g, "");

  // Decode HTML entities
  for (const [entity, char] of Object.entries(HTML_ENTITIES)) {
    text = text.replaceAll(entity, char);
  }
  // Decode numeric HTML entities (decimal)
  text = text.replace(/&#(\d+);/g, (_match, code: string) =>
    String.fromCharCode(Number(code))
  );
  // Decode numeric HTML entities (hex)
  text = text.replace(/&#x([0-9a-fA-F]+);/g, (_match, code: string) =>
    String.fromCharCode(parseInt(code, 16))
  );

  // Collapse excessive newlines (3+ into 2)
  text = text.replace(/\n{3,}/g, "\n\n");

  return text.trim();
}

// ---------------------------------------------------------------------------
// Field parsers (HN "Who is hiring" convention: Company | Title | Location)
// ---------------------------------------------------------------------------

function getFirstLineSegments(text: string): string[] {
  const firstLine = text.split("\n")[0] ?? "";
  return firstLine.split("|").map((s) => s.trim());
}

export function parseCompany(text: string): string {
  const segments = getFirstLineSegments(text);
  const first = segments[0]?.trim();
  return first && first.length > 0 ? first : "Unknown";
}

export function parseTitle(text: string): string | null {
  const segments = getFirstLineSegments(text);
  if (segments.length < 2) return null;
  const second = segments[1]?.trim();
  return second && second.length > 0 ? second : null;
}

const LOCATION_INDICATORS = [
  "remote",
  "onsite",
  "on-site",
  "on site",
  "hybrid",
  "sf",
  "nyc",
  "london",
  "berlin",
  "paris",
  "tokyo",
  "toronto",
  "vancouver",
  "seattle",
  "austin",
  "boston",
  "chicago",
  "denver",
  "los angeles",
  "la",
  "san francisco",
  "new york",
  "mountain view",
  "palo alto",
  "sunnyvale",
  "cupertino",
  "bangalore",
  "singapore",
  "dublin",
  "amsterdam",
  "munich",
  "zurich",
];

// Two-letter US state abbreviations
const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
  "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
  "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
  "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
  "DC",
];

export function parseLocation(text: string): string | null {
  const segments = getFirstLineSegments(text);

  for (const segment of segments) {
    const lower = segment.toLowerCase();

    // Check location indicator keywords
    if (LOCATION_INDICATORS.some((indicator) => lower.includes(indicator))) {
      return segment;
    }

    // Check for US state abbreviations — look for standalone 2-letter codes
    // (surrounded by word boundaries, commas, or at segment boundaries)
    for (const state of US_STATES) {
      const pattern = new RegExp(`\\b${state}\\b`, "i");
      if (pattern.test(segment)) {
        return segment;
      }
    }
  }

  return null;
}

// ---------------------------------------------------------------------------
// Main scraper
// ---------------------------------------------------------------------------

export interface ScrapeResult {
  threadTitle: string;
  jobsFound: number;
  jobsNew: number;
  jobsUpdated: number;
  jobsFiltered: number;
}

export async function scrapeHN(): Promise<ScrapeResult> {
  // 1. Find the latest hiring thread
  const thread = await findLatestHiringThread();
  if (!thread) {
    throw new Error("Could not find a current 'Who is hiring' thread on HN");
  }

  const now = () => new Date().toISOString();

  // 2. Insert a scrapeRuns record with status "running"
  const [run] = await db
    .insert(scrapeRuns)
    .values({
      source: "hn",
      status: "running",
      startedAt: now(),
    })
    .returning();

  let jobsNew = 0;
  let jobsUpdated = 0;
  let jobsFound = 0;
  let jobsFiltered = 0;

  const MAX_JOBS_TO_SAVE = 40;

  try {
    // 3. Fetch top-level comments (job postings)
    const comments = await fetchThreadComments(thread.storyId);
    jobsFound = comments.length;

    console.log(`\n📥 Found ${jobsFound} job postings from HN`);
    console.log(`⚠️  Will save a maximum of ${MAX_JOBS_TO_SAVE} jobs to database\n`);

    // 4. Process each comment
    for (const comment of comments) {
      // Stop if we've saved enough jobs
      if (jobsNew >= MAX_JOBS_TO_SAVE) {
        console.log(`\n⚠️  Reached maximum of ${MAX_JOBS_TO_SAVE} jobs saved`);
        console.log(`📊 Only ${jobsNew} of ${jobsFound} total jobs were added to database\n`);
        break;
      }
      const commentId = String(comment.id);
      const plainText = stripHtml(comment.text!);
      const company = parseCompany(plainText);
      const title = parseTitle(plainText);
      const location = parseLocation(plainText);
      const url = `https://news.ycombinator.com/item?id=${commentId}`;

      // AI-powered relevance check - skip obviously unrelated jobs
      const relevanceCheck = await isJobRelevant(plainText, title, company);
      if (!relevanceCheck.isRelevant) {
        jobsFiltered++;
        console.log(
          `Filtered out: ${company} - ${title ?? "Unknown"} (${relevanceCheck.reason})`
        );
        continue; // Skip to next job
      }

      // Check if this job already exists
      const existing = await db
        .select()
        .from(jobs)
        .where(and(eq(jobs.source, "hn"), eq(jobs.sourceId, commentId)))
        .limit(1);

      if (existing.length > 0) {
        // Update existing job
        await db
          .update(jobs)
          .set({
            description: plainText,
            updatedAt: now(),
          })
          .where(and(eq(jobs.source, "hn"), eq(jobs.sourceId, commentId)));
        jobsUpdated++;
      } else {
        // Insert new job
        const timestamp = now();
        const newJob: NewJob = {
          source: "hn",
          sourceId: commentId,
          url,
          company,
          title,
          location,
          description: plainText,
          postedAt: comment.created_at,
          discoveredAt: timestamp,
          updatedAt: timestamp,
        };
        await db.insert(jobs).values(newJob);
        jobsNew++;
      }
    }

    // 5. Update scrapeRuns with success
    await db
      .update(scrapeRuns)
      .set({
        status: "completed",
        completedAt: now(),
        jobsFound,
        jobsNew,
        jobsFiltered,
      })
      .where(eq(scrapeRuns.id, run.id));

    // 6. Auto-classify new jobs if any were added
    if (jobsNew > 0) {
      console.log(`\n🤖 Auto-classifying ${jobsNew} new jobs...`);
      try {
        const classifyResult = await classifyJobs({ batchSize: jobsNew, force: false });
        console.log(`✅ Classified ${classifyResult.classified} jobs`);
        console.log(`📊 Tokens used: ${classifyResult.tokensUsed.input} input, ${classifyResult.tokensUsed.output} output`);
      } catch (classifyError) {
        console.error("❌ Auto-classification failed:", classifyError);
        // Don't throw - classification failure shouldn't fail the scrape
      }
    }
  } catch (error) {
    // 6. Update scrapeRuns with failure
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    await db
      .update(scrapeRuns)
      .set({
        status: "failed",
        completedAt: now(),
        error: errorMessage,
        jobsFound,
        jobsNew,
        jobsFiltered,
      })
      .where(eq(scrapeRuns.id, run.id));

    throw error;
  }

  // 7. Return results
  return {
    threadTitle: thread.title,
    jobsFound,
    jobsNew,
    jobsUpdated,
    jobsFiltered,
  };
}
