import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { type InferSelectModel, type InferInsertModel } from "drizzle-orm";

// ---------------------------------------------------------------------------
// jobs
// ---------------------------------------------------------------------------
export const jobs = sqliteTable("jobs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  url: text("url").unique(),
  title: text("title"),
  company: text("company").notNull(),
  location: text("location"),
  salaryMin: integer("salary_min"),
  salaryMax: integer("salary_max"),
  description: text("description").notNull(),
  source: text("source").notNull(),
  sourceId: text("source_id"),
  tier: integer("tier").default(0),
  score: real("score"),
  scoreBreakdown: text("score_breakdown"),
  viewed: integer("viewed").default(0),
  tierManuallySet: integer("tier_manually_set").default(0),
  applied: integer("applied").default(0),
  stage: text("stage").default("inbox"),
  relevance: integer("relevance").default(0),
  starred: integer("starred").default(0),
  summary: text("summary"),
  postedAt: text("posted_at"),
  discoveredAt: text("discovered_at").notNull(),
  updatedAt: text("updated_at").notNull(),
});

// ---------------------------------------------------------------------------
// scrape_runs
// ---------------------------------------------------------------------------
export const scrapeRuns = sqliteTable("scrape_runs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  source: text("source").notNull(),
  startedAt: text("started_at").notNull(),
  completedAt: text("completed_at"),
  jobsFound: integer("jobs_found").default(0),
  jobsNew: integer("jobs_new").default(0),
  jobsFiltered: integer("jobs_filtered").default(0),
  status: text("status").default("running"),
  error: text("error"),
});

// ---------------------------------------------------------------------------
// user_actions
// ---------------------------------------------------------------------------
export const userActions = sqliteTable("user_actions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  jobId: integer("job_id")
    .notNull()
    .references(() => jobs.id),
  action: text("action").notNull(),
  oldTier: integer("old_tier"),
  newTier: integer("new_tier"),
  createdAt: text("created_at").notNull(),
});

// ---------------------------------------------------------------------------
// events
// ---------------------------------------------------------------------------
export const events = sqliteTable("events", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  eventType: text("event_type").notNull(),
  jobId: integer("job_id").references(() => jobs.id),
  payload: text("payload"),
  createdAt: text("created_at").notNull(),
});

// ---------------------------------------------------------------------------
// classification_runs
// ---------------------------------------------------------------------------
export const classificationRuns = sqliteTable("classification_runs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  startedAt: text("started_at").notNull(),
  completedAt: text("completed_at"),
  model: text("model").notNull(),
  jobsTotal: integer("jobs_total").default(0),
  jobsClassified: integer("jobs_classified").default(0),
  jobsSkipped: integer("jobs_skipped").default(0),
  inputTokens: integer("input_tokens").default(0),
  outputTokens: integer("output_tokens").default(0),
  status: text("status").default("running"),
  error: text("error"),
});

// ---------------------------------------------------------------------------
// Type helpers
// ---------------------------------------------------------------------------
export type Job = InferSelectModel<typeof jobs>;
export type NewJob = InferInsertModel<typeof jobs>;

export type ScrapeRun = InferSelectModel<typeof scrapeRuns>;
export type NewScrapeRun = InferInsertModel<typeof scrapeRuns>;

export type UserAction = InferSelectModel<typeof userActions>;
export type NewUserAction = InferInsertModel<typeof userActions>;

export type Event = InferSelectModel<typeof events>;
export type NewEvent = InferInsertModel<typeof events>;

export type ClassificationRun = InferSelectModel<typeof classificationRuns>;
export type NewClassificationRun = InferInsertModel<typeof classificationRuns>;
