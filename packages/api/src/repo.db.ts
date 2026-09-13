import { and, arrayContains, asc, eq, inArray } from "drizzle-orm";

import { getDb } from "./db/index";
import { recommendations, talks } from "./db/schema";
import type { Repo } from "./repo";

/** Repo over Drizzle. getDb() is called inside each method, so importing this
 *  module never needs DATABASE_URL. */
export const dbRepo: Repo = {
  async getTalk(id) {
    const rows = await getDb().select().from(talks).where(eq(talks.id, id)).limit(1);
    return rows[0] ?? null;
  },

  async getTalks(ids) {
    if (ids.length === 0) return [];
    return getDb().select().from(talks).where(inArray(talks.id, ids)).orderBy(asc(talks.id));
  },

  async anchorsFor(presenterId) {
    return getDb()
      .select()
      .from(talks)
      .where(arrayContains(talks.presenterIds, [presenterId]))
      .orderBy(asc(talks.id));
  },

  async authoredBy(presenterId) {
    const rows = await getDb()
      .select({ id: talks.id })
      .from(talks)
      .where(arrayContains(talks.authorIds, [presenterId]));
    return new Set(rows.map((r) => r.id));
  },

  async getMatches(forTalkIds, engineId) {
    if (forTalkIds.length === 0) return [];
    const rows = await getDb()
      .select()
      .from(recommendations)
      .innerJoin(talks, eq(recommendations.candidateId, talks.id))
      .where(
        and(
          eq(recommendations.engineId, engineId),
          eq(recommendations.match, true),
          inArray(recommendations.forTalkId, forTalkIds),
        ),
      )
      .orderBy(
        asc(recommendations.forTalkId),
        asc(recommendations.rank),
        asc(recommendations.candidateId),
      );
    return rows.map((row) => ({ ...row.recommendations, candidate: row.talks }));
  },
};
