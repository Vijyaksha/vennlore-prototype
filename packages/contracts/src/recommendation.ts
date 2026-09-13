import { z } from "zod";

export const CONTRACT_VERSION = 1;

/** One engine judgment: anchor talk -> candidate talk. Ids only; the data layer joins Talk fields. */
export const RecommendationSchema = z
  .strictObject({
    for_talk_id: z.int().min(0),
    candidate_id: z.int().min(1),
    score: z.number().min(0).max(1),
    rank: z.int().min(1),
    match: z.boolean(),
    cross_domain: z.boolean(),
    why: z.string(),
    strongest_parallel: z.string(),
    shared_methods: z.array(z.string()),
    evidence: z.record(z.string(), z.unknown()),
    engine_id: z.string().regex(/^[a-z0-9_]+$/),
    run_id: z.string().min(1),
    contract_version: z.literal(CONTRACT_VERSION),
  })
  .meta({ title: "Recommendation" });

export type Recommendation = z.infer<typeof RecommendationSchema>;
