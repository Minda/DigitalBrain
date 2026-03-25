import { NextResponse } from "next/server";
import { spawn } from "child_process";
import { resolve } from "path";

const JOBS_MCP_DIR = resolve(process.cwd(), "../../app/mcp/jobs");

function runClassifier(batchSize: number, force: boolean): Promise<Record<string, unknown>> {
  return new Promise((res, rej) => {
    const args = ["run", "python", "-m", "mcp_jobs.cli", "classify", "--json", "--batch-size", String(batchSize)];
    if (force) args.push("--force");

    const proc = spawn("uv", args, { cwd: JOBS_MCP_DIR });

    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));
    proc.on("close", (code) => {
      if (code !== 0) return rej(new Error(stderr || `Classifier exited with code ${code}`));
      try {
        const data = JSON.parse(stdout);
        if (data.error) return rej(new Error(data.error));
        res(data);
      } catch {
        rej(new Error(`Invalid JSON from classifier: ${stdout}`));
      }
    });
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const { batchSize = 50, force = false } = body as {
      batchSize?: number;
      force?: boolean;
    };

    if (!Number.isInteger(batchSize) || batchSize < 1 || batchSize > 200) {
      return NextResponse.json(
        { success: false, error: "batchSize must be an integer from 1 to 200" },
        { status: 400 }
      );
    }

    const result = await runClassifier(batchSize, force);

    return NextResponse.json({
      success: true,
      runId: result.run_id,
      classified: result.classified,
      remaining: result.remaining,
      model: result.model,
      tokensUsed: result.tokens_used,
    });
  } catch (error) {
    console.error("POST /api/jobs/classify failed:", error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
