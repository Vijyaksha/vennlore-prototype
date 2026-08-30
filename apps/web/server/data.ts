import { and, asc, desc, eq, ilike } from "drizzle-orm";

import { getDb } from "../db";
import { recommendations, talks } from "../db/schema";

export type TalkRow = typeof talks.$inferSelect;
export type RecRow = typeof recommendations.$inferSelect;

export interface Repo {
  searchTalks(query: string): Promise<TalkRow[]>;
  getTalk(id: number): Promise<TalkRow | null>;
  getMatches(forTalkId: number): Promise<(RecRow & { talk: TalkRow })[]>;
}

// Postgres LIKE/ILIKE treats %, _ and the default backslash escape character
// as metacharacters; user queries must match them literally.
export function escapeLike(value: string): string {
  return value.replace(/[\\%_]/g, (char) => `\\${char}`);
}

export const dbRepo: Repo = {
  async searchTalks(query) {
    return getDb()
      .select()
      .from(talks)
      .where(ilike(talks.title, `%${escapeLike(query)}%`))
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
      .orderBy(desc(recommendations.score), asc(recommendations.candidateId));
    return rows.map((row) => ({ ...row.recommendations, talk: row.talks }));
  },
};
