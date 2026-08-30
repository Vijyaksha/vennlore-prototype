"use client";

import { Fragment } from "react";
import { useTranslations } from "next-intl";

import { AgendaItem, type AgendaEntry } from "./agenda-item";
import { WalkSegment } from "./walk-segment";

export type { AgendaEntry, AgendaKind } from "./agenda-item";

export function Agenda({ items }: { items: AgendaEntry[] }) {
  const t = useTranslations("agenda");

  if (items.length === 0) {
    return (
      <div className="mx-5 my-7 rounded-lg border border-dashed border-border px-4 py-9 text-center text-[13.5px] text-faint">
        {t("emptyDay")}
      </div>
    );
  }

  return (
    <>
      <div className="px-5 pt-3.5">
        {items.map((item, index) => (
          <Fragment key={item.id}>
            {index > 0 && item.transit !== null && (
              <WalkSegment
                walk={item.transit.walk}
                slack={item.transit.slack}
                tight={item.transit.tight}
                room={item.room}
              />
            )}
            <AgendaItem item={item} />
          </Fragment>
        ))}
      </div>
      <div className="px-5 pt-2.5 pb-1 text-center font-mono text-[10px] tracking-[0.08em] text-faint uppercase">
        {t("disclaimer")}
      </div>
    </>
  );
}
