import type { locations, recommendations, talks } from "./schema";

export interface SeedTalkRow {
  id?: number;
  title?: string;
  session_title?: string | null;
  units?: string[];
  start?: string | null;
  end?: string | null;
  building?: string | null;
  room?: string | null;
  abstract?: string;
}

export interface SeedRecommendationRow {
  for_talk_id?: number;
  candidate_id?: number;
  same_method?: number;
  specificity?: number;
  usage_parallel?: number;
  score?: number;
  match?: boolean;
  cross_domain?: boolean;
  why?: string;
  strongest_parallel?: string;
}

export interface SeedLocationRow {
  id?: number;
  building?: string;
  room?: string;
}

export type TalkInsert = typeof talks.$inferInsert;
export type RecommendationInsert = typeof recommendations.$inferInsert;
export type LocationInsert = typeof locations.$inferInsert;

function parseDate(value: string | null | undefined, label: string): Date | null {
  if (value === null || value === undefined) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new Error(`${label}: unparseable date "${value}"`);
  }
  return date;
}

export function toTalkInsert(row: SeedTalkRow): TalkInsert {
  const label = `talk ${row.id ?? "<missing id>"}`;
  if (typeof row.id !== "number") {
    throw new Error(`${label}: missing id`);
  }
  if (!row.title) {
    throw new Error(`${label}: missing title`);
  }
  return {
    id: row.id,
    title: row.title,
    sessionTitle: row.session_title ?? null,
    units: row.units ?? [],
    start: parseDate(row.start, label),
    end: parseDate(row.end, label),
    building: row.building ?? null,
    room: row.room ?? null,
    abstract: row.abstract ?? "",
  };
}

export function toRecommendationInsert(
  row: SeedRecommendationRow,
): RecommendationInsert {
  const label = `recommendation ${row.for_talk_id ?? "<missing for_talk_id>"} -> ${row.candidate_id ?? "<missing candidate_id>"}`;
  const requireNumber = (value: number | undefined, field: string): number => {
    if (typeof value !== "number") {
      throw new Error(`${label}: missing ${field}`);
    }
    return value;
  };
  const requireBoolean = (value: boolean | undefined, field: string): boolean => {
    if (typeof value !== "boolean") {
      throw new Error(`${label}: missing ${field}`);
    }
    return value;
  };
  return {
    forTalkId: requireNumber(row.for_talk_id, "for_talk_id"),
    candidateId: requireNumber(row.candidate_id, "candidate_id"),
    sameMethod: requireNumber(row.same_method, "same_method"),
    specificity: requireNumber(row.specificity, "specificity"),
    usageParallel: requireNumber(row.usage_parallel, "usage_parallel"),
    score: requireNumber(row.score, "score"),
    match: requireBoolean(row.match, "match"),
    crossDomain: requireBoolean(row.cross_domain, "cross_domain"),
    why: row.why ?? "",
    strongestParallel: row.strongest_parallel ?? "",
  };
}

export function toLocationInsert(row: SeedLocationRow): LocationInsert {
  const label = `location ${row.id ?? "<missing id>"}`;
  if (typeof row.id !== "number") {
    throw new Error(`${label}: missing id`);
  }
  if (!row.building) {
    throw new Error(`${label}: missing building`);
  }
  if (!row.room) {
    throw new Error(`${label}: missing room`);
  }
  return {
    id: row.id,
    building: row.building,
    room: row.room,
  };
}
