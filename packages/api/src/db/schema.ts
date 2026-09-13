import { sql } from "drizzle-orm";
import {
  bigint,
  boolean,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  real,
  text,
  timestamp,
} from "drizzle-orm/pg-core";

const textArray = (name: string) =>
  text(name)
    .array()
    .notNull()
    .default(sql`'{}'::text[]`);
const intArray = (name: string) =>
  integer(name)
    .array()
    .notNull()
    .default(sql`'{}'::integer[]`);

/** One row per Talk contract field, same names. id 0 is the external anchor. */
export const talks = pgTable("talks", {
  id: integer("id").primaryKey(),
  externalId: text("external_id"),
  title: text("title").notNull(),
  abstract: text("abstract").notNull().default(""),
  units: textArray("units"),
  topics: textArray("topics"),
  type: text("type"),
  isInvited: boolean("is_invited").notNull().default(false),
  isWithdrawn: boolean("is_withdrawn").notNull().default(false),
  start: timestamp("start", { withTimezone: true }),
  end: timestamp("end", { withTimezone: true }),
  sortOrder: integer("sort_order"),
  presentationLocation: text("presentation_location"),
  authorIds: intArray("author_ids"),
  presenterIds: intArray("presenter_ids"),
  publicationReference: text("publication_reference"),
  fundingAcknowledgement: text("funding_acknowledgement"),
  teamAcknowledgement: text("team_acknowledgement"),
  sessionId: integer("session_id"),
  sessionTitle: text("session_title"),
  sessionCode: text("session_code"),
  sessionType: text("session_type"),
  sessionTopics: textArray("session_topics"),
  building: text("building"),
  room: text("room"),
});

/** Provenance for one index build or one recommend batch. */
export const runs = pgTable("runs", {
  runId: text("run_id").primaryKey(),
  engineId: text("engine_id").notNull(),
  kind: text("kind").notNull(),
  engineVersion: text("engine_version").notNull(),
  models: jsonb("models").$type<Record<string, string>>().notNull().default({}),
  corpusHash: text("corpus_hash").notNull().default(""),
  anchorIds: intArray("anchor_ids"),
  startedAt: timestamp("started_at", { withTimezone: true }).notNull(),
  finishedAt: timestamp("finished_at", { withTimezone: true }).notNull(),
  indexPath: text("index_path"),
  contractVersion: integer("contract_version").notNull(),
});

/** One row per Recommendation contract field. Engine-specific detail stays in evidence. */
export const recommendations = pgTable(
  "recommendations",
  {
    engineId: text("engine_id").notNull(),
    forTalkId: integer("for_talk_id")
      .notNull()
      .references(() => talks.id),
    candidateId: integer("candidate_id")
      .notNull()
      .references(() => talks.id),
    score: real("score").notNull(),
    rank: integer("rank").notNull(),
    match: boolean("match").notNull(),
    crossDomain: boolean("cross_domain").notNull(),
    why: text("why").notNull().default(""),
    strongestParallel: text("strongest_parallel").notNull().default(""),
    sharedMethods: textArray("shared_methods"),
    evidence: jsonb("evidence")
      .$type<Record<string, unknown>>()
      .notNull()
      .default({}),
    runId: text("run_id")
      .notNull()
      .references(() => runs.runId),
    contractVersion: integer("contract_version").notNull(),
  },
  (t) => [primaryKey({ columns: [t.engineId, t.forTalkId, t.candidateId] })],
);

// Location ids come from the conference API and exceed int32 (e.g. 4109684556).
export const locations = pgTable("locations", {
  id: bigint("id", { mode: "number" }).primaryKey(),
  building: text("building").notNull(),
  room: text("room").notNull(),
});
