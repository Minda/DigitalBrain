# Job Pipeline

Scrapes HN "Who is Hiring" threads, stores job listings in SQLite, and displays them in a Kanban board with drag-and-drop triage, relevance ranking, and behavioral event logging. First module in the Exobrain web portal.

## Architecture

```
src/
├── app/
│   ├── page.tsx                          # Portal homepage (imports JobsSummary widget)
│   ├── (jobs)/jobs/
│   │   ├── page.tsx                      # /jobs — server component orchestrator
│   │   ├── kanban-board.tsx              # Main board with DndContext (client)
│   │   ├── kanban-column.tsx             # Droppable column (client)
│   │   ├── kanban-card.tsx               # Draggable job card with star (client)
│   │   ├── relevance-section.tsx         # Collapsible subsection per column (client)
│   │   ├── job-detail-panel.tsx          # Slide-out detail panel (client)
│   │   ├── classify-button.tsx           # "Classify" trigger (client)
│   │   └── scrape-button.tsx             # "Scrape HN" trigger (client)
│   └── api/jobs/
│       ├── scrape/route.ts               # POST /api/jobs/scrape
│       ├── classify/route.ts             # POST /api/jobs/classify
│       ├── [id]/route.ts                 # PATCH /api/jobs/:id
│       └── events/route.ts               # POST /api/jobs/events
├── modules/jobs/
│   ├── schema.ts                         # Drizzle schema (jobs, scrape_runs, events, classification_runs)
│   ├── db.ts                             # Module DB client
│   ├── classifier.ts                     # LLM classification pipeline (Haiku + AI SDK)
│   ├── summary.tsx                       # Dashboard widget for portal homepage
│   └── scrapers/
│       └── hn.ts                         # HN Who's Hiring scraper (Algolia API)
└── lib/
    └── db.ts                             # createModuleDB() factory (shared across modules)
```

Data lives at `data/jobs.db` (project root, gitignored). Each module gets its own SQLite file via the `createModuleDB(moduleName, schema)` factory.

## Database Schema

Five tables in `data/jobs.db`:

### `jobs`

| Column             | Type    | Constraints              | Description                                        |
|--------------------|---------|-------------------------|----------------------------------------------------|
| `id`               | INTEGER | PK, autoincrement       | Internal ID                                        |
| `url`              | TEXT    | UNIQUE                  | Canonical URL — shared key with Simplify.jobs      |
| `title`            | TEXT    |                         | Job title (parsed from first-line pipe convention)  |
| `company`          | TEXT    | NOT NULL                | Company name (first segment of first line)          |
| `location`         | TEXT    |                         | Location/remote status (parsed from pipe segments)  |
| `salary_min`       | INTEGER |                         | Min salary (future use)                             |
| `salary_max`       | INTEGER |                         | Max salary (future use)                             |
| `description`      | TEXT    | NOT NULL                | Full posting text (HTML stripped)                    |
| `source`           | TEXT    | NOT NULL                | Source identifier, e.g. `"hn"`                      |
| `source_id`        | TEXT    |                         | ID within source (HN comment ID)                    |
| `stage`            | TEXT    | DEFAULT `"inbox"`       | Pipeline stage: `inbox`, `viewed`, `applied`, `dismissed` |
| `relevance`        | INTEGER | DEFAULT 0               | 0 = unclassified, 1 = poor → 5 = strong match      |
| `starred`          | INTEGER | DEFAULT 0               | Boolean (0/1) — user-flagged highlight              |
| `summary`          | TEXT    |                         | LLM-generated 2-3 sentence summary                  |
| `score`            | REAL    |                         | Computed relevance score (from classifier)           |
| `score_breakdown`  | TEXT    |                         | JSON breakdown: roleMatch, techMatch, locationFit, dealbreakers, reasoning |
| `tier`             | INTEGER | DEFAULT 0               | *(deprecated)* Superseded by `relevance`            |
| `viewed`           | INTEGER | DEFAULT 0               | *(deprecated)* Superseded by `stage`                |
| `tier_manually_set`| INTEGER | DEFAULT 0               | *(deprecated)* Superseded by events table           |
| `applied`          | INTEGER | DEFAULT 0               | *(deprecated)* Superseded by `stage`                |
| `posted_at`        | TEXT    |                         | ISO timestamp from source                           |
| `discovered_at`    | TEXT    | NOT NULL                | ISO timestamp when first scraped                    |
| `updated_at`       | TEXT    | NOT NULL                | ISO timestamp of last update                        |

