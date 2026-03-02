CREATE TABLE `jobs` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`url` text,
	`title` text,
	`company` text NOT NULL,
	`location` text,
	`salary_min` integer,
	`salary_max` integer,
	`description` text NOT NULL,
	`source` text NOT NULL,
	`source_id` text,
	`tier` integer DEFAULT 0,
	`score` real,
	`score_breakdown` text,
	`viewed` integer DEFAULT 0,
	`tier_manually_set` integer DEFAULT 0,
	`applied` integer DEFAULT 0,
	`posted_at` text,
	`discovered_at` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `jobs_url_unique` ON `jobs` (`url`);--> statement-breakpoint
CREATE TABLE `scrape_runs` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`source` text NOT NULL,
	`started_at` text NOT NULL,
	`completed_at` text,
	`jobs_found` integer DEFAULT 0,
	`jobs_new` integer DEFAULT 0,
	`status` text DEFAULT 'running',
	`error` text
);
--> statement-breakpoint
CREATE TABLE `user_actions` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`job_id` integer NOT NULL,
	`action` text NOT NULL,
	`old_tier` integer,
	`new_tier` integer,
	`created_at` text NOT NULL,
	FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON UPDATE no action ON DELETE no action
);
