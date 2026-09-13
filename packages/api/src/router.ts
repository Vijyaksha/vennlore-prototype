import { TRPCError } from "@trpc/server";
import { z } from "zod";

import { groupByDenverDay } from "./agenda";
import type { MatchRow, Repo, TalkRow } from "./repo";
import { publicProcedure, router } from "./trpc";

/** Who the picks are for: a presenter (all their talks are anchors) or one talk. */
const Subject = z.union([
  z.object({ presenterId: z.int().min(1), engineId: z.string().optional() }),
  z.object({ talkId: z.int().min(0), engineId: z.string().optional() }),
]);
type Subject = z.infer<typeof Subject>;

export type AgendaKind = "mine" | "core" | "surprise";

async function resolveAnchors(repo: Repo, input: Subject): Promise<{ presenterId: number | null; anchors: TalkRow[] }> {
  if ("presenterId" in input) {
    const anchors = await repo.anchorsFor(input.presenterId);
    if (anchors.length === 0) {
      throw new TRPCError({ code: "NOT_FOUND", message: `presenter ${input.presenterId} not found` });
    }
    return { presenterId: input.presenterId, anchors };
  }
  const talk = await repo.getTalk(input.talkId);
  if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.talkId} not found` });
  return { presenterId: null, anchors: [talk] };
}

/** The slim agenda fields: what the calendar renders, not the whole talk row. */
function agendaEntry(t: TalkRow, kind: AgendaKind) {
  return {
    id: t.id,
    title: t.title,
    sessionTitle: t.sessionTitle,
    start: t.start,
    end: t.end,
    building: t.building,
    room: t.room,
    units: t.units,
    kind,
  };
}

export const appRouter = router({
  talk: router({
    get: publicProcedure.input(z.object({ id: z.int().min(0) })).query(async ({ ctx, input }) => {
      const talk = await ctx.repo.getTalk(input.id);
      if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.id} not found` });
      return talk;
    }),
  }),
  presenter: router({
    picks: publicProcedure.input(Subject).query(async ({ ctx, input }) => {
      const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
      const recommendations: MatchRow[] = await ctx.repo.getMatches(
        anchors.map((a) => a.id),
        input.engineId ?? ctx.engineId,
      );
      return { presenterId, anchors, recommendations };
    }),
    agenda: publicProcedure.input(Subject).query(async ({ ctx, input }) => {
      const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
      const matches = await ctx.repo.getMatches(
        anchors.map((a) => a.id),
        input.engineId ?? ctx.engineId,
      );
      // A candidate matched under several anchors keeps the last kind written;
      // a presenter's own talk is always "mine".
      const entries = new Map<number, ReturnType<typeof agendaEntry>>();
      for (const m of matches) entries.set(m.candidateId, agendaEntry(m.candidate, m.crossDomain ? "surprise" : "core"));
      for (const a of anchors) entries.set(a.id, agendaEntry(a, "mine"));
      return { presenterId, days: groupByDenverDay([...entries.values()]) };
    }),
  }),
});

export type AppRouter = typeof appRouter;
