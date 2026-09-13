"use client";

import Link from "next/link";
import { useFormatter, useTranslations } from "next-intl";

import { Badge } from "@repo/ui/components/badge";
import { Card } from "@repo/ui/components/card";
import { cn } from "@repo/ui/lib/utils";

import { denverDayKey, TIME_ZONE } from "@/lib/conference";

// Dates cross the tRPC HTTP boundary as ISO strings.
export interface Pick {
  candidateId: number;
  /** The presenter's anchor talk this pick was recommended for. */
  forTalkId: number;
  title: string;
  sessionTitle: string | null;
  units: string[];
  start: string | null;
  /** Engine score between 0 and 1. */
  score: number;
  crossDomain: boolean;
  why: string;
  sharedMethods: string[];
}

export interface Anchor {
  id: number;
  title: string;
}

export function PickCard({ pick, anchors }: { pick: Pick; anchors: Anchor[] }) {
  const t = useTranslations("picks");
  const format = useFormatter();

  const start = pick.start === null ? null : new Date(pick.start);
  const kind = pick.crossDomain ? t("unexpected") : t("core");
  const division = pick.units.join("/");
  // Only a presenter with several talks needs to know which one a pick is for.
  const forTalk =
    anchors.length > 1
      ? anchors.find((anchor) => anchor.id === pick.forTalkId)
      : undefined;
  const calendarHref =
    start === null
      ? "/calendar"
      : `/calendar?date=${denverDayKey(start)}`;

  return (
    <Card
      className={cn(
        "flex min-h-[430px] snap-center flex-col gap-3 overflow-visible rounded-lg",
        "border border-border bg-card px-[18px] pt-5 pb-4 ring-0 transition-colors",
        "hover:border-primary focus-within:border-primary",
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <Badge
          className={cn(
            "h-auto rounded-full border-transparent px-2.5 py-[3px] font-mono text-[10.5px] font-normal tracking-[0.06em]",
            pick.crossDomain
              ? "bg-surprise-soft text-surprise"
              : "bg-accent-soft text-primary",
          )}
        >
          {division === "" ? kind : `${division} · ${kind}`}
        </Badge>
        <span className="font-mono text-[11px] text-faint tabular-nums">
          {t("score", { score: pick.score })}
        </span>
      </div>
      {forTalk !== undefined && (
        <span
          title={forTalk.title}
          className="truncate font-mono text-[10.5px] text-muted-foreground"
        >
          {t("forTalk", { title: forTalk.title })}
        </span>
      )}
      <h3 className="text-lg leading-[1.32] font-semibold text-balance text-card-foreground">
        {pick.title}
      </h3>
      {pick.sessionTitle !== null && (
        <span className="font-mono text-[11.5px] text-faint tabular-nums">
          {pick.sessionTitle}
        </span>
      )}
      <p className="flex-1 border-l-2 border-primary pl-3 font-serif text-[14.5px] leading-[1.55] italic">
        {pick.why}
      </p>
      {pick.sharedMethods.length > 0 && (
        <div
          role="group"
          aria-label={t("sharedMethods")}
          className="flex flex-wrap gap-1.5"
        >
          {pick.sharedMethods.map((method) => (
            <Badge
              key={method}
              variant="outline"
              className="font-mono text-[10.5px] font-normal"
            >
              {method}
            </Badge>
          ))}
        </div>
      )}
      <div className="flex items-center justify-between border-t border-border pt-3">
        <span className="font-mono text-[11.5px] text-muted-foreground tabular-nums">
          {start === null
            ? t("untimed")
            : t("when", {
                dow: format.dateTime(start, { weekday: "short", timeZone: TIME_ZONE }),
                date: format.dateTime(start, {
                  month: "numeric",
                  day: "numeric",
                  timeZone: TIME_ZONE,
                }),
                time: format.dateTime(start, {
                  hour: "numeric",
                  minute: "2-digit",
                  timeZone: TIME_ZONE,
                }),
              })}
        </span>
        <Link
          href={calendarHref}
          className="text-[13px] font-medium text-primary"
        >
          {t("calendar")}
        </Link>
      </div>
    </Card>
  );
}
