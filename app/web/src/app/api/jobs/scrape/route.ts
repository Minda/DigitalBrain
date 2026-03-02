import { NextResponse } from "next/server";
import { scrapeHN } from "@/modules/jobs/scrapers/hn";

export async function POST() {
  try {
    const result = await scrapeHN();
    return NextResponse.json({ success: true, ...result });
  } catch (error) {
    console.error("Scrape failed:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
