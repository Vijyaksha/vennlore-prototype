import { z } from "zod";

import {
  CONTRACT_VERSION, RecommendationSchema, RunSchema, TalkSchema,
  type Recommendation, type Run, type Talk,
} from "@repo/contracts";

import type { locations, recommendations, runs, talks } from "./schema";

export type TalkInsert = typeof talks.$inferInsert;
export type RecommendationInsert = typeof recommendations.$inferInsert;
export type RunInsert = typeof runs.$inferInsert;
export type LocationInsert = typeof locations.$inferInsert;

const LocationSchema = z.strictObject({ id: z.int(), building: z.string().min(1), room: z.string().min(1) });

const SeedFileSchema = z.strictObject({
  contract_version: z.literal(CONTRACT_VERSION),
  talks: z.array(TalkSchema),
  locations: z.array(LocationSchema),
  recommendations: z.array(RecommendationSchema),
  runs: z.array(RunSchema),
});
export type SeedFile = z.infer<typeof SeedFileSchema>;

/** Validates the whole seed against the contract; errors name the offending row. */
export function toSeedFile(value: unknown): SeedFile {
  const result = SeedFileSchema.safeParse(value);
  if (!result.success) {
    const issue = result.error.issues[0]!;
    const where = issue.path.map((p, i) => (typeof p === "number" ? `[${p}]` : i ? `.${String(p)}` : String(p))).join("");
    throw new Error(`seed file: ${where || "<root>"}: ${issue.message}`);
  }
  return result.data;
}

const date = (v: string | null) => (v === null ? null : new Date(v));

export function toTalkInsert(t: Talk): TalkInsert {
  return {
    id: t.id, externalId: t.external_id, title: t.title, abstract: t.abstract,
    units: t.units, topics: t.topics, type: t.type, isInvited: t.is_invited,
    isWithdrawn: t.is_withdrawn, start: date(t.start), end: date(t.end),
    sortOrder: t.sort_order, presentationLocation: t.presentation_location,
    authorIds: t.author_ids, presenterIds: t.presenter_ids,
    publicationReference: t.publication_reference,
    fundingAcknowledgement: t.funding_acknowledgement,
    teamAcknowledgement: t.team_acknowledgement, sessionId: t.session_id,
    sessionTitle: t.session_title, sessionCode: t.session_code,
    sessionType: t.session_type, sessionTopics: t.session_topics,
    building: t.building, room: t.room,
  };
}

export function toRecommendationInsert(r: Recommendation): RecommendationInsert {
  return {
    engineId: r.engine_id, forTalkId: r.for_talk_id, candidateId: r.candidate_id,
    score: r.score, rank: r.rank, match: r.match, crossDomain: r.cross_domain,
    why: r.why, strongestParallel: r.strongest_parallel, sharedMethods: r.shared_methods,
    evidence: r.evidence, runId: r.run_id, contractVersion: r.contract_version,
  };
}

export function toRunInsert(m: Run): RunInsert {
  return {
    runId: m.run_id, engineId: m.engine_id, kind: m.kind, engineVersion: m.engine_version,
    models: m.models, corpusHash: m.corpus_hash, anchorIds: m.anchor_ids,
    startedAt: new Date(m.started_at), finishedAt: new Date(m.finished_at),
    indexPath: m.index_path, contractVersion: m.contract_version,
  };
}

export function toLocationInsert(l: z.infer<typeof LocationSchema>): LocationInsert {
  return { id: l.id, building: l.building, room: l.room };
}
