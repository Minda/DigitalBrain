#!/usr/bin/env tsx

/**
 * Wipe all jobs and related data from the database
 *
 * Usage: npx tsx scripts/wipe-jobs.ts
 */

import { db } from "@/modules/jobs/db";
import { jobs, scrapeRuns, userActions, events, classificationRuns } from "@/modules/jobs/schema";

async function main() {
  console.log("🗑️  Wiping all job data from database...\n");

  // Delete in order to respect foreign key constraints
  console.log("Deleting user actions...");
  await db.delete(userActions);
  console.log("✅ User actions deleted");

  console.log("Deleting events...");
  await db.delete(events);
  console.log("✅ Events deleted");

  console.log("Deleting classification runs...");
  await db.delete(classificationRuns);
  console.log("✅ Classification runs deleted");

  console.log("Deleting scrape runs...");
  await db.delete(scrapeRuns);
  console.log("✅ Scrape runs deleted");

  console.log("Deleting all jobs...");
  await db.delete(jobs);
  console.log("✅ All jobs deleted");

  console.log("\n✨ Database wiped successfully!");
  console.log("\nYou can now run a fresh scrape to populate with new jobs.");
}

main()
  .then(() => {
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Error wiping database:", error);
    process.exit(1);
  });