**Pipeline stages:** `inbox` → `viewed` → `applied` (or `dismissed`). Jobs also appear in a computed "Stale" column if they've been in inbox >5 days.

**Relevance levels:** 0 = unclassified, 1 = poor match, 2 = weak, 3 = moderate, 4 = good, 5 = strong match. Levels 4–5 are expanded by default in the Kanban Inbox column.

**Dedup key:** `source` + `source_id`. On re-scrape, existing jobs get their `description` and `updated_at` refreshed.

### `scrape_runs`

| Column        | Type    | Constraints        | Description                         |
|---------------|---------|--------------------|-------------------------------------|
| `id`          | INTEGER | PK, autoincrement  | Run ID                              |
| `source`      | TEXT    | NOT NULL           | Which scraper ran (`"hn"`)          |
| `started_at`  | TEXT    | NOT NULL           | ISO timestamp                       |
| `completed_at`| TEXT    |                    | ISO timestamp (null while running)  |
| `jobs_found`  | INTEGER | DEFAULT 0          | Total comments processed            |
| `jobs_new`    | INTEGER | DEFAULT 0          | New jobs inserted                   |
| `status`      | TEXT    | DEFAULT `"running"`| `running` → `completed` or `failed` |
| `error`       | TEXT    |                    | Error message if failed             |

### `events`

| Column       | Type    | Constraints             | Description                                    |
|--------------|---------|-------------------------|------------------------------------------------|
| `id`         | INTEGER | PK, autoincrement       | Event ID                                       |
| `event_type` | TEXT    | NOT NULL                | Event type (see below)                         |
| `job_id`     | INTEGER | FK → jobs.id, nullable  | Which job was acted on                         |
| `payload`    | TEXT    |                         | JSON string with event-specific details        |
| `created_at` | TEXT    | NOT NULL                | ISO timestamp                                  |

**Event types:**

| Event Type             | Trigger                               | Payload                                    |
|------------------------|---------------------------------------|--------------------------------------------|
| `stage_changed`        | Drag between columns or stage button  | `{ "fromStage": "inbox", "toStage": "viewed" }` |
| `relevance_corrected`  | Drag between relevance subsections    | `{ "oldRelevance": 0, "newRelevance": 5 }` |
| `job_viewed`           | Open job detail panel                 | `{}`                                       |
| `job_starred`          | Toggle star                           | `{ "starred": true }`                      |
| `job_dismissed`        | Dismiss from inbox                    | `{}`                                       |

### `classification_runs`

| Column             | Type    | Constraints        | Description                              |
|--------------------|---------|--------------------|------------------------------------------|
| `id`               | INTEGER | PK, autoincrement  | Run ID                                   |
| `started_at`       | TEXT    | NOT NULL           | ISO timestamp                            |
| `completed_at`     | TEXT    |                    | ISO timestamp (null while running)       |
| `model`            | TEXT    | NOT NULL           | Model used, e.g. `"claude-haiku-4-5-20251001"` |
| `jobs_total`       | INTEGER | DEFAULT 0          | Jobs attempted in this run               |
| `jobs_classified`  | INTEGER | DEFAULT 0          | Successfully classified                  |
| `jobs_skipped`     | INTEGER | DEFAULT 0          | Failed / skipped                         |
| `input_tokens`     | INTEGER | DEFAULT 0          | Total input tokens consumed              |
| `output_tokens`    | INTEGER | DEFAULT 0          | Total output tokens consumed             |
| `status`           | TEXT    | DEFAULT `"running"` | `running` → `completed` or `failed`     |
| `error`            | TEXT    |                    | Error message if failed                  |

### `user_actions` *(deprecated)*

Superseded by the `events` table. Remains in the schema but is no longer populated.

## Classification Pipeline

The classifier auto-rates job relevance (1–5) using Claude Haiku with structured output. User corrections feed back as few-shot examples on subsequent runs, creating a self-improving loop.

