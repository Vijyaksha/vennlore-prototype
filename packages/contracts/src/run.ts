import { z } from "zod";

import { CONTRACT_VERSION } from "./recommendation.js";

/** Provenance for one index build or one recommend batch. */
export const RunSchema = z
  .strictObject({
    run_id: z.string().min(1),
    engine_id: z.string().regex(/^[a-z0-9_]+$/),
    kind: z.enum(["index", "recommend"]),
    engine_version: z.string(),
    models: z.record(z.string(), z.string()),
    corpus_hash: z.string(),
    anchor_ids: z.array(z.int()),
    started_at: z.iso.datetime(),
    finished_at: z.iso.datetime(),
    index_path: z.string().nullable(),
    contract_version: z.literal(CONTRACT_VERSION),
  })
  .meta({ title: "Run" });

export type Run = z.infer<typeof RunSchema>;
