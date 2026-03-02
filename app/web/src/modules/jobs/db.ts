import { createModuleDB } from "@/lib/db";
import * as schema from "./schema";

export const db = createModuleDB("jobs", schema);
