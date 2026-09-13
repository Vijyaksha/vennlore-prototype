import { z } from "zod";
import { RecommendationSchema } from "./recommendation";
import { RunSchema } from "./run";
import { TalkSchema } from "./talk";

export const SCHEMAS = { talk: TalkSchema, recommendation: RecommendationSchema, run: RunSchema } as const;
export type SchemaKind = keyof typeof SCHEMAS;

/** JSON Schema (draft 2020-12) for every contract kind, keyed by kind. */
export function emitAll(): Record<SchemaKind, Record<string, unknown>> {
  const opts = { target: "draft-2020-12" as const };
  return Object.fromEntries(
    Object.entries(SCHEMAS).map(([kind, schema]) => [kind, z.toJSONSchema(schema, opts)]),
  ) as unknown as Record<SchemaKind, Record<string, unknown>>;
}
