// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { buildNetwork, PicksGraph } from "../../components/picks-graph";
import { renderWithIntl } from "./intl";

type P = Parameters<typeof buildNetwork>[0][number];
const pick = (id: number, title: string, path: string[] | null, cross_domain = false): P =>
  ({ candidate_id: id, cross_domain, evidence: path ? { path } : {}, candidate: { title } }) as P;

const PICKS = [
  pick(1, "Exciton films", ["your talk", "method: transient photocurrent", "this talk"]),
  pick(2, "Membrane photocurrents", ["your talk", "\"Exciton films\"", "method: transient photocurrent", "this talk"], true),
  pick(3, "OLED cavities", ["your talk", "topic: excitons", "this talk"]),
  pick(4, "No path engine", null),
];

describe("buildNetwork", () => {
  test("merges shared concepts into one node and links you → concepts → picks", () => {
    const net = buildNetwork(PICKS);
    const labels = net.nodes.map((n) => n.label);
    expect(labels.filter((l) => l === "method: transient photocurrent")).toHaveLength(1);
    expect(net.nodes.filter((n) => n.kind === "you")).toHaveLength(1);
    expect(net.nodes.filter((n) => n.kind === "core" || n.kind === "unexpected").map((n) => n.label))
      .toEqual(["Exciton films", "Membrane photocurrents", "OLED cavities"]);
    expect(net.edges).toContainEqual({ from: "via:\"Exciton films\"", to: "concept:method: transient photocurrent" });
    expect(net.edges).toContainEqual({ from: "concept:method: transient photocurrent", to: "pick:2" });
  });
  test("is empty when no pick carries a path", () => {
    expect(buildNetwork([pick(4, "x", null)]).nodes).toHaveLength(0);
  });
});

describe("PicksGraph", () => {
  test("draws one node per merged entity and colours picks by kind", () => {
    renderWithIntl(<PicksGraph recommendations={PICKS} />);
    const img = screen.getByRole("img", { name: "Network of 3 picks linked through 3 concepts and talks" });
    expect(img.querySelectorAll("[data-slot='net-node']")).toHaveLength(7);
    expect(img.querySelectorAll("[data-kind='unexpected']")).toHaveLength(1);
  });
  test("renders nothing for engines without graph paths", () => {
    const { container } = renderWithIntl(<PicksGraph recommendations={[pick(4, "x", null)]} />);
    expect(container).toBeEmptyDOMElement();
  });
});
