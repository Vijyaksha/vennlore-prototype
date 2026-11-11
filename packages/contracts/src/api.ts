import { z } from "zod";

import { RecommendationSchema } from "./recommendation";
import { TalkSchema } from "./talk";

/** Engine ids follow the row rule; the API also caps the length a client may send. */
export const EngineIdSchema = RecommendationSchema.shape.engine_id.max(64);

/** Who the picks are for: a presenter (every talk they present is an anchor) or one talk.
 *  Strict on both branches so a request naming both is rejected, not silently resolved. */
export const SubjectSchema = z
  .union([
    z.strictObject({ presenter_id: z.int().min(1), engine_id: EngineIdSchema.optional() }),
    z.strictObject({ talk_id: z.int().min(0), engine_id: EngineIdSchema.optional() }),
  ])
  .meta({ title: "Subject" });
export type Subject = z.infer<typeof SubjectSchema>;

/** A matched recommendation joined with its candidate talk. */
export const PickSchema = RecommendationSchema.extend({ candidate: TalkSchema }).meta({ title: "Pick" });
export type Pick = z.infer<typeof PickSchema>;

export const PicksResponseSchema = z
  .strictObject({
    presenter_id: z.int().min(1).nullable(),
    anchors: z.array(TalkSchema),
    /** match=true rows for the anchors, ordered by for_talk_id, rank, candidate_id. */
    recommendations: z.array(PickSchema),
  })
  .meta({ title: "PicksResponse" });
export type PicksResponse = z.infer<typeof PicksResponseSchema>;

export const AgendaKindSchema = z.enum(["mine", "core", "surprise"]);
export type AgendaKind = z.infer<typeof AgendaKindSchema>;

/** Walking connection from the previous item on the same day. */
export const ConnectionSchema = z.strictObject({
  walk: z.int().min(0),
  /** Minutes to spare after walking: negative when the two talks clash. */
  slack: z.number(),
  /** slack is under the 15-minute threshold walk.ts's connection() calls tight. */
  tight: z.boolean(),
});
export type Connection = z.infer<typeof ConnectionSchema>;

/** The slim agenda item the calendar renders: not the whole Talk. Only timed talks appear, so start is non-null. */
export const AgendaItemSchema = z
  .strictObject({
    id: z.int().min(0),
    title: z.string().min(1),
    session_title: z.string().nullable(),
    start: z.iso.datetime(),
    end: z.iso.datetime().nullable(),
    building: z.string().nullable(),
    room: z.string().nullable(),
    units: z.array(z.string()),
    kind: AgendaKindSchema,
    transit: ConnectionSchema.nullable(),
  })
  .meta({ title: "AgendaItem" });
export type AgendaItem = z.infer<typeof AgendaItemSchema>;

export const AgendaDaySchema = z
  .strictObject({
    /** Conference-local (America/Denver) calendar date, YYYY-MM-DD. */
    date: z.iso.date(),
    items: z.array(AgendaItemSchema),
  })
  .meta({ title: "AgendaDay" });

export const AgendaResponseSchema = z
  .strictObject({
    presenter_id: z.int().min(1).nullable(),
    days: z.array(AgendaDaySchema),
  })
  .meta({ title: "AgendaResponse" });
export type AgendaResponse = z.infer<typeof AgendaResponseSchema>;

/** A talk or paper listed under a research theme: enough to name it and tell talks from papers. */
export const ThemeTalkSchema = z
  .strictObject({ id: z.int().min(0), title: z.string().min(1), type: z.string().nullable() })
  .meta({ title: "ThemeTalk" });

/** A research theme an engine found across the programme: concepts that talks use together. */
export const ThemeSchema = z
  .strictObject({
    id: z.string().min(1),
    title: z.string().min(1),
    summary: z.string(),
    concepts: z.array(z.string()),
    talks: z.array(ThemeTalkSchema),
  })
  .meta({ title: "Theme" });
export type Theme = z.infer<typeof ThemeSchema>;

export const ThemesResponseSchema = z
  .strictObject({ engine_id: EngineIdSchema, themes: z.array(ThemeSchema) })
  .meta({ title: "ThemesResponse" });
export type ThemesResponse = z.infer<typeof ThemesResponseSchema>;

/** A question about the whole conference, answered from the themes most related to it.
 *  answer is null when no language model is available: the themes alone are the answer. */
export const AskResponseSchema = z
  .strictObject({
    engine_id: EngineIdSchema,
    question: z.string().min(1),
    answer: z.string().nullable(),
    themes: z.array(ThemeSchema),
  })
  .meta({ title: "AskResponse" });
export type AskResponse = z.infer<typeof AskResponseSchema>;
