import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/modules/jobs/schema.ts",
  out: "./src/db/migrations",
  dialect: "sqlite",
  dbCredentials: {
    url: "file:../../data/jobs.db",
  },
});
