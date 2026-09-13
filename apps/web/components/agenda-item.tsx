"use client";

import { useFormatter, useTranslations } from "next-intl";

import { Badge } from "@repo/ui/components/badge";
import { Card } from "@repo/ui/components/card";
import { cn } from "@repo/ui/lib/utils";

import { TIME_ZONE } from "@/lib/conference";

export type AgendaKind = "core" | "surprise" | "mine";

export interface AgendaEntry {
  id: number;
  title: string;
  sessionTitle: string | null;
  start: string;
  end: string | null;
  room: string | null;
  transit: { walk: number; slack: number; tight: boolean } | null;
  kind: AgendaKind;
  units: string[];
}

function Grip() {
  return (
    <span
      aria-hidden="true"
      className="absolute top-1/2 right-2.5 grid -translate-y-1/2 grid-cols-[4px_4px] gap-[3px] opacity-55"
    >
      {Array.from({ length: 6 }, (_, index) => (
        <i key={index} className="h-1 w-1 rounded-full bg-faint" />
      ))}
    </span>
  );
}

export function AgendaItem({ item }: { item: AgendaEntry }) {
  const t = useTranslations("agenda");
  const format = useFormatter();

  const mine = item.kind === "mine";
  const time = (value: Date | string) =>
    format.dateTime(new Date(value), {
      hour: "numeric",
      minute: "2-digit",
      timeZone: TIME_ZONE,
    });

  return (
    <div
      data-kind={item.kind}
      className="relative mb-3.5 grid grid-cols-[64px_1fr] gap-x-2.5"
    >
      <span
        aria-hidden="true"
        className={cn(
          "absolute top-[18px] left-[60px] z-10 h-[9px] w-[9px] rounded-full ring-[3px] ring-background",
          item.kind === "surprise" ? "bg-surprise" : "bg-primary",
        )}
      />
      <div className="border-r border-border pt-3.5 pr-0.5 text-right font-mono tabular-nums">
        <div className="text-[12.5px] text-foreground">{time(item.start)}</div>
        {item.end !== null && (
          <div className="mt-px text-[10.5px] text-faint">{time(item.end)}</div>
        )}
      </div>
      <Card
        className={cn(
          "relative ml-2 gap-0 overflow-visible rounded-lg border border-border bg-card px-4 py-3.5 ring-0",
          mine && "border-primary bg-accent-soft",
        )}
      >
        <div className="flex items-center justify-between gap-2">
          <Badge
            className={cn(
              "h-auto rounded-full border-transparent px-2.5 py-[3px] font-mono text-[10.5px] font-normal tracking-[0.06em]",
              item.kind === "surprise"
                ? "bg-surprise-soft text-surprise"
                : "bg-accent-soft text-primary",
            )}
          >
            {mine ? t("yourTalk") : item.units.join("/")}
          </Badge>
          {item.room !== null && (
            <span className="font-mono text-[11.5px] text-faint tabular-nums">
              {item.room}
            </span>
          )}
        </div>
        <h3 className="mt-2 mb-[3px] pr-[18px] text-[15.5px] leading-[1.35] font-semibold text-balance">
          {item.title}
        </h3>
        <span className="block font-mono text-[11.5px] text-muted-foreground tabular-nums">
          {mine ? t("presenting") : item.sessionTitle}
        </span>
        <Grip />
      </Card>
    </div>
  );
}
