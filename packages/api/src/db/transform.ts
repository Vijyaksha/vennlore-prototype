import { z } from "zod";

import {
  CONTRACT_VERSION, RecommendationSchema, RunSchema, TalkSchema,
  type Run, type Talk,
} from "@repo/contracts";

import type { runs, talks } from "./schema";

export type TalkInsert = typeof talks.$inferInsert;
export type RunInsert = typeof runs.$inferInsert;

const LocationSchema = z.strictObject({ id: z.int(), building: z.string().min(1), room: z.string().min(1) });

type SeedShape = { talks: { id: number }[]; locations: { id: number }[]; runs: { run_id: string }[];
  recommendations: { for_talk_id: number; candidate_id: number; run_id: string; engine_id: string }[] };

/** Ids must be unique per table and every recommendation must point at a talk and a run in the same seed. */
function checkReferences(seed: SeedShape, ctx: z.RefinementCtx): void {
  const dup = <T>(rows: T[], key: (r: T) => string | number, path: (i: number) => (string | number)[], label: string) => {
    const seen = new Set<string | number>();
    rows.forEach((r, i) => {
      const k = key(r);
      if (seen.has(k)) ctx.addIssue({ code: "custom", path: path(i), message: `duplicate ${label} ${String(k)}` });
      seen.add(k);
    });
  };
  dup(seed.talks, (t) => t.id, (i) => ["talks", i, "id"], "talk id");
  dup(seed.locations, (l) => l.id, (i) => ["locations", i, "id"], "location id");
  dup(seed.runs, (r) => r.run_id, (i) => ["runs", i, "run_id"], "run id");
  dup(seed.recommendations, (r) => `${r.engine_id}/${r.for_talk_id}/${r.candidate_id}`, (i) => ["recommendations", i], "recommendation key");
  const talkIds = new Set(seed.talks.map((t) => t.id));
  const runIds = new Set(seed.runs.map((r) => r.run_id));
  seed.recommendations.forEach((r, i) => {
    if (!talkIds.has(r.for_talk_id)) ctx.addIssue({ code: "custom", path: ["recommendations", i, "for_talk_id"], message: `no talk ${r.for_talk_id} in this seed` });
    if (!talkIds.has(r.candidate_id)) ctx.addIssue({ code: "custom", path: ["recommendations", i, "candidate_id"], message: `no talk ${r.candidate_id} in this seed` });
    if (!runIds.has(r.run_id)) ctx.addIssue({ code: "custom", path: ["recommendations", i, "run_id"], message: `no run ${r.run_id} in this seed` });
  });
}

const SeedFileSchema = z.strictObject({
  contract_version: z.literal(CONTRACT_VERSION),
  talks: z.array(TalkSchema),
  locations: z.array(LocationSchema),
  recommendations: z.array(RecommendationSchema),
  runs: z.array(RunSchema),
}).superRefine(checkReferences);
export type SeedFile = z.infer<typeof SeedFileSchema>;

/** Validates the whole seed against the contract; errors name the offending row. */
export function toSeedFile(value: unknown): SeedFile {
  const result = SeedFileSchema.safeParse(value);
  if (!result.success) {
    const issue = result.error.issues[0]!;
    const where = issue.path.map((p, i) => (typeof p === "number" ? `[${p}]` : i ? `.${String(p)}` : String(p))).join("");
    const rest = result.error.issues.length - 1;
    const more = rest > 0 ? ` (+${rest} more issue${rest > 1 ? "s" : ""})` : "";
    throw new Error(`seed file: ${where || "<root>"}: ${issue.message}${more}`);
  }
  return result.data;
}

const date = (v: string | null) => (v === null ? null : new Date(v));

export function toTalkInsert(t: Talk): TalkInsert {
  return { ...t, start: date(t.start), end: date(t.end) };
}

export function toRunInsert(m: Run): RunInsert {
  return { ...m, started_at: new Date(m.started_at), finished_at: new Date(m.finished_at) };
}