### How it works

```mermaid
sequenceDiagram
    participant UI as Classify Button
    participant API as POST /api/jobs/classify
    participant Clf as classifier.ts
    participant Haiku as Claude Haiku
    participant DB as jobs.db

    UI->>API: POST { batchSize: 50 }
    API->>Clf: classifyJobs({ batchSize: 50 })

    Clf->>Clf: loadUserProfile() — reads config/job-profile.md
    Clf->>DB: SELECT recent relevance_corrected events (few-shot examples)
    Clf->>DB: SELECT jobs WHERE relevance = 0 LIMIT 50
    Clf->>DB: INSERT classification_runs (status: running)

    loop 10 concurrent per batch
        Clf->>Haiku: generateObject({ profile, job, fewShotExamples })
        Haiku-->>Clf: { summary, relevance, breakdown }
        Clf->>DB: UPDATE jobs SET relevance, score, scoreBreakdown, summary
    end

    Clf->>DB: UPDATE classification_runs (status: completed, token counts)
    Clf-->>API: { runId, classified, remaining, tokensUsed }
    API-->>UI: { success: true, ... }
    UI->>UI: router.refresh() — Kanban re-renders
```

### Components

**User profile** (`config/job-profile.md`): Natural-language description of role preferences, tech interests, location, dealbreakers. Read at classification time. Must be filled in before the first run.

**Structured output** (Zod schema): Each job produces `{ summary, relevance (1-5), breakdown: { roleMatch, techMatch, locationFit, dealbreakers, reasoning } }` via `generateObject()`.

**Few-shot calibration**: Queries the 10 most recent `relevance_corrected` events from the events table, joins with jobs to build calibration examples in the prompt. User corrections from the Kanban board directly improve future classification accuracy.

**Concurrency**: 10 parallel LLM calls per batch, up to 50 jobs per API request. ~$0.002/job with Haiku.

### Self-improving loop

```
User clicks "Classify" → jobs auto-rated → user corrects misclassifications via Kanban drag
  → relevance_corrected events logged → next classify run includes corrections as few-shot examples
  → classification accuracy improves over time
```

## Scrapers

All scrapers live in `modules/jobs/scrapers/`. Each exports an async function that fetches jobs from one source, parses them into the shared `jobs` schema, and tracks the run in `scrape_runs`.

```mermaid
graph LR
    subgraph Sources
        HN["HN Who's Hiring"]
        S2["80K Hours (Phase 3)"]
        S3["Wellfound (Phase 3)"]
        S4["WTTJ (Phase 4)"]
    end

    subgraph "scrapers/"
        HNS["hn.ts"]
        S2S["80k.ts"]
        S3S["wellfound.ts"]
        S4S["wttj.ts"]
    end

    subgraph Pipeline
        Parse["Parse + strip HTML"]
        Dedup["Dedup (source + source_id)"]
        Store["Insert / update jobs table"]
        Track["Update scrape_runs"]
    end

    HN --> HNS
    S2 --> S2S
    S3 --> S3S
    S4 --> S4S

    HNS --> Parse
    S2S --> Parse
    S3S --> Parse
    S4S --> Parse

    Parse --> Dedup --> Store --> Track

    style HNS fill:#d1fae5,stroke:#059669
    style S2S fill:#f3f4f6,stroke:#9ca3af,stroke-dasharray: 5 5
    style S3S fill:#f3f4f6,stroke:#9ca3af,stroke-dasharray: 5 5
    style S4S fill:#f3f4f6,stroke:#9ca3af,stroke-dasharray: 5 5
```

### HN Scraper (`hn.ts`) — implemented

Uses the **Algolia HN API** (no browser automation, no auth required). Two API calls per scrape:

