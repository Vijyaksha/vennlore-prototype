import { TRPCError } from "@trpc/server";
import {
  AgendaResponseSchema, AskResponseSchema, PicksResponseSchema, SubjectSchema, TalkSchema,
  ThemesResponseSchema,
  type AgendaItem, type AgendaKind, type Subject,
} from "@repo/contracts";
import { z } from "zod";

import { groupByDenverDay } from "./agenda";
import type { MatchRow, Repo, TalkRow } from "./repo";
import { SearchError, type SearchClient } from "./search";
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

/** Free-text search: a mutation (POST), since research descriptions are long. */
const SearchInputSchema = z.strictObject({ text: z.string().trim().min(10).max(4000) });
const AskInputSchema = z.strictObject({ question: z.string().trim().min(3).max(1000) });

/** Runs a call to the pipeline's search service, turning its failures into tRPC errors. */
async function viaSearch<T>(search: SearchClient | undefined, fn: (s: SearchClient) => Promise<T>): Promise<T> {
  if (search === undefined) {
    throw new TRPCError({ code: "SERVICE_UNAVAILABLE", message: "search is not configured" });
  }
  try {
    return await fn(search);
  } catch (error) {
    if (!(error instanceof SearchError)) throw error;
    throw new TRPCError({
      code: error.kind === "bad_request" ? "BAD_REQUEST"
        : error.kind === "unavailable" ? "SERVICE_UNAVAILABLE" : "BAD_GATEWAY",
      message: error.message,
    });
  }
}

export const appRouter = router({
  search: router({
    recommend: publicProcedure
      .input(SearchInputSchema)
      .output(PicksResponseSchema)
      .mutation(async ({ ctx, input }) => {
        const { anchor, picks } = await viaSearch(ctx.search, (s) => s.recommend(input.text));
        // The service's rows are untrusted until they parse as the contract.
        return PicksResponseSchema.parse({ presenter_id: null, anchors: [anchor], recommendations: picks });
      }),
  }),
  themes: router({
    list: publicProcedure
      .output(ThemesResponseSchema)
      .query(async ({ ctx }) => ThemesResponseSchema.parse(await viaSearch(ctx.search, (s) => s.themes()))),
    ask: publicProcedure
      .input(AskInputSchema)
      .output(AskResponseSchema)
      .mutation(async ({ ctx, input }) =>
        AskResponseSchema.parse(await viaSearch(ctx.search, (s) => s.ask(input.question)))),
  }),
  talk: router({
    get: publicProcedure
      .input(z.strictObject({ id: z.int().min(0) }))
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
          const prev = best.get(m.candidate_id);
          if (prev === undefined || m.score > prev.score) best.set(m.candidate_id, m);
        }
        // TalkRow already satisfies AgendaInput and groupByDenverDay carries extra
        // fields through, so the rows themselves are the in-process agenda entries;
        // the slim AgendaItem is cut from them once transit has been computed.
        const entries = new Map<number, TalkRow & { kind: AgendaKind }>();
        for (const m of best.values())
          entries.set(m.candidate_id, { ...m.candidate, kind: m.cross_domain ? "surprise" : "core" });
        for (const a of anchors) entries.set(a.id, { ...a, kind: "mine" });
        const mineFirst = (a: { kind: AgendaKind }, b: { kind: AgendaKind }) => Number(b.kind === "mine") - Number(a.kind === "mine");
        const days = groupByDenverDay([...entries.values()], mineFirst).map((d) => ({
          date: d.date,
          items: d.items.map((i): AgendaItem => ({
            id: i.id, title: i.title, session_title: i.session_title,
            start: i.start.toISOString(), end: i.end === null ? null : i.end.toISOString(),
            building: i.building, room: i.room, units: i.units, kind: i.kind, transit: i.transit,
          })),
        }));
        return { presenter_id: presenterId, days };
      }),
  }),
});

export type AppRouter = typeof appRouter;
