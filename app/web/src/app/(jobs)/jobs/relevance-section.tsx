"use client";

import { useState } from "react";
import { useDroppable } from "@dnd-kit/core";
import { KanbanCard } from "./kanban-card";
import type { Job } from "./kanban-card";

// ---------------------------------------------------------------------------
// Relevance configuration
// ---------------------------------------------------------------------------
type RelevanceLevel = 0 | 1 | 2 | 3 | 4 | 5;

const RELEVANCE_CONFIG: Record<
  number,
  { label: string; badge: string; badgeColor: string; defaultExpanded: boolean }
> = {
  5: { label: "Strong Match", badge: "5", badgeColor: "bg-emerald-500 text-white", defaultExpanded: true },
  4: { label: "Good Match", badge: "4", badgeColor: "bg-blue-500 text-white", defaultExpanded: true },
  3: { label: "Moderate", badge: "3", badgeColor: "bg-amber-500 text-white", defaultExpanded: false },
  2: { label: "Weak Match", badge: "2", badgeColor: "bg-orange-500 text-white", defaultExpanded: false },
  1: { label: "Poor Match", badge: "1", badgeColor: "bg-red-500 text-white", defaultExpanded: false },
  0: { label: "Unclassified", badge: "?", badgeColor: "bg-zinc-400 text-white", defaultExpanded: false },
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------
export interface RelevanceSectionProps {
  level: RelevanceLevel;
  jobs: Job[];
  onStarToggle: (jobId: number) => void;
  onCardClick: (jobId: number) => void;
  stagePrefix?: string; // e.g., "inbox", "viewed", "stale", "applied"
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function RelevanceSection({
  level,
  jobs,
  onStarToggle,
  onCardClick,
  stagePrefix = "inbox",
}: RelevanceSectionProps) {
  const config = RELEVANCE_CONFIG[level];

  // Auto-expand Unclassified section if it has jobs, otherwise use config default
  const shouldExpandByDefault = level === 0 && jobs.length > 0 ? true : config.defaultExpanded;
  const [expanded, setExpanded] = useState(shouldExpandByDefault);

  const droppableId = `column-${stagePrefix}-${level}`;
  const { setNodeRef, isOver } = useDroppable({ id: droppableId });

  // Always show sections for level 1-5 (empty drop targets are helpful)
  // Only hide level 0 (Unclassified) when empty
  if (jobs.length === 0 && level === 0 && !isOver) return null;

  return (
    <div
      ref={setNodeRef}
      className={`rounded-lg transition-all ${
        isOver ? "ring-2 ring-blue-400 bg-blue-50/50" : ""
      }`}
    >
      {/* Section header */}
      <button
        type="button"
        onClick={() => setExpanded((prev) => !prev)}
        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left transition-colors hover:bg-zinc-200/60"
      >
        <span className="text-[11px] text-zinc-400">
          {expanded ? "\u25BC" : "\u25B6"}
        </span>

        <span className={`inline-flex h-5 w-5 items-center justify-center rounded text-[11px] font-bold ${config.badgeColor}`}>
          {config.badge}
        </span>

        <span className="text-xs font-medium text-zinc-600">
          {config.label}
        </span>

        <span className="ml-auto inline-flex h-4 min-w-[16px] items-center justify-center rounded-full bg-zinc-200 px-1 text-[10px] font-medium text-zinc-500">
          {jobs.length}
        </span>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className={`mt-1 space-y-2 pb-2 pl-1 ${jobs.length === 0 ? "min-h-[60px] rounded border-2 border-dashed border-zinc-300" : ""}`}>
          {jobs.length === 0 ? (
            <div className="flex items-center justify-center py-4 text-xs text-zinc-400">
              Drop here
            </div>
          ) : (
            jobs.map((job) => (
              <KanbanCard
                key={job.id}
                job={job}
                onStarToggle={onStarToggle}
                onClick={onCardClick}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}
