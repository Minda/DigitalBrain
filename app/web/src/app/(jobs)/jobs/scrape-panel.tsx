"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const SOURCES = [
  { id: "hn", label: "HN" },
  { id: "80k", label: "80k Hours" },
] as const;

type Source = (typeof SOURCES)[number]["id"];

export function ScrapePanel() {
  const [selected, setSelected] = useState<Set<Source>>(new Set(["hn", "80k"]));
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const allSelected = selected.size === SOURCES.length;

  function toggleAll() {
    setSelected(allSelected ? new Set() : new Set(SOURCES.map((s) => s.id)));
  }

  function toggle(id: Source) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  async function handleScrape() {
    if (selected.size === 0) return;
    setLoading(true);
    setMessages([]);
    setError(null);

    try {
      const results: string[] = [];
      for (const source of SOURCES.filter((s) => selected.has(s.id))) {
        const res = await fetch("/api/jobs/scrape", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source: source.id }),
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
          setError(data.error ?? `${source.label} scrape failed.`);
          setLoading(false);
          return;
        }
        if (source.id === "hn") {
          results.push(`HN: ${data.jobsNew} new — "${data.threadTitle}"`);
        } else {
          results.push(`80k: ${data.jobsNew} new`);
        }
      }
      setMessages(results);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1.5">
      <div className="flex items-center gap-3">
        {SOURCES.map((s) => (
          <label
            key={s.id}
            className="flex cursor-pointer items-center gap-1.5 text-sm text-zinc-600 select-none"
          >
            <input
              type="checkbox"
              checked={selected.has(s.id)}
              onChange={() => toggle(s.id)}
              disabled={loading}
              className="h-3.5 w-3.5 rounded accent-blue-600"
            />
            {s.label}
          </label>
        ))}
        <button
          onClick={toggleAll}
          disabled={loading}
          className="text-xs text-zinc-400 hover:text-zinc-600 disabled:opacity-40"
        >
          {allSelected ? "none" : "all"}
        </button>
        <button
          onClick={handleScrape}
          disabled={loading || selected.size === 0}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Scraping..." : "Scrape"}
        </button>
      </div>

      {messages.map((m, i) => (
        <p key={i} className="text-xs text-green-600">
          {m}
        </p>
      ))}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
