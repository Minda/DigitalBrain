"use client";

import { useState, useCallback, useMemo } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "./kanban-column";
import { KanbanCard, relativeTime } from "./kanban-card";
import { RelevanceSection } from "./relevance-section";
import { JobDetailPanel } from "./job-detail-panel";
import type { Job } from "./kanban-card";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const STALE_DAYS = 5;

type RelevanceLevel = 0 | 1 | 2 | 3 | 4 | 5;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------
export interface KanbanBoardProps {
  initialJobs: Job[];
  lastScrape: {
    startedAt: string;
    status: string | null;
    jobsNew: number | null;
    jobsFiltered: number | null;
  } | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** True when the job's discoveredAt is older than STALE_DAYS. */
function isStale(job: Job): boolean {
  const cutoff = Date.now() - STALE_DAYS * 24 * 60 * 60 * 1000;
  return new Date(job.discoveredAt).getTime() < cutoff;
}

/** Parse a droppable id to determine target stage and relevance.
 *  Examples:
 *    "column-inbox-5" → { stage: "inbox", relevance: 5 }
 *    "column-viewed-3" → { stage: "viewed", relevance: 3 }
 *    "column-stale-1" → { stage: "inbox", relevance: 1 } (stale is still inbox stage)
 *    "column-applied-4" → { stage: "applied", relevance: 4 }
 */
function parseDroppableId(
  id: string
): { stage: string; relevance: number | null } | null {
  // Pattern: "column-{stage}-{level}"
  const match = id.match(/^column-(\w+)-(\d+)$/);
  if (match) {
    const [, stage, levelStr] = match;
    const level = parseInt(levelStr, 10);

    // Stale is still inbox stage internally
    const actualStage = stage === "stale" ? "inbox" : stage;

    return { stage: actualStage, relevance: isNaN(level) ? null : level };
  }

  return null;
}

/** Extract the numeric job id from a draggable id like "job-42". */
function parseDraggableId(id: string): number | null {
  const match = String(id).match(/^job-(\d+)$/);
  return match ? parseInt(match[1], 10) : null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function KanbanBoard({ initialJobs, lastScrape }: KanbanBoardProps) {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [activeJobId, setActiveJobId] = useState<number | null>(null);

  // Require a small movement before starting a drag to avoid conflicts with click
  const pointerSensor = useSensor(PointerSensor, {
    activationConstraint: { distance: 5 },
  });
  const sensors = useSensors(pointerSensor);

  // -------------------------------------------------------------------------
  // Computed buckets
  // -------------------------------------------------------------------------
  const { inboxByRelevance, viewedByRelevance, staleByRelevance, appliedByRelevance } = useMemo(() => {
    const inbox: Record<number, Job[]> = { 5: [], 4: [], 3: [], 2: [], 1: [], 0: [] };
    const viewed: Record<number, Job[]> = { 5: [], 4: [], 3: [], 2: [], 1: [], 0: [] };
    const stale: Record<number, Job[]> = { 5: [], 4: [], 3: [], 2: [], 1: [], 0: [] };
    const applied: Record<number, Job[]> = { 5: [], 4: [], 3: [], 2: [], 1: [], 0: [] };

    for (const job of jobs) {
      const stage = job.stage ?? "inbox";
      const rel = (job.relevance ?? 0) as number;
      const bucket = rel >= 0 && rel <= 5 ? rel : 0;

      if (stage === "viewed") {
        viewed[bucket].push(job);
      } else if (stage === "applied") {
        applied[bucket].push(job);
      } else if (stage === "dismissed") {
        // Dismissed jobs are not shown on the board
        continue;
      } else {
        // inbox (or any unknown stage treated as inbox)
        if (isStale(job)) {
          stale[bucket].push(job);
        } else {
          inbox[bucket].push(job);
        }
      }
    }

    return {
      inboxByRelevance: inbox,
      viewedByRelevance: viewed,
      staleByRelevance: stale,
      appliedByRelevance: applied,
    };
  }, [jobs]);

  const inboxCount = Object.values(inboxByRelevance).reduce(
    (sum, arr) => sum + arr.length,
    0
  );
  const viewedCount = Object.values(viewedByRelevance).reduce(
    (sum, arr) => sum + arr.length,
    0
  );
  const staleCount = Object.values(staleByRelevance).reduce(
    (sum, arr) => sum + arr.length,
    0
  );
  const appliedCount = Object.values(appliedByRelevance).reduce(
    (sum, arr) => sum + arr.length,
    0
  );

  // -------------------------------------------------------------------------
  // Drag handlers
  // -------------------------------------------------------------------------
  const handleDragStart = useCallback((event: DragStartEvent) => {
    const jobId = parseDraggableId(String(event.active.id));
    setActiveJobId(jobId);
  }, []);

  const handleDragEnd = useCallback(
    async (event: DragEndEvent) => {
      setActiveJobId(null);

      const { active, over } = event;
      if (!over) return;

      const jobId = parseDraggableId(String(active.id));
      if (jobId === null) return;

      const target = parseDroppableId(String(over.id));
      if (!target) return;

      // Find the current job
      const currentJob = jobs.find((j) => j.id === jobId);
      if (!currentJob) return;

      // Build the patch
      const patch: { stage?: string; relevance?: number } = {};
      if (target.stage !== (currentJob.stage ?? "inbox")) {
        patch.stage = target.stage;
      }
      if (target.relevance !== null && target.relevance !== currentJob.relevance) {
        patch.relevance = target.relevance;
      }

      // Nothing changed
      if (Object.keys(patch).length === 0) return;

      // Optimistic update
      const now = new Date().toISOString();
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId
            ? {
                ...j,
                ...patch,
                updatedAt: now,
              }
            : j
        )
      );

      // Persist to server
      try {
        const res = await fetch(`/api/jobs/${jobId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
        });
        if (!res.ok) {
          console.error("Failed to update job", res.status);
          // Revert optimistic update
          setJobs((prev) =>
            prev.map((j) => (j.id === jobId ? currentJob : j))
          );
        }
      } catch (err) {
        console.error("Failed to update job", err);
        // Revert optimistic update
        setJobs((prev) =>
          prev.map((j) => (j.id === jobId ? currentJob : j))
        );
      }
    },
    [jobs]
  );

  // -------------------------------------------------------------------------
  // Star toggle
  // -------------------------------------------------------------------------
  const handleStarToggle = useCallback(
    async (jobId: number) => {
      const currentJob = jobs.find((j) => j.id === jobId);
      if (!currentJob) return;

      const newStarred = currentJob.starred === 1 ? 0 : 1;

      // Optimistic update
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId ? { ...j, starred: newStarred } : j
        )
      );

      try {
        const res = await fetch(`/api/jobs/${jobId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ starred: newStarred }),
        });
        if (!res.ok) {
          // Revert
          setJobs((prev) =>
            prev.map((j) => (j.id === jobId ? currentJob : j))
          );
        }
      } catch {
        // Revert
        setJobs((prev) =>
          prev.map((j) => (j.id === jobId ? currentJob : j))
        );
      }
    },
    [jobs]
  );

  // -------------------------------------------------------------------------
  // Stage change (from detail panel)
  // -------------------------------------------------------------------------
  const handleStageChange = useCallback(
    async (jobId: number, newStage: "inbox" | "viewed" | "applied" | "dismissed") => {
      const currentJob = jobs.find((j) => j.id === jobId);
      if (!currentJob) return;
      if ((currentJob.stage ?? "inbox") === newStage) return;

      // Optimistic update
      const now = new Date().toISOString();
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId ? { ...j, stage: newStage, updatedAt: now } : j
        )
      );

      try {
        const res = await fetch(`/api/jobs/${jobId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stage: newStage }),
        });
        if (!res.ok) {
          setJobs((prev) => prev.map((j) => (j.id === jobId ? currentJob : j)));
        }
      } catch {
        setJobs((prev) => prev.map((j) => (j.id === jobId ? currentJob : j)));
      }

      // Close panel if dismissed
      if (newStage === "dismissed") {
        setSelectedJobId(null);
      }
    },
    [jobs]
  );

  // -------------------------------------------------------------------------
  // Relevance change (from detail panel)
  // -------------------------------------------------------------------------
  const handleRelevanceChange = useCallback(
    async (jobId: number, newRelevance: 0 | 1 | 2 | 3 | 4 | 5) => {
      const currentJob = jobs.find((j) => j.id === jobId);
      if (!currentJob) return;
      if (currentJob.relevance === newRelevance) return;

      // Optimistic update
      const now = new Date().toISOString();
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId ? { ...j, relevance: newRelevance, updatedAt: now } : j
        )
      );

      try {
        const res = await fetch(`/api/jobs/${jobId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ relevance: newRelevance }),
        });
        if (!res.ok) {
          setJobs((prev) => prev.map((j) => (j.id === jobId ? currentJob : j)));
        }
      } catch {
        setJobs((prev) => prev.map((j) => (j.id === jobId ? currentJob : j)));
      }
    },
    [jobs]
  );

  // -------------------------------------------------------------------------
  // Card click — opens detail panel, marks as viewed
  // -------------------------------------------------------------------------
  const handleCardClick = useCallback(
    async (jobId: number) => {
      setSelectedJobId((prev) => (prev === jobId ? null : jobId));

      // Auto-mark as viewed if currently in inbox
      const currentJob = jobs.find((j) => j.id === jobId);
      if (currentJob && (currentJob.stage ?? "inbox") === "inbox") {
        const now = new Date().toISOString();
        setJobs((prev) =>
          prev.map((j) =>
            j.id === jobId ? { ...j, stage: "viewed", updatedAt: now } : j
          )
        );

        try {
          await fetch(`/api/jobs/${jobId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stage: "viewed" }),
          });
        } catch {
          // Revert
          if (currentJob) {
            setJobs((prev) =>
              prev.map((j) => (j.id === jobId ? currentJob : j))
            );
          }
        }

        // Log view event
        try {
          await fetch("/api/jobs/events", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              eventType: "job_viewed",
              jobId,
              payload: {},
            }),
          });
        } catch {
          // Non-critical — don't revert
        }
      }
    },
    [jobs]
  );

  // The job being dragged (for overlay)
  const activeJob = activeJobId
    ? jobs.find((j) => j.id === activeJobId) ?? null
    : null;

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {/* Last scrape status bar */}
      {lastScrape && (
        <div className="mb-4 text-sm text-zinc-500">
          Last scrape: {relativeTime(lastScrape.startedAt)}
          {lastScrape.status === "completed" && lastScrape.jobsNew !== null && (
            <> &middot; {lastScrape.jobsNew} new jobs</>
          )}
          {lastScrape.status === "completed" && lastScrape.jobsFiltered !== null && lastScrape.jobsFiltered > 0 && (
            <> &middot; {lastScrape.jobsFiltered} filtered out</>
          )}
          {lastScrape.status === "running" && (
            <>
              {" "}
              &middot;{" "}
              <span className="text-amber-600">running...</span>
            </>
          )}
          {lastScrape.status === "error" && (
            <>
              {" "}
              &middot; <span className="text-red-600">failed</span>
            </>
          )}
        </div>
      )}

      {/* Board: horizontal scroll container */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {/* ── Inbox (fresh) ── */}
        <div className="flex min-w-[280px] max-w-[320px] shrink-0 flex-col rounded-xl bg-zinc-100 p-3">
          {/* Inbox header */}
          <div className="mb-3 flex items-center justify-between px-1">
            <h2 className="text-sm font-semibold text-zinc-700">
              Inbox (fresh)
            </h2>
            <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-zinc-200 px-1.5 text-xs font-medium text-zinc-600">
              {inboxCount}
            </span>
          </div>

          <div
            className="flex-1 space-y-1 overflow-y-auto pr-0.5"
            style={{ maxHeight: "calc(100vh - 180px)" }}
          >
            {([5, 4, 3, 2, 1, 0] as RelevanceLevel[]).map((level) => (
              <RelevanceSection
                key={level}
                level={level}
                jobs={inboxByRelevance[level]}
                onStarToggle={handleStarToggle}
                onCardClick={handleCardClick}
              />
            ))}
          </div>
        </div>

        {/* ── Viewed ── */}
        <div className="flex min-w-[280px] max-w-[320px] shrink-0 flex-col rounded-xl bg-zinc-100 p-3">
          <div className="mb-3 flex items-center justify-between px-1">
            <h2 className="text-sm font-semibold text-zinc-700">Viewed</h2>
            <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-zinc-200 px-1.5 text-xs font-medium text-zinc-600">
              {viewedCount}
            </span>
          </div>
          <div
            className="flex-1 space-y-1 overflow-y-auto pr-0.5"
            style={{ maxHeight: "calc(100vh - 180px)" }}
          >
            {([5, 4, 3, 2, 1, 0] as RelevanceLevel[]).map((level) => (
              <RelevanceSection
                key={level}
                level={level}
                jobs={viewedByRelevance[level]}
                onStarToggle={handleStarToggle}
                onCardClick={handleCardClick}
                stagePrefix="viewed"
              />
            ))}
          </div>
        </div>

        {/* ── Stale ── */}
        <div className="flex min-w-[280px] max-w-[320px] shrink-0 flex-col rounded-xl bg-zinc-100 p-3">
          <div className="mb-3 flex items-center justify-between px-1">
            <h2 className="text-sm font-semibold text-zinc-700">Stale</h2>
            <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-zinc-200 px-1.5 text-xs font-medium text-zinc-600">
              {staleCount}
            </span>
          </div>
          <div
            className="flex-1 space-y-1 overflow-y-auto pr-0.5"
            style={{ maxHeight: "calc(100vh - 180px)" }}
          >
            {([5, 4, 3, 2, 1, 0] as RelevanceLevel[]).map((level) => (
              <RelevanceSection
                key={level}
                level={level}
                jobs={staleByRelevance[level]}
                onStarToggle={handleStarToggle}
                onCardClick={handleCardClick}
                stagePrefix="stale"
              />
            ))}
          </div>
        </div>

        {/* ── Applied ── */}
        <div className="flex min-w-[280px] max-w-[320px] shrink-0 flex-col rounded-xl bg-zinc-100 p-3">
          <div className="mb-3 flex items-center justify-between px-1">
            <h2 className="text-sm font-semibold text-zinc-700">Applied</h2>
            <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-zinc-200 px-1.5 text-xs font-medium text-zinc-600">
              {appliedCount}
            </span>
          </div>
          <div
            className="flex-1 space-y-1 overflow-y-auto pr-0.5"
            style={{ maxHeight: "calc(100vh - 180px)" }}
          >
            {([5, 4, 3, 2, 1, 0] as RelevanceLevel[]).map((level) => (
              <RelevanceSection
                key={level}
                level={level}
                jobs={appliedByRelevance[level]}
                onStarToggle={handleStarToggle}
                onCardClick={handleCardClick}
                stagePrefix="applied"
              />
            ))}
          </div>
        </div>
      </div>

      {/* Drag overlay — follows the cursor */}
      <DragOverlay>
        {activeJob ? (
          <div className="w-[280px] scale-105 opacity-90 shadow-xl">
            <KanbanCard
              job={activeJob}
              onStarToggle={() => {}}
              onClick={() => {}}
            />
          </div>
        ) : null}
      </DragOverlay>

      {/* Job detail panel */}
      {selectedJobId && (() => {
        const selectedJob = jobs.find((j) => j.id === selectedJobId);
        if (!selectedJob) return null;
        return (
          <JobDetailPanel
            job={selectedJob}
            onClose={() => setSelectedJobId(null)}
            onStageChange={handleStageChange}
            onStarToggle={handleStarToggle}
            onRelevanceChange={handleRelevanceChange}
          />
        );
      })()}
    </DndContext>
  );
}
