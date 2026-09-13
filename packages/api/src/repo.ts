import { CONTRACT_VERSION } from "@repo/contracts";

import type { recommendations, talks } from "./db/schema";

export type TalkRow = typeof talks.$inferSelect;
export type RecRow = typeof recommendations.$inferSelect;
export type MatchRow = RecRow & { candidate: TalkRow };

/** Everything the router needs from the store. dbRepo implements it over
 *  Drizzle; memoryRepo implements it over arrays for tests. */
export interface Repo {
  getTalk(id: number): Promise<TalkRow | null>;
  /** Unique talks for the given ids, sorted by id. */
  getTalks(ids: number[]): Promise<TalkRow[]>;
  anchorsFor(presenterId: number): Promise<TalkRow[]>;
  authoredBy(presenterId: number): Promise<Set<number>>;
  /** match=true rows of one engine written under the current contract version,
   *  for the given anchors, ordered by for_talk_id, rank, candidate_id. */
  getMatches(forTalkIds: number[], engine_id: string): Promise<MatchRow[]>;
}

export function memoryRepo(talkRows: TalkRow[], recRows: RecRow[]): Repo {
  const byId = new Map(talkRows.map((t) => [t.id, t]));
  return {
    getTalk: async (id) => byId.get(id) ?? null,
    getTalks: async (ids) =>
      [...new Set(ids)]
        .map((id) => byId.get(id))
        .filter((t): t is TalkRow => t !== undefined)
        .sort((a, b) => a.id - b.id),
    anchorsFor: async (presenterId) =>
      talkRows.filter((t) => t.presenter_ids.includes(presenterId)).sort((a, b) => a.id - b.id),
    authoredBy: async (presenterId) =>
      new Set(talkRows.filter((t) => t.author_ids.includes(presenterId)).map((t) => t.id)),
    getMatches: async (forTalkIds, engine_id) =>
      recRows
        .filter(
          (r) =>
            r.engine_id === engine_id &&
            r.match &&
            r.contract_version === CONTRACT_VERSION &&
            forTalkIds.includes(r.for_talk_id),
        )
        .sort((a, b) => a.for_talk_id - b.for_talk_id || a.rank - b.rank || a.candidate_id - b.candidate_id)
        .flatMap((r) => {
          const c = byId.get(r.candidate_id);
          return c ? [{ ...r, candidate: c }] : [];
        }),
  };
}
