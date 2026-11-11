"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import { cn } from "@repo/ui/lib/utils";

/** The graph path an engine recorded for a pick (evidence.path), when it has one. */
export function pathFromEvidence(evidence: Record<string, unknown>): string[] | null {
  const path = evidence.path;
  return Array.isArray(path) && path.length >= 2 && path.every((p) => typeof p === "string")
    ? (path as string[])
    : null;
}

type Kind = "end" | "talk" | "concept";

const kindOf = (label: string, i: number, n: number): Kind =>
  i === 0 || i === n - 1 ? "end" : label.startsWith('"') ? "talk" : "concept";

const NODE_H = 30;
const GAP = 20;
const WIDTH = 280;
const clip = (s: string, n = 40) => (s.length > n ? `${s.slice(0, n - 1)}…` : s);

/** "How we found this": the pick's graph path drawn as linked nodes. */
export function PickPath({ path }: { path: string[] }) {
  const t = useTranslations("picks");
  const [open, setOpen] = useState(false);
  const height = path.length * NODE_H + (path.length - 1) * GAP;

  return (
    <div className="flex flex-col gap-2">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="self-start font-mono text-[11px] text-muted-foreground underline-offset-2 hover:text-primary hover:underline"
      >
        {t("howFound")}
      </button>
      {open && (
        <svg
          role="img"
          aria-label={t("pathLabel", { path: path.join(" → ") })}
          viewBox={`0 0 ${WIDTH} ${height}`}
          className="w-full"
        >
          {path.map((label, i) => {
            const kind = kindOf(label, i, path.length);
            const y = i * (NODE_H + GAP);
            return (
              <g key={i}>
                {i > 0 && (
                  <line
                    data-slot="path-edge"
                    x1={WIDTH / 2}
                    x2={WIDTH / 2}
                    y1={y - GAP + 2}
                    y2={y - 3}
                    className="stroke-border"
                    strokeWidth={1.5}
                    markerEnd="url(#pick-path-arrow)"
                  />
                )}
                <g data-slot="path-node" data-kind={kind}>
                  <title>{label}</title>
                  <rect
                    x={1}
                    y={y}
                    width={WIDTH - 2}
                    height={NODE_H}
                    rx={kind === "concept" ? 15 : 7}
                    className={cn(
                      kind === "concept" && "fill-accent-soft stroke-primary",
                      kind === "talk" && "fill-card stroke-border",
                      kind === "end" && "fill-muted stroke-border",
                    )}
                  />
                  <text
                    x={WIDTH / 2}
                    y={y + NODE_H / 2}
                    textAnchor="middle"
                    dominantBaseline="central"
                    className="fill-foreground font-mono text-[11px]"
                  >
                    {clip(label)}
                  </text>
                </g>
              </g>
            );
          })}
          <defs>
            <marker id="pick-path-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M0,0 L8,4 L0,8 z" className="fill-border" />
            </marker>
          </defs>
        </svg>
      )}
    </div>
  );
}
