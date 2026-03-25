"use client";

import { useState, useCallback, useMemo } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
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

type RelevanceLevel = 0 | 1 | 2 | 3;
type PostingType = "job" | "internship" | "grant";

const TYPE_CONFIG: Record<PostingType, { label: string; color: string }> = {
  job: { label: "Jobs", color: "bg-blue-100" },
  internship: { label: "Internships", color: "bg-green-100" },
  grant: { label: "Grants", color: "bg-purple-100" },
};

// ---------------------------------------------------------------------------
// Flat Section Component (for Viewed/Stale/Interested/Applied)
// ---------------------------------------------------------------------------
interface FlatSectionProps {
  droppableId: string;
  label: string;
  jobs: Job[];
  onStarToggle: (jobId: number) => void;
  onCardClick: (jobId: number) => void;
  defaultCollapsed?: boolean;
}

function FlatSection({ droppableId, label, jobs, onStarToggle, onCardClick, defaultCollapsed = false }: FlatSectionProps) {
  const { setNodeRef, isOver } = useDroppable({ id: droppableId });
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  return (
    <div
      ref={setNodeRef}
      className={`rounded-lg p-2 transition-all ${
        isOver ? "ring-2 ring-blue-400 bg-blue-50/50" : "bg-zinc-50"
      }`}
    >
      <div className="mb-2 flex items-center justify-between px-1">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex items-center gap-1 text-xs font-semibold text-zinc-700 hover:text-zinc-900 transition-colors"
        >
          <span className="text-[10px]">{isCollapsed ? "▶" : "▼"}</span>
          <span>{label}</span>
        </button>
        <span className="inline-flex h-4 min-w-[16px] items-center justify-center rounded-full bg-zinc-200 px-1 text-[10px] font-medium text-zinc-500">
          {jobs.length}
        </span>
      </div>
      {!isCollapsed && (
        <div className="space-y-2">
          {jobs.length === 0 ? (
            <div className="flex min-h-[60px] items-center justify-center rounded border-2 border-dashed border-zinc-300 py-4 text-xs text-zinc-400">
              Drop here
            </div>
          ) : (
            jobs.map((job) => (
              <KanbanCard
                key={job.id}
                job={job}
                onStarToggle={onStarToggle}
                onClick={onCardClick}
                showLevelBadge
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}

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

/** Parse a droppable id to determine target type, stage, and relevance.
 *  Examples:
 *    "column-job-inbox-1" → { type: "job", stage: "inbox", relevance: 1 }
 *    "column-internship-viewed" → { type: "internship", stage: "viewed", relevance: null }
 *    "column-grant-stale" → { type: "grant", stage: "inbox", relevance: null } (stale is still inbox stage)
 *    "column-job-interested" → { type: "job", stage: "interested", relevance: null }
 *    "column-job-applied" → { type: "job", stage: "applied", relevance: null }
 */
function parseDroppableId(
  id: string
): { type: string; stage: string; relevance: number | null } | null {
  // Pattern: "column-{type}-{stage}-{level}" (for inbox with levels)
  const matchWithLevel = id.match(/^column-(\w+)-(\w+)-(\d+)$/);
  if (matchWithLevel) {
    const [, type, stage, levelStr] = matchWithLevel;
    const level = parseInt(levelStr, 10);
    const actualStage = stage === "stale" ? "inbox" : stage;
    return { type, stage: actualStage, relevance: isNaN(level) ? null : level };
  }

  // Pattern: "column-{type}-{stage}" (for flat lists: viewed/stale/interested/applied)
  const matchNoLevel = id.match(/^column-(\w+)-(\w+)$/);
  if (matchNoLevel) {
    const [, type, stage] = matchNoLevel;
    const actualStage = stage === "stale" ? "inbox" : stage;
    return { type, stage: actualStage, relevance: null };
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
  // Computed buckets: organized by type → stage → relevance
  // -------------------------------------------------------------------------
  const postingsByType = useMemo(() => {
    const byType: Record<PostingType, {
      inbox: Record<number, Job[]>;
      viewed: Job[];
      stale: Job[];
      interested: Job[];
      applied: Job[];
    }> = {
      job: { inbox: { 1: [], 2: [], 3: [], 0: [] }, viewed: [], stale: [], interested: [], applied: [] },
      internship: { inbox: { 1: [], 2: [], 3: [], 0: [] }, viewed: [], stale: [], interested: [], applied: [] },
      grant: { inbox: { 1: [], 2: [], 3: [], 0: [] }, viewed: [], stale: [], interested: [], applied: [] },
    };

    for (const job of jobs) {
      const type = (job.type ?? "job") as PostingType;
      const stage = job.stage ?? "inbox";
      const rel = (job.relevance ?? 0) as number;
      const bucket = rel >= 0 && rel <= 3 ? rel : 0;

      // Skip dismissed jobs
      if (stage === "dismissed") continue;

      if (stage === "viewed") {
        byType[type].viewed.push(job);
      } else if (stage === "interested") {
        byType[type].interested.push(job);
      } else if (stage === "applied") {
        byType[type].applied.push(job);
      } else {
        // inbox (or any unknown stage treated as inbox)
        if (isStale(job)) {
          byType[type].stale.push(job);
        } else {
          byType[type].inbox[bucket].push(job);
        }
      }
    }

    return byType;
  }, [jobs]);

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
      const patch: { type?: string; stage?: string; relevance?: number } = {};
      if (target.type !== (currentJob.type ?? "job")) {
        patch.type = target.type;
      }
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
        const res = await fetch(`/api/postings/${jobId}`, {
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
  // Star toggle - moves to/from interested stage
  // -------------------------------------------------------------------------
  const handleStarToggle = useCallback(
    async (jobId: number) => {
      const currentJob = jobs.find((j) => j.id === jobId);
      if (!currentJob) return;

      // Toggle between interested and previous stage (or inbox)
      const isInterested = currentJob.stage === "interested";
      const newStage = isInterested ? (currentJob.stage === "applied" ? "viewed" : "inbox") : "interested";
      const newStarred = isInterested ? 0 : 1;

      // Optimistic update
      const now = new Date().toISOString();
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId ? { ...j, starred: newStarred, stage: newStage, updatedAt: now } : j
        )
      );

      try {
        const res = await fetch(`/api/postings/${jobId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ starred: newStarred, stage: newStage }),
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
    async (jobId: number, newStage: "inbox" | "viewed" | "interested" | "applied" | "dismissed") => {
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
        const res = await fetch(`/api/postings/${jobId}`, {
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
    async (jobId: number, newRelevance: 0 | 1 | 2 | 3) => {
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
        const res = await fetch(`/api/postings/${jobId}`, {
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
  // Type change (from detail panel)
  // -------------------------------------------------------------------------
  const handleTypeChange = useCallback(
    async (jobId: number, newType: "job" | "internship" | "grant") => {
      const currentJob = jobs.find((j) => j.id === jobId);
      if (!currentJob) return;
      if ((currentJob.type ?? "job") === newType) return;

      // Optimistic update
      const now = new Date().toISOString();
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId ? { ...j, type: newType, updatedAt: now } : j
        )
      );

      try {
        const res = await fetch(`/api/postings/${jobId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type: newType }),
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
          await fetch(`/api/postings/${jobId}`, {
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
          await fetch("/api/postings/events", {
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

      {/* Board: 3 columns by type (Jobs, Internships, Grants) */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {(["job", "internship", "grant"] as PostingType[]).map((type) => {
          const typeData = postingsByType[type];
          const typeConfig = TYPE_CONFIG[type];

          // Count totals for this type
          const inboxCount = Object.values(typeData.inbox).reduce((sum, arr) => sum + arr.length, 0);
          const totalCount = inboxCount + typeData.viewed.length + typeData.stale.length + typeData.interested.length + typeData.applied.length;

          return (
            <div
              key={type}
              className={`flex min-w-[320px] max-w-[360px] shrink-0 flex-col rounded-xl ${typeConfig.color} p-3`}
            >
              {/* Type column header */}
              <div className="mb-3 flex items-center justify-between px-1">
                <h2 className="text-sm font-semibold text-zinc-800">{typeConfig.label}</h2>
                <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-white/60 px-1.5 text-xs font-medium text-zinc-700">
                  {totalCount}
                </span>
              </div>

              {/* Scrollable container for 4 vertical sections */}
              <div
                className="flex-1 space-y-3 overflow-y-auto pr-0.5"
                style={{ maxHeight: "calc(100vh - 180px)" }}
              >
                {/* ── Inbox section (collapsible levels) ── */}
                <div className="rounded-lg bg-white p-2">
                  <div className="mb-2 flex items-center justify-between px-1">
                    <h3 className="text-xs font-semibold text-zinc-700">Inbox (fresh)</h3>
                    <span className="inline-flex h-4 min-w-[16px] items-center justify-center rounded-full bg-zinc-200 px-1 text-[10px] font-medium text-zinc-500">
                      {inboxCount}
                    </span>
                  </div>
                  <div className="space-y-1">
                    {([1, 2, 3, 0] as RelevanceLevel[]).map((level) => (
                      <RelevanceSection
                        key={level}
                        level={level}
                        jobs={typeData.inbox[level]}
                        onStarToggle={handleStarToggle}
                        onCardClick={handleCardClick}
                        stagePrefix={`${type}-inbox`}
                      />
                    ))}
                  </div>
                </div>

                {/* ── Viewed section (flat list with badges) ── */}
                <FlatSection
                  droppableId={`column-${type}-viewed`}
                  label="Viewed"
                  jobs={typeData.viewed}
                  onStarToggle={handleStarToggle}
                  onCardClick={handleCardClick}
                />

                {/* ── Stale section (flat list with badges) ── */}
                <FlatSection
                  droppableId={`column-${type}-stale`}
                  label="Stale"
                  jobs={typeData.stale}
                  onStarToggle={handleStarToggle}
                  onCardClick={handleCardClick}
                  defaultCollapsed={true}
                />

                {/* ── Interested section (flat list with badges) ── */}
                <FlatSection
                  droppableId={`column-${type}-interested`}
                  label="⭐ Interested"
                  jobs={typeData.interested}
                  onStarToggle={handleStarToggle}
                  onCardClick={handleCardClick}
                />

                {/* ── Applied section (flat list with badges) ── */}
                <FlatSection
                  droppableId={`column-${type}-applied`}
                  label="Applied"
                  jobs={typeData.applied}
                  onStarToggle={handleStarToggle}
                  onCardClick={handleCardClick}
                />
              </div>
            </div>
          );
        })}
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
            onTypeChange={handleTypeChange}
          />
        );
      })()}
    </DndContext>
  );
}
