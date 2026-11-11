"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import type { Theme } from "@repo/contracts";
import { Badge } from "@repo/ui/components/badge";
import { Card } from "@repo/ui/components/card";

import { paperSource } from "@/lib/paper";

/** One research theme: concepts that talks and papers use together. */
export function ThemeCard({ theme }: { theme: Theme }) {
  const t = useTranslations("themes");
  const [open, setOpen] = useState(false);
  const papers = theme.talks.filter((x) => paperSource(x.type) !== null).length;

  return (
    <Card className="flex flex-col gap-3 rounded-lg border border-border bg-card px-[18px] py-4 ring-0">
      <h3 className="text-[17px] leading-snug font-semibold text-card-foreground">{theme.title}</h3>
      {theme.summary !== "" && (
        <p className="font-serif text-[14px] leading-[1.5] text-muted-foreground">{theme.summary}</p>
      )}
      <div role="group" aria-label={t("concepts")} className="flex flex-wrap gap-1.5">
        {theme.concepts.slice(0, 8).map((c) => (
          <Badge key={c} variant="outline" className="font-mono text-[10.5px] font-normal">{c}</Badge>
        ))}
      </div>
      <div className="flex items-center justify-between border-t border-border pt-2.5">
        <span className="font-mono text-[11.5px] text-muted-foreground">
          {t("counts", { talks: theme.talks.length - papers, papers })}
        </span>
        <button
          type="button"
          aria-expanded={open}
          onClick={() => setOpen((o) => !o)}
          className="text-[13px] font-medium text-primary"
        >
          {open ? t("hide") : t("show")}
        </button>
      </div>
      {open && (
        <ul className="flex flex-col gap-1.5">
          {theme.talks.map((x) => {
            const source = paperSource(x.type);
            return (
              <li key={x.id} className="flex items-baseline gap-2 text-[13px] leading-snug">
                <span className="shrink-0 font-mono text-[10.5px] text-faint">{source ?? t("talk")}</span>
                <span>{x.title}</span>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
