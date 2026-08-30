"use client";

import { useTranslations } from "next-intl";

import { cn } from "@repo/ui/lib/utils";

function Walker() {
  return (
    <svg
      width="11"
      height="13"
      viewBox="0 0 11 13"
      fill="none"
      aria-hidden="true"
      className="flex-none"
    >
      <circle cx="6" cy="1.8" r="1.5" fill="currentColor" />
      <path
        d="M5.8 3.8 L4.6 7.2 L2.6 12 M4.6 7.2 L7 9 L7.6 12 M5.8 4.2 L8.6 5.6 M5 5.4 L2.8 6.6"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
    </svg>
  );
}

export interface WalkSegmentProps {
  walk: number;
  slack: number;
  tight: boolean;
  room: string | null;
}

export function WalkSegment({ walk, slack, tight, room }: WalkSegmentProps) {
  const t = useTranslations("agenda");

  const hours = Math.floor(slack / 60);
  const minutes = slack % 60;
  const sub = tight
    ? t("tight", { minutes: slack })
    : slack > 45
      ? hours > 0
        ? minutes > 0
          ? t("openBoth", { hours, minutes })
          : t("openHours", { hours })
        : t("openMinutes", { minutes })
      : t("spare", { minutes: slack });

  return (
    <div
      data-tight={tight}
      className={cn(
        "relative -mt-1 mb-2.5 flex min-h-[62px] flex-col justify-center gap-0.5 pl-[86px]",
        tight && "[--walk-dot:var(--color-surprise)]",
      )}
    >
      <span
        aria-hidden="true"
        className="route-dots absolute top-0.5 bottom-0.5 left-[63px]"
      />
      <div
        className={cn(
          "flex items-center gap-[7px] font-mono text-xs tabular-nums",
          tight ? "text-surprise" : "text-muted-foreground",
        )}
      >
        <Walker />
        <span>
          {room === null
            ? t("walk", { minutes: walk })
            : t("walkTo", { minutes: walk, room })}
        </span>
      </div>
      <div
        className={cn(
          "font-mono text-[10.5px]",
          tight ? "text-surprise" : "text-faint",
        )}
      >
        {sub}
      </div>
    </div>
  );
}
