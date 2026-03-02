import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import path from "path";

const DATA_DIR =
  process.env.DATA_DIR || path.resolve(process.cwd(), "../../data");

const clients = new Map();

export function createModuleDB<TSchema extends Record<string, unknown>>(
  moduleName: string,
  schema: TSchema
) {
  if (clients.has(moduleName)) {
    return clients.get(moduleName);
  }

  const dbPath = path.join(DATA_DIR, `${moduleName}.db`);
  const client = createClient({ url: `file:${dbPath}` });
  const db = drizzle(client, { schema });

  clients.set(moduleName, db);
  return db;
}
