import { and, asc, desc, eq } from "drizzle-orm";

import { getDb } from "../db";
import { recommendations, talks } from "../db/schema";

export type TalkRow = typeof talks.$inferSelect;
export type RecRow = typeof recommendations.$inferSelect;

export interface Repo {
  getTalk(id: number): Promise<TalkRow | null>;
  getMatches(forTalkId: number): Promise<(RecRow & { talk: TalkRow })[]>;
}

export const dbRepo: Repo = {
  async getTalk(id) {
    const rows = await getDb().select().from(talks).where(eq(talks.id, id)).limit(1);
    return rows[0] ?? null;
  },

  async getMatches(forTalkId) {
    const rows = await getDb()
      .select()
      .from(recommendations)
      .innerJoin(talks, eq(recommendations.candidateId, talks.id))
      .where(
        and(
          eq(recommendations.forTalkId, forTalkId),
          eq(recommendations.match, true),
        ),
      )
      .orderBy(desc(recommendations.score), asc(recommendations.candidateId));
    return rows.map((row) => ({ ...row.recommendations, talk: row.talks }));
  },
};
