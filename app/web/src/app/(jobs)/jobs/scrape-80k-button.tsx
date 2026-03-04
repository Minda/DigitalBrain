"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type ScrapeState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; message: string }
  | { status: "error"; message: string };

export function Scrape80kButton() {
  const [state, setState] = useState<ScrapeState>({ status: "idle" });
  const router = useRouter();

  async function handleScrape() {
    setState({ status: "loading" });

    try {
      const res = await fetch("/api/jobs/scrape-80k", { method: "POST" });
      const data = await res.json();

      if (!res.ok || !data.success) {
        setState({
          status: "error",
          message: data.error ?? "Scrape failed. Check the server logs.",
        });
        return;
      }

      setState({
        status: "success",
        message: `Found ${data.jobsNew} new jobs from 80k Hours`,
      });

      router.refresh();
    } catch (err) {
      setState({
        status: "error",
        message: err instanceof Error ? err.message : "Network error",
      });
    }
  }

  const isLoading = state.status === "loading";

  return (
    <div className="flex flex-col items-end gap-2">
      <button
        onClick={handleScrape}
        disabled={isLoading}
        className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoading ? "Scraping..." : "Scrape 80k Hours"}
      </button>

      {state.status === "success" && (
        <p className="text-xs text-green-600">{state.message}</p>
      )}

      {state.status === "error" && (
        <p className="text-xs text-red-600">{state.message}</p>
      )}
    </div>
  );
}
