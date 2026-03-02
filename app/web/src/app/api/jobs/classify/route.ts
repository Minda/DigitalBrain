import { NextResponse } from "next/server";
import { classifyJobs } from "@/modules/jobs/classifier";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const { batchSize, force } = body as {
      batchSize?: number;
      force?: boolean;
    };

    // Validate batchSize
    if (batchSize !== undefined) {
      if (!Number.isInteger(batchSize) || batchSize < 1 || batchSize > 200) {
        return NextResponse.json(
          { success: false, error: "batchSize must be an integer from 1 to 200" },
          { status: 400 }
        );
      }
    }

    const result = await classifyJobs({ batchSize, force });

    return NextResponse.json({ success: true, ...result });
  } catch (error) {
    console.error("POST /api/jobs/classify failed:", error);

    const message =
      error instanceof Error ? error.message : "Unknown error";

    return NextResponse.json(
      { success: false, error: message },
      { status: 500 }
    );
  }
}
