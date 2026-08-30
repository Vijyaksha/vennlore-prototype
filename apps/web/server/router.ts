import { TRPCError } from "@trpc/server";
import { z } from "zod";

import { connection, walkMinutes, type Connection } from "../lib/walk";
import type { RecRow, TalkRow } from "./data";
import { publicProcedure, router } from "./trpc";

export interface PickRow {
  candidateId: number;
  title: string;
  sessionTitle: string | null;
  units: string[];
  start: Date | null;
  end: Date | null;
  building: string | null;
  room: string | null;
  score: number;
  sameMethod: number;
  specificity: number;
  usageParallel: number;
  why: string;
  strongestParallel: string;
  crossDomain: boolean;
}

export interface AgendaItem {
  id: number;
  title: string;
  sessionTitle: string | null;
  start: Date;
  end: Date | null;
  building: string | null;
  room: string | null;
  transit: Connection | null;
}

function toPickRow(match: RecRow & { talk: TalkRow }): PickRow {
  return {
    candidateId: match.candidateId,
    title: match.talk.title,
    sessionTitle: match.talk.sessionTitle,
    units: match.talk.units,
    start: match.talk.start,
    end: match.talk.end,
    building: match.talk.building,
    room: match.talk.room,
    score: match.score,
    sameMethod: match.sameMethod,
    specificity: match.specificity,
    usageParallel: match.usageParallel,
    why: match.why,
    strongestParallel: match.strongestParallel,
    crossDomain: match.crossDomain,
  };
}

const denverDate = new Intl.DateTimeFormat("en-CA", {
  timeZone: "America/Denver",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

async function getTalkOrThrow(
  repo: { getTalk(id: number): Promise<TalkRow | null> },
  talkId: number,
): Promise<TalkRow> {
  const talk = await repo.getTalk(talkId);
  if (talk === null) {
    throw new TRPCError({ code: "NOT_FOUND", message: `talk ${talkId} not found` });
  }
  return talk;
}

export const appRouter = router({
  searchTalks: publicProcedure
    .input(z.object({ query: z.string().min(2) }))
    .query(({ ctx, input }) => ctx.repo.searchTalks(input.query)),

  picks: publicProcedure
    .input(z.object({ talkId: z.number() }))
    .query(async ({ ctx, input }) => {
      const talk = await getTalkOrThrow(ctx.repo, input.talkId);
      const matches = await ctx.repo.getMatches(input.talkId);
      const picks = matches.map(toPickRow);
      return {
        talk,
        core: picks.filter((p) => !p.crossDomain),
        unexpected: picks.filter((p) => p.crossDomain),
      };
    }),

  agenda: publicProcedure
    .input(z.object({ talkId: z.number() }))
    .query(async ({ ctx, input }) => {
      const talk = await getTalkOrThrow(ctx.repo, input.talkId);
      const matches = await ctx.repo.getMatches(input.talkId);

      const timed = [talk, ...matches.map((m) => m.talk)].filter(
        (t): t is TalkRow & { start: Date } => t.start !== null,
      );
      timed.sort((a, b) => a.start.getTime() - b.start.getTime());

      const byDate = new Map<string, AgendaItem[]>();
      for (const t of timed) {
        const date = denverDate.format(t.start);
        const items = byDate.get(date) ?? [];
        const previous = items.at(-1);
        let transit: Connection | null = null;
        if (previous !== undefined) {
          const departure = previous.end ?? previous.start;
          const gapMinutes = (t.start.getTime() - departure.getTime()) / 60_000;
          transit = connection(gapMinutes, walkMinutes(previous, t));
        }
        items.push({
          id: t.id,
          title: t.title,
          sessionTitle: t.sessionTitle,
          start: t.start,
          end: t.end,
          building: t.building,
          room: t.room,
          transit,
        });
        byDate.set(date, items);
      }

      return {
        days: [...byDate.entries()]
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([date, items]) => ({ date, items })),
      };
    }),
});

export type AppRouter = typeof appRouter;
