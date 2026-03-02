"use client";

import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";

// ---------------------------------------------------------------------------
// Types (client-side mirror of the Drizzle schema — cannot import server code)
// ---------------------------------------------------------------------------
export interface Job {
  id: number;
  url: string | null;
  title: string | null;
  company: string;
  location: string | null;
  description: string;
  source: string;
  sourceId: string | null;
  stage: string | null;
  relevance: number | null;
  starred: number | null;
  tier: number | null;
  score: number | null;
  discoveredAt: string;
  updatedAt: string;
  postedAt: string | null;
  salaryMin: number | null;
  salaryMax: number | null;
  scoreBreakdown: string | null;
  summary: string | null;
  viewed: number | null;
  applied: number | null;
  tierManuallySet: number | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
export function relativeTime(isoDate: string): string {
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

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------
export interface KanbanCardProps {
  job: Job;
  onStarToggle: (jobId: number) => void;
  onClick: (jobId: number) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function KanbanCard({ job, onStarToggle, onClick }: KanbanCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id: `job-${job.id}` });

  const style = transform
    ? { transform: CSS.Translate.toString(transform) }
    : undefined;

  const isStarred = job.starred === 1;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`group relative rounded-lg border bg-white p-3 transition-shadow select-none ${
        isDragging
          ? "border-blue-300 opacity-50 shadow-lg"
          : "border-zinc-200 shadow-sm hover:shadow-md"
      }`}
    >
      {/* Drag handle — visible on hover */}
      <div
        {...listeners}
        {...attributes}
        className="absolute left-0 top-0 flex h-full w-5 cursor-grab items-center justify-center rounded-l-lg text-zinc-300 opacity-0 transition-opacity hover:text-zinc-400 group-hover:opacity-100 active:cursor-grabbing"
        aria-label="Drag handle"
      >
        <svg
          width="6"
          height="20"
          viewBox="0 0 6 20"
          fill="currentColor"
          className="pointer-events-none"
        >
          <circle cx="1.5" cy="2" r="1.2" />
          <circle cx="4.5" cy="2" r="1.2" />
          <circle cx="1.5" cy="7" r="1.2" />
          <circle cx="4.5" cy="7" r="1.2" />
          <circle cx="1.5" cy="12" r="1.2" />
          <circle cx="4.5" cy="12" r="1.2" />
          <circle cx="1.5" cy="17" r="1.2" />
          <circle cx="4.5" cy="17" r="1.2" />
        </svg>
      </div>

      {/* Clickable area */}
      <div
        className="cursor-pointer pl-4"
        onClick={() => onClick(job.id)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onClick(job.id);
          }
        }}
      >
        {/* Top row: star + company */}
        <div className="flex items-start gap-2">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onStarToggle(job.id);
            }}
            className={`mt-0.5 shrink-0 text-base leading-none transition-colors ${
              isStarred
                ? "text-amber-400 hover:text-amber-500"
                : "text-zinc-300 hover:text-amber-400"
            }`}
            aria-label={isStarred ? "Unstar job" : "Star job"}
          >
            {isStarred ? "\u2605" : "\u2606"}
          </button>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-zinc-900">
              {job.company}
            </p>
            {job.title && (
              <p className="truncate text-xs text-zinc-500">{job.title}</p>
            )}
            {job.location && (
              <p className="truncate text-[11px] text-zinc-400">
                {job.location}
              </p>
            )}
          </div>
        </div>

        {/* Description snippet */}
        {job.description && (
          <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-zinc-500">
            {job.description}
          </p>
        )}

        {/* Footer: relative time */}
        <div className="mt-1.5 flex items-center justify-end">
          <span className="text-[11px] text-zinc-400">
            {relativeTime(job.discoveredAt)}
          </span>
        </div>
      </div>
    </div>
  );
}