```mermaid
sequenceDiagram
    participant Client
    participant API as POST /api/jobs/scrape
    participant Scraper as hn.ts
    participant Algolia as hn.algolia.com
    participant DB as jobs.db

    Client->>API: POST /api/jobs/scrape
    API->>Scraper: scrapeHN()
    Scraper->>DB: INSERT scrape_runs (status: running)

    Scraper->>Algolia: GET /api/v1/search?query="Ask HN: Who is hiring"
    Algolia-->>Scraper: Search results (5 stories)
    Note over Scraper: Filter: includes "who is hiring",<br/>excludes "who wants to be hired"<br/>and "freelancer"

    Scraper->>Algolia: GET /api/v1/items/{storyId}
    Algolia-->>Scraper: Full comment tree (~400-500 comments)
    Note over Scraper: Keep only top-level children<br/>where type=comment and text≠null

    loop Each comment
        Note over Scraper: stripHtml → parseCompany<br/>→ parseTitle → parseLocation
        Scraper->>DB: SELECT WHERE source=hn AND source_id=commentId
        alt New job
            Scraper->>DB: INSERT into jobs
        else Existing job
            Scraper->>DB: UPDATE description + updated_at
        end
    end

    Scraper->>DB: UPDATE scrape_runs (status: completed)
    Scraper-->>API: { threadTitle, jobsFound, jobsNew, jobsUpdated }
    API-->>Client: { success: true, ... }
```

#### Step-by-step

1. **Find the latest thread** — `findLatestHiringThread()`
   - Searches Algolia for `"Ask HN: Who is hiring"` stories (top 5 results)
   - Filters to match titles containing "who is hiring" but NOT "who wants to be hired" or "freelancer"
   - Returns the `objectID` (HN story ID) and title

2. **Track the run** — inserts a `scrape_runs` row with `status: "running"` before any work begins. Updated to `"completed"` or `"failed"` at the end.

3. **Fetch all comments** — `fetchThreadComments(storyId)`
   - Calls `GET https://hn.algolia.com/api/v1/items/{storyId}`
   - Returns the full comment tree as nested JSON (~3MB for a typical thread)
   - Filters to top-level children only (these are the actual job postings)
   - Discards replies, deleted comments, and comments with null text

4. **Parse each comment** into structured fields:

   **HTML stripping** (`stripHtml`):
   - `<p>` → double newline, `<br>` → single newline
   - `<a href="url">text</a>` → keeps the URL (if link text matches the URL, just shows URL; otherwise shows `text (url)`)
   - Strips all remaining tags
   - Decodes named entities (`&amp;`, `&lt;`, `&nbsp;`, etc.) and numeric entities (`&#123;`, `&#x7B;`)
   - Collapses 3+ consecutive newlines into 2

   **Field extraction** from the pipe convention (`Company | Title | Location | ...`):
   - `parseCompany` — first pipe-separated segment of the first line, falls back to `"Unknown"`
   - `parseTitle` — second segment if it exists
   - `parseLocation` — scans all segments for location indicators:
     - Keywords: remote, onsite, hybrid, and ~25 major city names
     - US state abbreviations: all 50 states + DC, matched as standalone word boundaries
     - Returns the full segment text (e.g. `"Remote (US/EU timezones)"`)

5. **Dedup + upsert** — checks `source` + `source_id` for each comment:
   - **New**: inserts full job record with all parsed fields
   - **Existing**: updates only `description` and `updated_at` (re-parsed text may differ if the poster edited their comment)

6. **Finalize run** — updates the `scrape_runs` row with final counts and status

#### Typical numbers

- ~400-500 top-level comments per monthly thread
- First scrape: ~480 new jobs
- Re-scrape same thread: 0 new, ~480 updated
- Single API response ~3MB, total runtime 5-15 seconds

### Adding a new scraper

Create `modules/jobs/scrapers/{source}.ts` following this pattern:

