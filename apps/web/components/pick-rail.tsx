"use client";

import { useTranslations } from "next-intl";
import { useRef, useState } from "react";

import { cn } from "@repo/ui/lib/utils";

import { EmptySlot } from "./empty-slot";
import { PickCard, type Anchor, type Pick } from "./pick-card";

const CORE_MAX = 2;
const UNEXPECTED_MAX = 3;
const RAIL_GAP = 14;

export interface PickRailProps {
  anchors: Anchor[];
  recommendations: Pick[];
}

const byScore = (a: Pick, b: Pick) =>
  b.score - a.score || a.candidateId - b.candidateId;

/** One pick per candidate: a talk matched under several anchors keeps its
 *  best-scoring match (the first one on ties). */
function mergeByCandidate(recommendations: Pick[]): Pick[] {
  const best = new Map<number, Pick>();
  for (const pick of recommendations) {
    const prev = best.get(pick.candidateId);
    if (prev === undefined || pick.score > prev.score) {
      best.set(pick.candidateId, pick);
    }
  }
  return [...best.values()].sort(byScore);
}

export function PickRail({ anchors, recommendations }: PickRailProps) {
  const t = useTranslations("picks");
  const railRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(0);

  const merged = mergeByCandidate(recommendations);
  const keptCore = merged.filter((pick) => !pick.crossDomain).slice(0, CORE_MAX);
  const keptUnexpected = merged
    .filter((pick) => pick.crossDomain)
    .slice(0, UNEXPECTED_MAX);
  const picks = [...keptCore, ...keptUnexpected].sort(byScore);
  const showSlot = picks.length > 0 && keptCore.length < CORE_MAX;
  const count = picks.length + (showSlot ? 1 : 0);

  if (picks.length === 0) {
    return (
      <div className="mx-5 my-7 rounded-lg border border-dashed border-border px-4 py-9 text-center text-[13.5px] text-faint">
        {t("noMatches")}
      </div>
    );
  }

  const onScroll = () => {
    const rail = railRef.current;
    const first = rail?.firstElementChild;
    if (rail === null || !(first instanceof HTMLElement) || first.offsetWidth === 0) {
      return;
    }
    const index = Math.round(rail.scrollLeft / (first.offsetWidth + RAIL_GAP));
    setActive(Math.min(Math.max(index, 0), count - 1));
  };

  return (
    <>
      <div
        ref={railRef}
        onScroll={onScroll}
        aria-label={t("railLabel")}
        className="no-scrollbar grid snap-x snap-mandatory auto-cols-[min(76vw,310px)] grid-flow-col gap-3.5 overflow-x-auto px-5 pt-[18px] pb-3.5"
      >
        {picks.map((pick) => (
          <PickCard key={pick.candidateId} pick={pick} anchors={anchors} />
        ))}
        {showSlot && <EmptySlot hasCore={keptCore.length > 0} />}
      </div>
      <div aria-hidden="true" className="flex justify-center gap-1.5 pt-1 pb-2.5">
        {Array.from({ length: count }, (_, index) => (
          <span
            key={index}
            data-slot="rail-dot"
            className={cn(
              "h-1.5 w-1.5 rounded-full",
              index === active ? "bg-primary" : "bg-border",
            )}
          />
        ))}
      </div>
    </>
  );
}
