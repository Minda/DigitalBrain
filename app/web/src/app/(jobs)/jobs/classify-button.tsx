"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type ClassifyState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; classified: number; remaining: number }
  | { status: "error"; message: string };

export function ClassifyButton() {
  const [state, setState] = useState<ClassifyState>({ status: "idle" });
  const router = useRouter();

  async function handleClassify() {
    setState({ status: "loading" });

    try {
      const res = await fetch("/api/jobs/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batchSize: 50 }),
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        setState({
          status: "error",
          message: data.error ?? "Classification failed.",
        });
        return;
      }

      setState({
        status: "success",
        classified: data.classified,
        remaining: data.remaining,
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
        onClick={handleClassify}
        disabled={isLoading}
        className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoading ? "Classifying..." : "Classify"}
      </button>

      {state.status === "success" && (
        <p className="text-xs text-green-600">
          Classified {state.classified} jobs
          {state.remaining > 0 && ` (${state.remaining} remaining)`}
        </p>
      )}

      {state.status === "error" && (
        <p className="max-w-[240px] text-xs text-red-600">{state.message}</p>
      )}
    </div>
  );
}
