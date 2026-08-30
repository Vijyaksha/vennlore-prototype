"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useFormatter, useTranslations } from "next-intl";
import { Suspense, useState } from "react";

import { Button } from "@repo/ui/components/button";
import { Skeleton } from "@repo/ui/components/skeleton";

import { Agenda, type AgendaEntry, type AgendaKind } from "@/components/agenda";
import { DayStrip } from "@/components/day-strip";
import { ErrorState } from "@/components/error-state";
import { CONFERENCE_DAYS, dayDate, TIME_ZONE } from "@/lib/conference";
import { trpc } from "@/lib/trpc";

function CalendarSkeleton() {
  const t = useTranslations("common");
  return (
    <div aria-label={t("loading")} className="px-5 pt-[18px]">
      <Skeleton className="h-14 w-44 rounded-md" />
      <div className="flex gap-1.5 pt-4 pb-2">
        {CONFERENCE_DAYS.map((date) => (
          <Skeleton key={date} className="h-14 min-w-[50px] flex-1 rounded-[10px]" />
        ))}
      </div>
      <div className="flex flex-col gap-3.5 pt-3.5">
        <Skeleton className="h-24 rounded-lg" />
        <Skeleton className="h-24 rounded-lg" />
      </div>
    </div>
  );
}

function CalendarScreen() {
  const t = useTranslations("agenda");
  const format = useFormatter();
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const talkId = Number(params.id);
  const validId = Number.isFinite(talkId);

  const agenda = trpc.agenda.useQuery({ talkId }, { enabled: validId });
  const picks = trpc.picks.useQuery({ talkId }, { enabled: validId });

  const paramIndex = (CONFERENCE_DAYS as readonly string[]).indexOf(
    searchParams.get("date") ?? "",
  );
  const [selected, setSelected] = useState<number | null>(
    paramIndex >= 0 ? paramIndex : null,
  );

  if (!validId || agenda.isError || picks.isError) {
    return (
      <ErrorState
        onRetry={() => {
          void agenda.refetch();
          void picks.refetch();
        }}
      />
    );
  }

  if (agenda.isPending || picks.isPending) {
    return <CalendarSkeleton />;
  }

  const kinds = new Map<number, { kind: AgendaKind; units: string[] }>();
  for (const pick of picks.data.core) {
    kinds.set(pick.candidateId, { kind: "core", units: pick.units });
  }
  for (const pick of picks.data.unexpected) {
    kinds.set(pick.candidateId, { kind: "surprise", units: pick.units });
  }
  kinds.set(talkId, { kind: "mine", units: picks.data.talk.units });

  const byDate = new Map(agenda.data.days.map((day) => [day.date, day.items]));
  const days = CONFERENCE_DAYS.map((date) => {
    const items: AgendaEntry[] = (byDate.get(date) ?? []).map((item) => ({
      ...item,
      kind: kinds.get(item.id)?.kind ?? "surprise",
      units: kinds.get(item.id)?.units ?? [],
    }));
    return { date, items, pips: items.map((item) => item.kind) };
  });

  const firstWithItems = days.findIndex((day) => day.items.length > 0);
  const active = selected ?? Math.max(firstWithItems, 0);
  const day = days[active]!;
  const date = dayDate(day.date);

  return (
    <section>
      <div className="flex items-center justify-between px-5 pt-[18px] pb-1">
        <h2 className="font-serif text-2xl font-normal">
          <span className="mb-0.5 block font-mono text-xs tracking-[0.1em] text-faint uppercase">
            {t("dayCount", {
              dow: format.dateTime(date, { weekday: "short", timeZone: TIME_ZONE }),
              day: active + 1,
              total: CONFERENCE_DAYS.length,
            })}
          </span>
          {format.dateTime(date, {
            month: "long",
            day: "numeric",
            timeZone: TIME_ZONE,
          })}
        </h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            aria-label={t("previousDay")}
            disabled={active === 0}
            onClick={() => setSelected(active - 1)}
            className="h-[38px] w-[38px] rounded-[10px] border-border bg-card text-base text-foreground disabled:text-faint"
          >
            ‹
          </Button>
          <Button
            variant="outline"
            aria-label={t("nextDay")}
            disabled={active === days.length - 1}
            onClick={() => setSelected(active + 1)}
            className="h-[38px] w-[38px] rounded-[10px] border-border bg-card text-base text-foreground disabled:text-faint"
          >
            ›
          </Button>
        </div>
      </div>
      <DayStrip days={days} activeIndex={active} onSelect={setSelected} />
      <Agenda items={day.items} />
    </section>
  );
}

export default function CalendarPage() {
  return (
    <Suspense fallback={<CalendarSkeleton />}>
      <CalendarScreen />
    </Suspense>
  );
}
