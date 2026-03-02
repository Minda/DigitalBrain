CREATE TABLE `classification_runs` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`started_at` text NOT NULL,
	`completed_at` text,
	`model` text NOT NULL,
	`jobs_total` integer DEFAULT 0,
	`jobs_classified` integer DEFAULT 0,
	`jobs_skipped` integer DEFAULT 0,
	`input_tokens` integer DEFAULT 0,
	`output_tokens` integer DEFAULT 0,
	`status` text DEFAULT 'running',
	`error` text
);
--> statement-breakpoint
CREATE TABLE `events` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`event_type` text NOT NULL,
	`job_id` integer,
	`payload` text,
	`created_at` text NOT NULL,
	FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
ALTER TABLE `jobs` ADD `stage` text DEFAULT 'inbox';--> statement-breakpoint
ALTER TABLE `jobs` ADD `relevance` integer DEFAULT 0;--> statement-breakpoint
ALTER TABLE `jobs` ADD `starred` integer DEFAULT 0;--> statement-breakpoint
ALTER TABLE `jobs` ADD `summary` text;--> statement-breakpoint
ALTER TABLE `scrape_runs` ADD `jobs_filtered` integer DEFAULT 0;