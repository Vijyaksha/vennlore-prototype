import { sql } from "drizzle-orm";
import {
  bigint,
  boolean,
  integer,
  pgTable,
  primaryKey,
  text,
  timestamp,
} from "drizzle-orm/pg-core";

export const talks = pgTable("talks", {
  id: integer("id").primaryKey(),
  title: text("title").notNull(),
  sessionTitle: text("session_title"),
  units: text("units")
    .array()
    .notNull()
    .default(sql`'{}'::text[]`),
  start: timestamp("start", { withTimezone: true }),
  end: timestamp("end", { withTimezone: true }),
  building: text("building"),
  room: text("room"),
  abstract: text("abstract").notNull().default(""),
});

export const recommendations = pgTable(
  "recommendations",
  {
    forTalkId: integer("for_talk_id").notNull(),
    candidateId: integer("candidate_id").notNull(),
    sameMethod: integer("same_method").notNull(),
    specificity: integer("specificity").notNull(),
    usageParallel: integer("usage_parallel").notNull(),
    score: integer("score").notNull(),
    match: boolean("is_match").notNull(),
    crossDomain: boolean("cross_domain").notNull(),
    why: text("why").notNull().default(""),
    strongestParallel: text("strongest_parallel").notNull().default(""),
  },
  (t) => [primaryKey({ columns: [t.forTalkId, t.candidateId] })],
);

// Location ids come from the conference API and exceed int32 (e.g. 4109684556).
export const locations = pgTable("locations", {
  id: bigint("id", { mode: "number" }).primaryKey(),
  building: text("building").notNull(),
  room: text("room").notNull(),
});
