import { TRPCError } from "@trpc/server";
import {
  AgendaResponseSchema, PicksResponseSchema, SubjectSchema, TalkSchema,
  type AgendaItem, type AgendaKind, type Subject,
} from "@repo/contracts";
import { z } from "zod";

import { groupByDenverDay } from "./agenda";
import type { MatchRow, Repo, TalkRow } from "./repo";
import { publicProcedure, router } from "./trpc";
import { toPick, toTalk } from "./wire";

async function resolveAnchors(repo: Repo, input: Subject): Promise<{ presenterId: number | null; anchors: TalkRow[] }> {
  if ("presenter_id" in input) {
    const anchors = await repo.anchorsFor(input.presenter_id);
    if (anchors.length === 0) {
      throw new TRPCError({ code: "NOT_FOUND", message: `presenter ${input.presenter_id} not found` });
    }
    return { presenterId: input.presenter_id, anchors };
  }
  const talk = await repo.getTalk(input.talk_id);
  if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.talk_id} not found` });
  return { presenterId: null, anchors: [talk] };
}

/** In-process agenda entry: the slim agenda fields, with Date starts so
 *  groupByDenverDay can sort and compute transit before they become ISO strings. */
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
    get: publicProcedure
      .input(z.object({ id: z.int().min(0) }))
      .output(TalkSchema)
      .query(async ({ ctx, input }) => {
        const talk = await ctx.repo.getTalk(input.id);
        if (talk === null) throw new TRPCError({ code: "NOT_FOUND", message: `talk ${input.id} not found` });
        return toTalk(talk);
      }),
  }),
  presenter: router({
    picks: publicProcedure
      .input(SubjectSchema)
      .output(PicksResponseSchema)
      .query(async ({ ctx, input }) => {
        const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
        const matches: MatchRow[] = await ctx.repo.getMatches(
          anchors.map((a) => a.id),
          input.engine_id ?? ctx.engineId,
        );
        return { presenter_id: presenterId, anchors: anchors.map(toTalk), recommendations: matches.map(toPick) };
      }),
    agenda: publicProcedure
      .input(SubjectSchema)
      .output(AgendaResponseSchema)
      .query(async ({ ctx, input }) => {
        const { presenterId, anchors } = await resolveAnchors(ctx.repo, input);
        const matches = await ctx.repo.getMatches(
          anchors.map((a) => a.id),
          input.engine_id ?? ctx.engineId,
        );
        // A candidate matched under several anchors takes its kind from its
        // best-scoring match (first in getMatches order on ties), agreeing with the
        // merged picks rail; a presenter's own talk is always "mine".
        const best = new Map<number, MatchRow>();
        for (const m of matches) {
          const prev = best.get(m.candidateId);
          if (prev === undefined || m.score > prev.score) best.set(m.candidateId, m);
        }
        const entries = new Map<number, ReturnType<typeof agendaEntry>>();
        for (const m of best.values()) entries.set(m.candidateId, agendaEntry(m.candidate, m.crossDomain ? "surprise" : "core"));
        for (const a of anchors) entries.set(a.id, agendaEntry(a, "mine"));
        const mineFirst = (a: { kind: AgendaKind }, b: { kind: AgendaKind }) => Number(b.kind === "mine") - Number(a.kind === "mine");
        const days = groupByDenverDay([...entries.values()], mineFirst).map((d) => ({
          date: d.date,
          items: d.items.map((i): AgendaItem => ({
            id: i.id, title: i.title, session_title: i.sessionTitle,
            start: i.start.toISOString(), end: i.end === null ? null : i.end.toISOString(),
            building: i.building, room: i.room, units: i.units, kind: i.kind, transit: i.transit,
          })),
        }));
        return { presenter_id: presenterId, days };
      }),
  }),
});

export type AppRouter = typeof appRouter;
