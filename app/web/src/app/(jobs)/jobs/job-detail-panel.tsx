"use client";

import { useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types — local to this client component (no server imports)
// ---------------------------------------------------------------------------
type Stage = "inbox" | "viewed" | "applied" | "dismissed";
type RelevanceLevel = 0 | 1 | 2 | 3;

export interface JobDetailPanelProps {
  job: {
    id: number;
    url: string | null;
    title: string | null;
    company: string;
    location: string | null;
    description: string;
    source: string;
    relevance: number | null;
    starred: number | null;
    stage: string | null;
    score: number | null;
    scoreBreakdown: string | null;
    summary: string | null;
    discoveredAt: string;
    postedAt: string | null;
    salaryMin: number | null;
    salaryMax: number | null;
  };
  onClose: () => void;
  onStageChange: (jobId: number, stage: Stage) => void;
  onStarToggle: (jobId: number) => void;
  onRelevanceChange: (jobId: number, relevance: RelevanceLevel) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
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
  if (days === 1) return "1 day ago";
  return `${days} days ago`;
}

function formatSalary(min: number | null, max: number | null): string | null {
  if (min === null && max === null) return null;

  const fmt = (v: number) => {
    if (v >= 1000) return `$${Math.round(v / 1000)}K`;
    return `$${v}`;
  };

  if (min !== null && max !== null) return `${fmt(min)} - ${fmt(max)}`;
  if (min !== null) return `${fmt(min)}+`;
  return `Up to ${fmt(max!)}`;
}

const STAGES: { value: Stage; label: string }[] = [
  { value: "inbox", label: "Inbox" },
  { value: "viewed", label: "Viewed" },
  { value: "applied", label: "Applied" },
  { value: "dismissed", label: "Dismiss" },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function JobDetailPanel({
  job,
  onClose,
  onStageChange,
  onStarToggle,
  onRelevanceChange,
}: JobDetailPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [breakdownOpen, setBreakdownOpen] = useState(false);

  // Trigger slide-in on mount
  useEffect(() => {
    // requestAnimationFrame ensures the initial translate-x-full is painted first
    requestAnimationFrame(() => setIsOpen(true));
  }, []);

  // Close on Escape key
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const salary = formatSalary(job.salaryMin, job.salaryMax);
  const currentStage = (job.stage ?? "inbox") as Stage;
  const currentRelevance = (job.relevance ?? 0) as RelevanceLevel;
  const isStarred = job.starred === 1;

  return (
    // Backdrop
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Semi-transparent overlay */}
      <div
        className={`absolute inset-0 transition-opacity duration-200 ${
          isOpen ? "bg-black/20" : "bg-black/0"
        }`}
        onClick={onClose}
        aria-label="Close panel"
      />

      {/* Slide-in panel */}
      <div
        ref={panelRef}
        className={`relative flex w-[480px] flex-col border-l border-zinc-200 bg-white shadow-xl transition-transform duration-200 ease-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-3 top-3 z-10 rounded-md p-1.5 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600 transition-colors"
          aria-label="Close"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Header: company + star */}
          <div className="flex items-start gap-3 pr-8">
            <h2 className="text-xl font-bold text-zinc-900 leading-tight">
              {job.company}
            </h2>
            <button
              onClick={() => onStarToggle(job.id)}
              className="shrink-0 mt-0.5 text-xl transition-colors"
              aria-label={isStarred ? "Unstar" : "Star"}
            >
              {isStarred ? (
                <span className="text-amber-400">&#9733;</span>
              ) : (
                <span className="text-zinc-300 hover:text-amber-300">&#9734;</span>
              )}
            </button>
          </div>

          {/* Title */}
          {job.title && (
            <p className="mt-1 text-base text-zinc-600">{job.title}</p>
          )}

          {/* Location */}
          {job.location && (
            <p className="mt-1 text-sm text-zinc-400">{job.location}</p>
          )}

          {/* Salary */}
          {salary && (
            <p className="mt-2 text-sm font-medium text-green-700">{salary}</p>
          )}

          {/* Relevance buttons */}
          <div className="mt-5">
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-zinc-400">
              Relevance
            </p>
            <div className="flex gap-2">
              {([1, 2, 3] as RelevanceLevel[]).map((level) => {
                const labels: Record<number, string> = {
                  1: "Perfect",
                  2: "Good",
                  3: "Distant",
                };
                const activeColors: Record<number, string> = {
                  1: "bg-emerald-500 text-white",
                  2: "bg-blue-500 text-white",
                  3: "bg-amber-500 text-white",
                };
                const isActive = currentRelevance === level;
                return (
                  <button
                    key={level}
                    onClick={() => onRelevanceChange(job.id, level)}
                    className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
                      isActive
                        ? activeColors[level]
                        : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200"
                    }`}
                    aria-label={`Set relevance to ${labels[level]}`}
                  >
                    {labels[level]}
                  </button>
                );
              })}
              {currentRelevance > 0 && (
                <button
                  onClick={() => onRelevanceChange(job.id, 0)}
                  className="ml-1 text-xs text-zinc-400 hover:text-zinc-600 transition-colors"
                  aria-label="Clear relevance"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Stage buttons */}
          <div className="mt-5">
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-zinc-400">
              Stage
            </p>
            <div className="flex gap-2">
              {STAGES.map(({ value, label }) => {
                const isActive = currentStage === value;
                return (
                  <button
                    key={value}
                    onClick={() => onStageChange(job.id, value)}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                      isActive
                        ? value === "dismissed"
                          ? "bg-zinc-700 text-white"
                          : "bg-blue-600 text-white"
                        : value === "dismissed"
                          ? "bg-zinc-100 text-zinc-500 hover:bg-zinc-200"
                          : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200"
                    }`}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Score breakdown (collapsible) */}
          {job.scoreBreakdown && (() => {
            try {
              const bd = JSON.parse(job.scoreBreakdown) as {
                roleMatch?: number;
                techMatch?: number;
                locationFit?: number;
                dealbreakers?: boolean;
                reasoning?: string;
              };
              return (
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={() => setBreakdownOpen((p) => !p)}
                    className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-600 transition-colors"
                  >
                    <span>{breakdownOpen ? "\u25BC" : "\u25B6"}</span>
                    <span>AI Breakdown</span>
                  </button>
                  {breakdownOpen && (
                    <div className="mt-2 rounded-md bg-zinc-50 px-3 py-2.5 text-xs text-zinc-600 space-y-1.5">
                      <div className="flex justify-between">
                        <span>Role match</span>
                        <span className="font-medium">{bd.roleMatch ?? "—"}/3</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tech match</span>
                        <span className="font-medium">{bd.techMatch ?? "—"}/3</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Location fit</span>
                        <span className="font-medium">{bd.locationFit ?? "—"}/3</span>
                      </div>
                      {bd.dealbreakers && (
                        <div className="text-red-600 font-medium">Dealbreaker detected</div>
                      )}
                      {bd.reasoning && (
                        <p className="pt-1 text-zinc-500 italic">{bd.reasoning}</p>
                      )}
                    </div>
                  )}
                </div>
              );
            } catch {
              return null;
            }
          })()}

          {/* Divider */}
          <hr className="my-5 border-zinc-200" />

          {/* LLM Summary (if present) */}
          {job.summary && (
            <div className="mb-4 rounded-md bg-purple-50 px-3 py-2.5 text-sm leading-relaxed text-purple-900">
              {job.summary}
            </div>
          )}

          {/* Full description */}
          <div className="text-sm leading-relaxed text-zinc-700 whitespace-pre-wrap">
            {job.description}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-zinc-200 px-6 py-3 text-xs text-zinc-400">
          <div className="flex items-center gap-2 flex-wrap">
            {job.postedAt && <span>Posted {relativeTime(job.postedAt)}</span>}
            {job.postedAt && <span>&middot;</span>}
            <span>Discovered {relativeTime(job.discoveredAt)}</span>
            {job.url && (
              <>
                <span>&middot;</span>
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-blue-600 hover:underline"
                >
                  View on HN
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
