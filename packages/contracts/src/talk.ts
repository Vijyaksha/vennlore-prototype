import { z } from "zod";

const nullableString = z.string().nullable();
const nullableDatetime = z.iso.datetime().nullable();

/** One talk, as loaded from the APS feed. id 0 is reserved for an external anchor. */
export const TalkSchema = z
  .strictObject({
    id: z.int().min(0),
    external_id: nullableString,
    title: z.string().min(1),
    abstract: z.string(),
    units: z.array(z.string()),
    topics: z.array(z.string()),
    type: nullableString,
    is_invited: z.boolean(),
    is_withdrawn: z.boolean(),
    start: nullableDatetime,
    end: nullableDatetime,
    sort_order: z.int().nullable(),
    presentation_location: nullableString,
    author_ids: z.array(z.int()),
    presenter_ids: z.array(z.int()),
    publication_reference: nullableString,
    funding_acknowledgement: nullableString,
    team_acknowledgement: nullableString,
    session_id: z.int().nullable(),
    session_title: nullableString,
    session_code: nullableString,
    session_type: nullableString,
    session_topics: z.array(z.string()),
    building: nullableString,
    room: nullableString,
  })
  .meta({ id: "Talk", title: "Talk" });

export type Talk = z.infer<typeof TalkSchema>;