```typescript
import { db } from "@/modules/jobs/db";
import { jobs, scrapeRuns } from "@/modules/jobs/schema";
import type { NewJob } from "@/modules/jobs/schema";
import { eq, and } from "drizzle-orm";

export async function scrapeMySource(): Promise<ScrapeResult> {
  const now = () => new Date().toISOString();

  // 1. Insert scrape_runs record
  const [run] = await db
    .insert(scrapeRuns)
    .values({ source: "my-source", status: "running", startedAt: now() })
    .returning();

  try {
    // 2. Fetch listings from the source API / page
    const listings = await fetchListings();

    // 3. For each listing: parse, dedup, insert/update
    for (const listing of listings) {
      const existing = await db
        .select().from(jobs)
        .where(and(eq(jobs.source, "my-source"), eq(jobs.sourceId, listing.id)))
        .limit(1);

      if (existing.length > 0) {
        await db.update(jobs)
          .set({ description: listing.text, updatedAt: now() })
          .where(and(eq(jobs.source, "my-source"), eq(jobs.sourceId, listing.id)));
      } else {
        const ts = now();
        await db.insert(jobs).values({
          source: "my-source",
          sourceId: listing.id,
          url: listing.url,
          company: listing.company,
          title: listing.title,
          location: listing.location,
          description: listing.text,
          postedAt: listing.postedAt,
          discoveredAt: ts,
          updatedAt: ts,
        });
      }
    }

    // 4. Update scrape_runs with success
    await db.update(scrapeRuns)
      .set({ status: "completed", completedAt: now(), jobsFound: listings.length, jobsNew: newCount })
      .where(eq(scrapeRuns.id, run.id));
  } catch (error) {
    // 5. Update scrape_runs with failure
    await db.update(scrapeRuns)
      .set({ status: "failed", completedAt: now(), error: String(error) })
      .where(eq(scrapeRuns.id, run.id));
    throw error;
  }
}
```

Then add an API route at `app/api/jobs/scrape-{source}/route.ts` and a button in the UI.

### Planned scrapers (future phases)

| Source | Phase | Method | Notes |
|--------|-------|--------|-------|
| HN Who's Hiring | 1 (done) | Algolia API | Monthly threads, ~500 jobs each |
| 80,000 Hours | 3 | API/scrape | EA/longtermist job board |
| Wellfound | 3 | API | Startup jobs (formerly AngelList) |
| Meta/Google careers | 3 | Scrape | Large company career pages |
| Welcome to the Jungle | 4 | Scrape | European tech jobs |

## API

### `POST /api/jobs/scrape`

Triggers a full HN scrape. Returns:

```json
{
  "success": true,
  "threadTitle": "Ask HN: Who is hiring? (February 2026)",
  "jobsFound": 480,
  "jobsNew": 480,
  "jobsUpdated": 0
}
```

Or on error:

```json
{
  "success": false,
  "error": "Could not find a current 'Who is hiring' thread on HN"
}
```

### `PATCH /api/jobs/:id`

Update a job's stage, relevance, or starred status. Automatically logs events for each change.

```json
// Request (all fields optional)
{ "stage": "viewed", "relevance": 5, "starred": 1 }

// Response
{ "success": true, "job": { ... } }
```

Validations: `stage` must be `inbox | viewed | applied | dismissed`, `relevance` must be 0–5, `starred` must be 0 or 1.

### `POST /api/jobs/classify`

Triggers LLM classification of unclassified jobs. Requires `config/job-profile.md` to exist with real preferences (not template placeholders).

```json
// Request (all fields optional)
{ "batchSize": 50, "force": false }

// Success
{
  "success": true,
  "runId": 3,
  "classified": 50,
  "remaining": 430,
  "model": "claude-haiku-4-5-20251001",
  "tokensUsed": { "input": 48000, "output": 9500 }
}

// Error (missing profile)
{ "success": false, "error": "Job profile not found at ..." }
```

`batchSize` (1–200, default 50): how many jobs to classify per request. `force` (default false): re-classify jobs that already have a relevance score.

### `POST /api/jobs/events`

Log a user interaction event.

```json
// Request
{ "eventType": "job_viewed", "jobId": 42, "payload": { "timeSpentSeconds": 12 } }

// Response
{ "success": true, "eventId": 7 }
```

## UI

### Portal Homepage (`/`)

The `JobsSummary` widget shows at a glance:
- Stats: new jobs today, Top Match (relevance 5) count, last scrape time
- Top 5 relevance-5 jobs (or most recent if none ranked yet)
- "View all jobs →" link

### Kanban Board (`/jobs`)

Four-column drag-and-drop board for triaging jobs:

