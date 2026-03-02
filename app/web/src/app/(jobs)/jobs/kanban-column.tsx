"use client";

import { useDroppable } from "@dnd-kit/core";
import type { ReactNode } from "react";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------
export interface KanbanColumnProps {
  id: string; // droppable id: "column-viewed", "column-stale", "column-applied"
  title: string; // "Viewed", "Stale", "Applied"
  count: number;
  children: ReactNode;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function KanbanColumn({ id, title, count, children }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div
      ref={setNodeRef}
      className={`flex min-w-[280px] max-w-[320px] shrink-0 flex-col rounded-xl bg-zinc-100 p-3 transition-all ${
        isOver ? "ring-2 ring-blue-400" : ""
      }`}
    >
      {/* Header */}
      <div className="mb-3 flex items-center justify-between px-1">
        <h2 className="text-sm font-semibold text-zinc-700">{title}</h2>
        <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-zinc-200 px-1.5 text-xs font-medium text-zinc-600">
          {count}
        </span>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 space-y-2 overflow-y-auto pr-0.5" style={{ maxHeight: "calc(100vh - 180px)" }}>
        {children}
      </div>
    </div>
  );
}
