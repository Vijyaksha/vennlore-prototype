import { and, desc, eq, ilike } from "drizzle-orm";

import { getDb } from "../db";
import { recommendations, talks } from "../db/schema";

export type TalkRow = typeof talks.$inferSelect;
export type RecRow = typeof recommendations.$inferSelect;

export interface Repo {
  searchTalks(query: string): Promise<TalkRow[]>;
  getTalk(id: number): Promise<TalkRow | null>;
  getMatches(forTalkId: number): Promise<(RecRow & { talk: TalkRow })[]>;
}

export const dbRepo: Repo = {
  async searchTalks(query) {
    return getDb()
      .select()
      .from(talks)
      .where(ilike(talks.title, `%${query}%`))
      .limit(20);
  },

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
      .orderBy(desc(recommendations.score));
    return rows.map((row) => ({ ...row.recommendations, talk: row.talks }));
  },
};