```
┌────────────────┬───────────────┬───────────────┬─────────────────────┐
│     INBOX      │    VIEWED     │     STALE     │      APPLIED        │
│    (12 new)    │     (5)       │     (23)      │       (2)           │
│                │               │               │                     │
│ ★★★★★ Strong  │ ┌───────────┐ │ ┌───────────┐ │ ┌───────────────┐   │
│   Match (2) ▼  │ │ Job card  │ │ │ Job card  │ │ │ Job card      │   │
│ ┌────────────┐ │ └───────────┘ │ └───────────┘ │ └───────────────┘   │
│ │ ★ Company  │ │ ┌───────────┐ │ ┌───────────┐ │                     │
│ │   Title    │ │ │ Job card  │ │ │ Job card  │ │                     │
│ │   Location │ │ └───────────┘ │ └───────────┘ │                     │
│ └────────────┘ │               │               │                     │
│                │               │               │                     │
│ ★★★★☆ Good    │               │               │                     │
│   Match (5) ▼  │               │               │                     │
│ ┌────────────┐ │               │               │                     │
│ │  ...       │ │               │               │                     │
│ └────────────┘ │               │               │                     │
│                │               │               │                     │
│ ★★★☆☆ (8) ▸  │               │               │                     │
│ ★★☆☆☆ (4) ▸  │               │               │                     │
│ ★☆☆☆☆ (2) ▸  │               │               │                     │
│ Unclassified   │               │               │                     │
│   (430) ▸     │               │               │                     │
└────────────────┴───────────────┴───────────────┴─────────────────────┘
```

**Inbox column:** Subsectioned by relevance level (5 at top → 0 at bottom). Levels 4–5 expanded by default, 1–3 and 0 collapsed. Count badge per subsection. Drag between subsections to change relevance.

**Viewed column:** Flat list, ordered by when viewed (most recent first).

**Stale column:** Computed — inbox jobs where `discoveredAt` > 5 days ago. Not stored as a stage; these are removed from the Inbox column and shown here instead. Users can drag from Stale to any other column.

**Applied column:** Flat list, ordered by when applied.

**Drag-and-drop:** Powered by @dnd-kit. Dragging between columns changes `stage`. Dragging within Inbox between relevance subsections changes `relevance`. All changes are optimistic with rollback on API failure.

### Job Card

Compact card with drag handle, star toggle, company/title/location, 2-line description clamp, and relative timestamp. Click opens the detail panel.

### Job Detail Panel

Slide-out panel from the right (480px wide). Shows full job description, metadata, clickable relevance stars (1–5), stage buttons (Inbox/Viewed/Applied/Dismiss), star toggle, and source link. Opening the panel auto-transitions inbox jobs to `viewed` stage and logs a `job_viewed` event.

**AI Summary**: If the job has been classified, a purple summary box (`bg-purple-50`) appears above the full description with the LLM-generated 2–3 sentence summary.

**AI Breakdown**: Below the relevance stars, a collapsible "AI Breakdown" section shows the classification components: role match (1–5), tech match (1–5), location fit (1–5), dealbreaker flag, and the LLM's reasoning. Collapsed by default, click to expand. Only appears after classification.

### Classify Button

Purple button in the page header next to "Scrape HN". Same state machine pattern as `ScrapeButton`:

- **Idle**: "Classify"
- **Loading**: "Classifying..." (disabled)
- **Success**: "Classified 50 jobs (430 remaining)"
- **Error**: Red error message

Calls `POST /api/jobs/classify` with `batchSize: 50`, then `router.refresh()` to re-render the Kanban board with updated relevance sections.

## Future Phases

- **Phase 1** (done): Scaffold, HN scraper, basic job list, portal homepage
- **Phase 2** (done): Kanban board (4 columns), drag-and-drop, star/highlight, event logging, job detail panel, relevance 1–5 scale
- **Phase 3** (in progress): LLM classification pipeline (done), user profile (done), few-shot calibration (done). Remaining: more scrapers, email digest
- **Phase 4**: Embeddings, classifier training, pairwise ranking
- **Phase 5**: AI-assisted applications

## Module Pattern

This follows the multi-module pattern for the Exobrain web portal. To add a new module (e.g. Recipes):

```
src/modules/recipes/schema.ts       # Drizzle schema
src/modules/recipes/db.ts           # createModuleDB("recipes", schema)
src/modules/recipes/summary.tsx     # Dashboard widget
src/app/(recipes)/recipes/page.tsx  # Full page
src/app/api/recipes/                # API routes
data/recipes.db                     # Separate SQLite file
```
