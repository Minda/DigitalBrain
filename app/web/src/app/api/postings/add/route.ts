import { NextResponse } from "next/server";
import { spawn } from "child_process";
import { resolve } from "path";

const JOBS_MCP_DIR = resolve(process.cwd(), "../../app/mcp/jobs");

interface AddJobParams {
  url: string;
  company?: string;
  title?: string;
  location?: string;
  description?: string;
}

function runAddJob(params: AddJobParams): Promise<Record<string, unknown>> {
  return new Promise((res, rej) => {
    const args = ["run", "python", "-m", "mcp_jobs.cli", "add", params.url, "--json"];

    if (params.company) {
      args.push("--company", params.company);
    }
    if (params.title) {
      args.push("--title", params.title);
    }
    if (params.location) {
      args.push("--location", params.location);
    }
    if (params.description) {
      args.push("--description", params.description);
    }

    const proc = spawn("uv", args, { cwd: JOBS_MCP_DIR });

    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));
    proc.on("close", (code) => {
      if (code !== 0) return rej(new Error(stderr || `Add job exited with code ${code}`));
      try {
        const data = JSON.parse(stdout);
        if (data.error) return rej(new Error(data.error));
        res(data);
      } catch {
        rej(new Error(`Invalid JSON from add job: ${stdout}`));
      }
    });
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const { url, company, title, location, description } = body as AddJobParams;

    if (!url) {
      return NextResponse.json(
        { success: false, error: "url is required" },
        { status: 400 }
      );
    }

    // If description is provided, require company and title
    if (description && (!company || !title)) {
      return NextResponse.json(
        { success: false, error: "company and title are required when providing description" },
        { status: 400 }
      );
    }

    const result = await runAddJob({ url, company, title, location, description });

    return NextResponse.json({
      success: true,
      jobsNew: result.jobs_new,
      jobsUpdated: result.jobs_updated,
      jobsSkipped: result.jobs_skipped,
    });
  } catch (error) {
    console.error("POST /api/jobs/add failed:", error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
