"use client";

import type { AgendaKind } from "@repo/contracts";
import { useFormatter, useTranslations } from "next-intl";

import { cn } from "@repo/ui/lib/utils";

import { dayDate, TIME_ZONE } from "@/lib/conference";

export interface DayStripDay {
  date: string;
  pips: readonly AgendaKind[];
}

export interface DayStripProps {
  days: DayStripDay[];
  activeIndex: number;
  onSelect: (index: number) => void;
}

export function DayStrip({ days, activeIndex, onSelect }: DayStripProps) {
  const t = useTranslations("agenda");
  const format = useFormatter();

  return (
    <div
      aria-label={t("dayStripLabel")}
      className="no-scrollbar flex gap-1.5 overflow-x-auto px-5 pt-3 pb-2"
    >
      {days.map((day, index) => {
        const date = dayDate(day.date);
        const active = index === activeIndex;
        return (
          <button
            key={day.date}
            type="button"
            onClick={() => onSelect(index)}
            aria-current={active ? "date" : undefined}
            className={cn(
              "min-w-[50px] flex-1 cursor-pointer rounded-[10px] border border-border px-1 pt-[7px] pb-1.5 text-center font-mono text-muted-foreground",
              "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary",
              active && "border-primary bg-accent-soft",
            )}
          >
            <div className="text-[9.5px] tracking-[0.1em] uppercase">
              {format.dateTime(date, { weekday: "short", timeZone: TIME_ZONE })}
            </div>
            <div className="text-base text-foreground">
              {format.dateTime(date, { day: "numeric", timeZone: TIME_ZONE })}
            </div>
            <div
              data-slot="day-pips"
              className="mt-[3px] flex h-[5px] justify-center gap-[3px]"
            >
              {day.pips.map((kind, pip) => (
                <i
                  key={pip}
                  className={cn(
                    "h-1 w-1 rounded-full",
                    kind === "surprise" ? "bg-surprise" : "bg-primary",
                  )}
                />
              ))}
            </div>
          </button>
        );
      })}
    </div>
  );
}
