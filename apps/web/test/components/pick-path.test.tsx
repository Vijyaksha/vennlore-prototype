// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { PickPath, pathFromEvidence } from "../../components/pick-path";
import { renderWithIntl } from "./intl";

const PATH = ["your talk", "\"Exciton transport in films\"", "method: transient photocurrent", "this talk"];

describe("PickPath", () => {
  test("is collapsed until asked, then draws every node of the graph path", () => {
    renderWithIntl(<PickPath path={PATH} />);
    const toggle = screen.getByRole("button", { name: "How we found this" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("img")).toBeNull();
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    const graph = screen.getByRole("img", { name: /^Graph path: your talk → .* → this talk$/ });
    expect(graph.querySelectorAll("[data-slot='path-node']")).toHaveLength(4);
    expect(graph.querySelectorAll("[data-slot='path-edge']")).toHaveLength(3);
  });

  test("marks method and concept nodes so the bridge stands out", () => {
    renderWithIntl(<PickPath path={PATH} />);
    fireEvent.click(screen.getByRole("button", { name: "How we found this" }));
    const kinds = [...document.querySelectorAll("[data-slot='path-node']")].map((n) => n.getAttribute("data-kind"));
    expect(kinds).toEqual(["end", "talk", "concept", "end"]);
  });
});

describe("pathFromEvidence", () => {
  test("reads a string path from any engine's evidence, else null", () => {
    expect(pathFromEvidence({ path: PATH })).toEqual(PATH);
    expect(pathFromEvidence({ path: ["only one"] })).toBeNull();
    expect(pathFromEvidence({ path: [1, 2] })).toBeNull();
    expect(pathFromEvidence({ rubric_sum: 13 })).toBeNull();
  });
});
