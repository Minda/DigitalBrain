import { db } from "@/modules/jobs/db";
import { jobs, scrapeRuns } from "@/modules/jobs/schema";
import { desc } from "drizzle-orm";
import Link from "next/link";
import { ScrapePanel } from "./scrape-panel";
import { ClassifyButton } from "./classify-button";
import { KanbanBoard } from "./kanban-board";

export const dynamic = "force-dynamic";

export default async function JobsPage() {
  // Fetch all jobs (Kanban needs them all for proper grouping)
  const allJobs = await db
    .select()
    .from(jobs)
    .orderBy(desc(jobs.discoveredAt))
    .limit(500);

  const [lastScrape] = await db
    .select()
    .from(scrapeRuns)
    .orderBy(desc(scrapeRuns.startedAt))
    .limit(1);

  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="mx-auto max-w-full px-4 py-6">
        {/* Header row */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-sm text-zinc-400 hover:text-zinc-600">
              &larr; Portal
            </Link>
            <h1 className="text-xl font-bold tracking-tight text-zinc-900">
              Job Pipeline
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <ClassifyButton />
            <ScrapePanel />
          </div>
        </div>

        {/* Kanban board */}
        <KanbanBoard
          initialJobs={allJobs}
          lastScrape={lastScrape ?? null}
        />
      </div>
    </div>
  );
}
