import { CONTRACT_VERSION } from "@repo/contracts";
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
      .where(arrayContains(talks.presenter_ids, [presenterId]))
      .orderBy(asc(talks.id));
  },

  async authoredBy(presenterId) {
    const rows = await getDb()
      .select({ id: talks.id })
      .from(talks)
      .where(arrayContains(talks.author_ids, [presenterId]));
    return new Set(rows.map((r) => r.id));
  },

  async getMatches(forTalkIds, engine_id) {
    if (forTalkIds.length === 0) return [];
    const rows = await getDb()
      .select()
      .from(recommendations)
      .innerJoin(talks, eq(recommendations.candidate_id, talks.id))
      .where(
        and(
          eq(recommendations.engine_id, engine_id),
          eq(recommendations.match, true),
          eq(recommendations.contract_version, CONTRACT_VERSION),
          inArray(recommendations.for_talk_id, forTalkIds),
        ),
      )
      .orderBy(
        asc(recommendations.for_talk_id),
        asc(recommendations.rank),
        asc(recommendations.candidate_id),
      );
    return rows.map((row) => ({ ...row.recommendations, candidate: row.talks }));
  },
};
