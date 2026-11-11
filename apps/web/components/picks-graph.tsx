"use client";

import { useTranslations } from "next-intl";

import type { Pick as PickRow } from "@repo/contracts";
import { cn } from "@repo/ui/lib/utils";

import { pathFromEvidence } from "./pick-path";

type Kind = "you" | "concept" | "talk" | "core" | "unexpected";
export interface NetNode { id: string; label: string; kind: Kind; col: number }
export interface Network { nodes: NetNode[]; edges: { from: string; to: string }[] }
type GraphPick = Pick<PickRow, "candidate_id" | "cross_domain" | "evidence"> & { candidate: { title: string } };

/** One network from every pick's graph path: you → concepts / bridging talks → picks.
 *  Shared concepts become one node, so the diagram shows how picks connect. */
export function buildNetwork(picks: GraphPick[]): Network {
  const nodes = new Map<string, NetNode>();
  const edges = new Map<string, { from: string; to: string }>();
  const add = (id: string, label: string, kind: Kind, col: number) => {
    const prev = nodes.get(id);
    nodes.set(id, prev ? { ...prev, col: Math.max(prev.col, col) } : { id, label, kind, col });
  };
  const routes: { chain: string[]; pick: GraphPick }[] = [];
  for (const p of picks) {
    const path = pathFromEvidence(p.evidence);
    if (path === null) continue;
    const chain = ["you"];
    path.slice(1, -1).forEach((label, i) => {
      const talk = label.startsWith('"');
      const id = `${talk ? "via" : "concept"}:${label}`;
      add(id, label, talk ? "talk" : "concept", i + 1);
      chain.push(id);
    });
    routes.push({ chain, pick: p });
  }
  if (routes.length === 0) return { nodes: [], edges: [] };
  add("you", "You", "you", 0);
  const last = Math.max(...[...nodes.values()].map((n) => n.col)) + 1;
  for (const { chain, pick } of routes) {
    const id = `pick:${pick.candidate_id}`;
    add(id, pick.candidate.title, pick.cross_domain ? "unexpected" : "core", last);
    [...chain, id].forEach((to, i, all) => {
      if (i === 0) return;
      const from = all[i - 1]!;
      edges.set(`${from}>${to}`, { from, to });
    });
  }
  return { nodes: [...nodes.values()], edges: [...edges.values()] };
}

const W = 960;
const NODE_W = 200;
const NODE_H = 30;
const ROW = 42;
const clip = (s: string, n = 30) => (s.length > n ? `${s.slice(0, n - 1)}…` : s);

/** The combined network of all picks, drawn in columns from you to the picks. */
export function PicksGraph({ recommendations }: { recommendations: GraphPick[] }) {
  const t = useTranslations("graph");
  const net = buildNetwork(recommendations);
  if (net.nodes.length === 0) return null;

  const cols = Math.max(...net.nodes.map((n) => n.col)) + 1;
  const byCol = Array.from({ length: cols }, (_, c) => net.nodes.filter((n) => n.col === c));
  const rows = Math.max(...byCol.map((c) => c.length));
  const height = rows * ROW + 12;
  const pos = new Map<string, { x: number; y: number }>();
  byCol.forEach((column, c) => {
    const x = cols === 1 ? 8 : 8 + (c * (W - NODE_W - 16)) / (cols - 1);
    const top = (height - column.length * ROW) / 2;
    column.forEach((n, r) => pos.set(n.id, { x, y: top + r * ROW + 6 }));
  });
  const picks = net.nodes.filter((n) => n.kind === "core" || n.kind === "unexpected").length;
  const middle = net.nodes.filter((n) => n.kind === "concept" || n.kind === "talk").length;

  return (
    <figure className="flex flex-col gap-2">
      <figcaption className="font-mono text-[11px] text-muted-foreground">{t("caption")}</figcaption>
      <div className="no-scrollbar overflow-x-auto rounded-lg border border-border bg-card p-2">
        <svg
          role="img"
          aria-label={t("label", { picks, middle })}
          viewBox={`0 0 ${W} ${height}`}
          className="min-w-[640px]"
        >
          {net.edges.map(({ from, to }) => {
            const a = pos.get(from)!;
            const b = pos.get(to)!;
            const x1 = a.x + NODE_W;
            const y1 = a.y + NODE_H / 2;
            const y2 = b.y + NODE_H / 2;
            const mid = (x1 + b.x) / 2;
            return (
              <path
                key={`${from}>${to}`}
                data-slot="net-edge"
                d={`M${x1},${y1} C${mid},${y1} ${mid},${y2} ${b.x},${y2}`}
                fill="none"
                strokeWidth={1.4}
                className={cn(to.startsWith("pick:") && net.nodes.find((n) => n.id === to)?.kind === "unexpected"
                  ? "stroke-surprise/60" : "stroke-border")}
              />
            );
          })}
          {net.nodes.map((n) => {
            const p = pos.get(n.id)!;
            return (
              <g key={n.id} data-slot="net-node" data-kind={n.kind}>
                <title>{n.label}</title>
                <rect
                  x={p.x}
                  y={p.y}
                  width={NODE_W}
                  height={NODE_H}
                  rx={n.kind === "concept" ? 15 : 7}
                  className={cn(
                    n.kind === "you" && "fill-primary stroke-primary",
                    n.kind === "concept" && "fill-accent-soft stroke-primary",
                    n.kind === "talk" && "fill-muted stroke-border",
                    n.kind === "core" && "fill-card stroke-primary",
                    n.kind === "unexpected" && "fill-surprise-soft stroke-surprise",
                  )}
                />
                <text
                  x={p.x + NODE_W / 2}
                  y={p.y + NODE_H / 2}
                  textAnchor="middle"
                  dominantBaseline="central"
                  className={cn("font-mono text-[11px]", n.kind === "you" ? "fill-primary-foreground" : "fill-foreground")}
                >
                  {clip(n.label)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </figure>
  );
}
