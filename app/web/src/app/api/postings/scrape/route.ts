import { NextResponse } from "next/server";
import { spawn } from "child_process";
import { resolve } from "path";

const JOBS_MCP_DIR = resolve(process.cwd(), "../../app/mcp/jobs");

function runScraper(source: "hn" | "80k" | "wellfound" | "stanford"): Promise<Record<string, unknown>> {
  return new Promise((res, rej) => {
    const proc = spawn(
      "uv",
      ["run", "python", "-m", "mcp_jobs.cli", "scrape", "--source", source, "--json"],
      { cwd: JOBS_MCP_DIR }
    );

    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));
    proc.on("close", (code) => {
      if (code !== 0) return rej(new Error(stderr || `Scraper exited with code ${code}`));
      try {
        res(JSON.parse(stdout));
      } catch {
        rej(new Error(`Invalid JSON from scraper: ${stdout}`));
      }
    });
  });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const { source } = body as { source?: string };

  if (!source || !["hn", "80k", "wellfound", "stanford"].includes(source)) {
    return NextResponse.json(
      { success: false, error: 'source must be "hn", "80k", "wellfound", or "stanford"' },
      { status: 400 }
    );
  }

  try {
    const result = await runScraper(source as "hn" | "80k" | "wellfound" | "stanford");
    return NextResponse.json({
      success: true,
      jobsNew: result.jobs_new,
      jobsFound: result.jobs_found,
      jobsSkipped: result.jobs_skipped,
      threadTitle: result.thread_title ?? null,
    });
  } catch (error) {
    console.error(`${source} scrape failed:`, error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
