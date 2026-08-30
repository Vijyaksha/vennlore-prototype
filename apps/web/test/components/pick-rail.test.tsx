// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import type { Pick } from "../../components/pick-card";
import { PickRail } from "../../components/pick-rail";
import { renderWithIntl } from "./intl";

const pick = (overrides: Partial<Pick> & { candidateId: number }): Pick => ({
  title: `Pick ${overrides.candidateId}`,
  sessionTitle: "Some Session",
  units: ["DLS"],
  start: "2026-03-18T19:24:00.000Z",
  score: 6,
  crossDomain: true,
  why: "shared measurement loop",
  ...overrides,
});

const core = (id: number, score = 6) =>
  pick({ candidateId: id, score, crossDomain: false, units: ["DPOLY"] });
const unexpected = (id: number, score = 6) => pick({ candidateId: id, score });

describe("PickRail", () => {
  test("renders every kept pick as a card with badge, score and why", () => {
    renderWithIntl(
      <PickRail
        talkId={0}
        core={[core(1, 11)]}
        unexpected={[unexpected(2, 7), unexpected(3, 5)]}
      />,
    );

    expect(screen.getByText("Pick 1")).toBeInTheDocument();
    expect(screen.getByText("Pick 2")).toBeInTheDocument();
    expect(screen.getByText("Pick 3")).toBeInTheDocument();
    expect(screen.getByText("DPOLY · core")).toBeInTheDocument();
    expect(screen.getAllByText("DLS · unexpected")).toHaveLength(2);
    expect(screen.getByText("11/15")).toBeInTheDocument();
  });

  test("caps unexpected picks at 3 and core picks at 2", () => {
    renderWithIntl(
      <PickRail
        talkId={0}
        core={[core(1), core(2), core(3)]}
        unexpected={[unexpected(4), unexpected(5), unexpected(6), unexpected(7)]}
      />,
    );

    expect(screen.queryByText("Pick 3")).toBeNull();
    expect(screen.queryByText("Pick 7")).toBeNull();
    expect(screen.getAllByText(/^Pick \d+$/)).toHaveLength(5);
  });

  test("with 1 core and 3 unexpected shows the honest empty second-core slot", () => {
    renderWithIntl(
      <PickRail
        talkId={0}
        core={[core(1)]}
        unexpected={[unexpected(2), unexpected(3), unexpected(4)]}
      />,
    );

    expect(
      screen.getByText("No second core match cleared the bar."),
    ).toBeInTheDocument();
  });

  test("with zero core matches shows the no-core slot", () => {
    renderWithIntl(
      <PickRail talkId={0} core={[]} unexpected={[unexpected(2), unexpected(3)]} />,
    );

    expect(screen.getByText("No core match cleared the bar.")).toBeInTheDocument();
  });

  test("with no matches at all shows the rail-level empty state", () => {
    renderWithIntl(<PickRail talkId={0} core={[]} unexpected={[]} />);

    expect(
      screen.getByText("No matches cleared the bar for this talk."),
    ).toBeInTheDocument();
    expect(screen.queryByText("No core match cleared the bar.")).toBeNull();
  });

  test("renders one position dot per rail item, including the empty slot", () => {
    const { container } = renderWithIntl(
      <PickRail
        talkId={0}
        core={[core(1)]}
        unexpected={[unexpected(2), unexpected(3), unexpected(4)]}
      />,
    );

    expect(container.querySelectorAll('[data-slot="rail-dot"]')).toHaveLength(5);
  });

  test("formats the card time in Denver local time and links to that calendar day", () => {
    renderWithIntl(<PickRail talkId={42} core={[core(1)]} unexpected={[]} />);

    expect(screen.getByText("Wed 3/18 · 1:24 PM")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Calendar" })).toHaveAttribute(
      "href",
      "/talk/42/calendar?date=2026-03-18",
    );
  });
});
