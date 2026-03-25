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
  type: string | null; // 'job' | 'internship' | 'grant'
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
  showLevelBadge?: boolean; // Show level badge for flat lists (Viewed, Stale, Applied)
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function KanbanCard({ job, onStarToggle, onClick, showLevelBadge = false }: KanbanCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id: `job-${job.id}` });

  const style = transform
    ? { transform: CSS.Translate.toString(transform) }
    : undefined;

  const isStarred = job.starred === 1;
  const relevance = job.relevance ?? 0;

  // Level badge configuration
  const levelConfig: Record<number, { badge: string; color: string }> = {
    1: { badge: "1", color: "bg-emerald-500 text-white" },
    2: { badge: "2", color: "bg-blue-500 text-white" },
    3: { badge: "3", color: "bg-amber-500 text-white" },
    0: { badge: "?", color: "bg-zinc-400 text-white" },
  };

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
        {/* Top row: star + level badge (if shown) + company + link */}
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

          {showLevelBadge && (
            <span className={`mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded text-[11px] font-bold ${levelConfig[relevance]?.color ?? levelConfig[0].color}`}>
              {levelConfig[relevance]?.badge ?? "?"}
            </span>
          )}

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

          {/* Link icon */}
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="mt-0.5 shrink-0 p-1 text-zinc-400 hover:text-blue-600 transition-colors"
              aria-label="Open job posting"
              title="Open job posting"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
          )}
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
