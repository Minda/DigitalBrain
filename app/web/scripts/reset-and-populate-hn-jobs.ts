#!/usr/bin/env tsx

/**
 * Script to wipe all job entries and repopulate with the 20 most recent HN job postings
 *
 * Usage: tsx scripts/reset-and-populate-hn-jobs.ts
 */

import { db } from "@/modules/jobs/db";
import { jobs, scrapeRuns } from "@/modules/jobs/schema";
import type { NewJob } from "@/modules/jobs/schema";

// ---------------------------------------------------------------------------
// Algolia HN API types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Helper functions from hn.ts
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

function stripHtml(html: string): string {
  let text = html;
  text = text.replace(/<p\s*\/?>/gi, "\n\n");
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(
    /<a\s[^>]*href=["']([^"']*)["'][^>]*>(.*?)<\/a>/gi,
    (_match, href: string, inner: string) => {
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
  text = text.replace(/<[^>]*>/g, "");
  for (const [entity, char] of Object.entries(HTML_ENTITIES)) {
    text = text.replaceAll(entity, char);
  }
  text = text.replace(/&#(\d+);/g, (_match, code: string) =>
    String.fromCharCode(Number(code))
  );
  text = text.replace(/&#x([0-9a-fA-F]+);/g, (_match, code: string) =>
    String.fromCharCode(parseInt(code, 16))
  );
  text = text.replace(/\n{3,}/g, "\n\n");
  return text.trim();
}

function getFirstLineSegments(text: string): string[] {
  const firstLine = text.split("\n")[0] ?? "";
  return firstLine.split("|").map((s) => s.trim());
}

function parseCompany(text: string): string {
  const segments = getFirstLineSegments(text);
  const first = segments[0]?.trim();
  return first && first.length > 0 ? first : "Unknown";
}

function parseTitle(text: string): string | null {
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

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
  "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
  "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
  "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
  "DC",
];

function parseLocation(text: string): string | null {
  const segments = getFirstLineSegments(text);

  for (const segment of segments) {
    const lower = segment.toLowerCase();

    if (LOCATION_INDICATORS.some((indicator) => lower.includes(indicator))) {
      return segment;
    }

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
// Find and fetch HN jobs
// ---------------------------------------------------------------------------

async function findLatestHiringThread(): Promise<{
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

async function fetchThreadComments(
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
// Main script
// ---------------------------------------------------------------------------

async function main() {
  console.log("🗑️  Wiping all existing job entries...");

  // Delete related records first (foreign key constraints)
  await db.delete(scrapeRuns);
  console.log("✅ Scrape runs deleted");

  // Import userActions and events schemas
  const { userActions, events } = await import("@/modules/jobs/schema");
  await db.delete(userActions);
  console.log("✅ User actions deleted");
  await db.delete(events);
  console.log("✅ Events deleted");

  // Delete all jobs
  await db.delete(jobs);
  console.log("✅ All job entries deleted");

  console.log("\n🔍 Finding latest HN hiring thread...");
  const thread = await findLatestHiringThread();
  if (!thread) {
    throw new Error("Could not find a current 'Who is hiring' thread on HN");
  }
  console.log(`✅ Found thread: ${thread.title}`);

  console.log("\n📥 Fetching job postings...");
  const comments = await fetchThreadComments(thread.storyId);
  console.log(`✅ Found ${comments.length} job postings`);

  // Sort by created_at (most recent first) and take the first 20
  const recentComments = comments
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 20);

  console.log(`\n💾 Inserting 20 most recent job postings...`);

  const now = () => new Date().toISOString();
  let inserted = 0;

  for (const comment of recentComments) {
    const commentId = String(comment.id);
    const plainText = stripHtml(comment.text!);
    const company = parseCompany(plainText);
    const title = parseTitle(plainText);
    const location = parseLocation(plainText);
    const url = `https://news.ycombinator.com/item?id=${commentId}`;

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
    inserted++;
    console.log(`  ${inserted}/20 - ${company}`);
  }

  console.log(`\n✅ Successfully inserted ${inserted} job postings`);
  console.log("\n📊 Summary:");
  console.log(`   Thread: ${thread.title}`);
  console.log(`   Total postings found: ${comments.length}`);
  console.log(`   Inserted: ${inserted}`);
}

main()
  .then(() => {
    console.log("\n✨ Done!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Error:", error);
    process.exit(1);
  });
