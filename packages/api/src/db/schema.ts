import { sql } from "drizzle-orm";
import {
  bigint,
  boolean,
  doublePrecision,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  text,
  timestamp,
} from "drizzle-orm/pg-core";

const textArray = () =>
  text()
    .array()
    .notNull()
    .default(sql`'{}'::text[]`);
const bigintArray = () =>
  bigint({ mode: "number" })
    .array()
    .notNull()
    .default(sql`'{}'::bigint[]`);

/** One row per Talk contract field, same names. id 0 is the external anchor. */
export const talks = pgTable("talks", {
  id: integer().primaryKey(),
  external_id: text(),
  title: text().notNull(),
  abstract: text().notNull().default(""),
  units: textArray(),
  topics: textArray(),
  type: text(),
  is_invited: boolean().notNull().default(false),
  is_withdrawn: boolean().notNull().default(false),
  start: timestamp({ withTimezone: true }),
  end: timestamp({ withTimezone: true }),
  sort_order: integer(),
  presentation_location: text(),
  author_ids: bigintArray(),
  presenter_ids: bigintArray(),
  publication_reference: text(),
  funding_acknowledgement: text(),
  team_acknowledgement: text(),
  session_id: integer(),
  session_title: text(),
  session_code: text(),
  session_type: text(),
  session_topics: textArray(),
  building: text(),
  room: text(),
});

/** Provenance for one index build or one recommend batch. */
export const runs = pgTable("runs", {
  run_id: text().primaryKey(),
  engine_id: text().notNull(),
  kind: text().notNull(),
  engine_version: text().notNull(),
  models: jsonb().$type<Record<string, string>>().notNull().default({}),
  corpus_hash: text().notNull().default(""),
  anchor_ids: bigintArray(),
  started_at: timestamp({ withTimezone: true }).notNull(),
  finished_at: timestamp({ withTimezone: true }).notNull(),
  index_path: text(),
  contract_version: integer().notNull(),
});

/** One row per Recommendation contract field. Engine-specific detail stays in evidence. */
export const recommendations = pgTable(
  "recommendations",
  {
    engine_id: text().notNull(),
    for_talk_id: integer()
      .notNull()
      .references(() => talks.id),
    candidate_id: integer()
      .notNull()
      .references(() => talks.id),
    score: doublePrecision().notNull(),
    rank: integer().notNull(),
    match: boolean().notNull(),
    cross_domain: boolean().notNull(),
    why: text().notNull().default(""),
    strongest_parallel: text().notNull().default(""),
    shared_methods: textArray(),
    evidence: jsonb()
      .$type<Record<string, unknown>>()
      .notNull()
      .default({}),
    run_id: text()
      .notNull()
      .references(() => runs.run_id),
    contract_version: integer().notNull(),
  },
  (t) => [primaryKey({ columns: [t.engine_id, t.for_talk_id, t.candidate_id] })],
);

// Location ids come from the conference API and exceed int32 (e.g. 4109684556).
export const locations = pgTable("locations", {
  id: bigint({ mode: "number" }).primaryKey(),
  building: text().notNull(),
  room: text().notNull(),
});
