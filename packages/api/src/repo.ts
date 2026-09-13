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
  getMatches(forTalkIds: number[], engineId: string): Promise<MatchRow[]>;
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
      talkRows.filter((t) => t.presenterIds.includes(presenterId)).sort((a, b) => a.id - b.id),
    authoredBy: async (presenterId) =>
      new Set(talkRows.filter((t) => t.authorIds.includes(presenterId)).map((t) => t.id)),
    getMatches: async (forTalkIds, engineId) =>
      recRows
        .filter(
          (r) =>
            r.engineId === engineId &&
            r.match &&
            r.contractVersion === CONTRACT_VERSION &&
            forTalkIds.includes(r.forTalkId),
        )
        .sort((a, b) => a.forTalkId - b.forTalkId || a.rank - b.rank || a.candidateId - b.candidateId)
        .flatMap((r) => {
          const c = byId.get(r.candidateId);
          return c ? [{ ...r, candidate: c }] : [];
        }),
  };
}
