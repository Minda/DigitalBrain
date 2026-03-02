import { db } from "@/modules/jobs/db";
import { jobs, scrapeRuns } from "@/modules/jobs/schema";
import type { Job } from "@/modules/jobs/schema";
import { desc, sql, count } from "drizzle-orm";
import Link from "next/link";

function relativeTime(isoDate: string): string {
  const now = Date.now();
  const then = new Date(isoDate).getTime();
  const diffMs = now - then;

  if (diffMs < 0) return "just now";

  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days === 1) return "1d ago";
  return `${days}d ago`;
}

export async function JobsSummary() {
  // Count jobs discovered in the last 24 hours
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

  const [newJobsResult] = await db
    .select({ count: count() })
    .from(jobs)
    .where(sql`${jobs.discoveredAt} >= ${oneDayAgo}`);

  const newJobsCount = newJobsResult?.count ?? 0;

  // Count top-match jobs (relevance = 5)
  const [topMatchResult] = await db
    .select({ count: count() })
    .from(jobs)
    .where(sql`${jobs.relevance} = 5`);

  const topMatchCount = topMatchResult?.count ?? 0;

  // Get last scrape run
  const [lastScrape] = await db
    .select()
    .from(scrapeRuns)
    .orderBy(desc(scrapeRuns.startedAt))
    .limit(1);

  // Get top-match jobs (relevance = 5), or most recent jobs as fallback
  let topJobs = await db
    .select()
    .from(jobs)
    .where(sql`${jobs.relevance} = 5`)
    .orderBy(desc(jobs.discoveredAt))
    .limit(5);

  if (topJobs.length === 0) {
    topJobs = await db
      .select()
      .from(jobs)
      .orderBy(desc(jobs.discoveredAt))
      .limit(5);
  }

  // Check total job count for empty state
  const [totalResult] = await db.select({ count: count() }).from(jobs);
  const totalCount = totalResult?.count ?? 0;

  if (totalCount === 0) {
    return (
      <div className="rounded-lg border border-zinc-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-zinc-900">Job Pipeline</h2>
        <p className="mt-4 text-sm text-zinc-500">
          No jobs yet. Scrape HN from the{" "}
          <Link href="/jobs" className="text-blue-600 hover:underline">
            jobs page
          </Link>
          .
        </p>
      </div>
    );
  }

  const lastScrapeText = lastScrape?.startedAt
    ? `Last scrape ${relativeTime(lastScrape.startedAt)}`
    : "No scrapes yet";

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-zinc-900">Job Pipeline</h2>

      <p className="mt-2 text-sm text-zinc-500">
        {newJobsCount} new today
        {topMatchCount > 0 && <> &middot; {topMatchCount} Top Match</>}
        {" "}&middot; {lastScrapeText}
      </p>

      <ul className="mt-4 space-y-2">
        {topJobs.map((job: Job) => (
          <li key={job.id} className="flex items-start gap-2 text-sm">
            <span className="mt-0.5 text-amber-500">&#9733;</span>
            <span className="flex-1 min-w-0">
              <span className="font-medium text-zinc-900">
                {job.title ?? "Untitled"}
              </span>
              {job.company && (
                <span className="text-zinc-500"> &mdash; {job.company}</span>
              )}
            </span>
            {job.location && (
              <span className="shrink-0 text-zinc-400">{job.location}</span>
            )}
          </li>
        ))}
      </ul>

      <div className="mt-4 text-right">
        <Link
          href="/jobs"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          View all jobs &rarr;
        </Link>
      </div>
    </div>
  );
}
