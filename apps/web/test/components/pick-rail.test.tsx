// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

import { screen, within } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import type { Pick, Talk } from "@repo/contracts";

import { PickRail } from "../../components/pick-rail";
import { renderWithIntl } from "./intl";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(
    readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"),
  );

/** A contract Pick: every Recommendation field plus a full candidate Talk. */
const pick = ({
  candidate,
  ...overrides
}: Partial<Omit<Pick, "candidate">> & {
  candidate_id: number;
  candidate?: Partial<Talk>;
}): Pick => ({
  ...(fixture("recommendation") as Omit<Pick, "candidate">),
  for_talk_id: 0,
  score: 0.6,
  cross_domain: true,
  why: "shared measurement loop",
  shared_methods: [],
  ...overrides,
  candidate: {
    ...(fixture("talk") as Talk),
    id: overrides.candidate_id,
    title: `Pick ${overrides.candidate_id}`,
    session_title: "Some Session",
    units: ["DLS"],
    start: "2026-03-18T19:24:00.000Z",
    ...candidate,
  },
});

const core = (id: number, score = 0.6) =>
  pick({
    candidate_id: id,
    score,
    cross_domain: false,
    candidate: { units: ["DPOLY"] },
  });
const unexpected = (id: number, score = 0.6) => pick({ candidate_id: id, score });

const ONE_ANCHOR = [{ id: 0, title: "Porphyrin nanorods" }];
const TWO_ANCHORS = [
  { id: 0, title: "Porphyrin nanorods" },
  { id: 1, title: "Ultrafast carrier dynamics in perovskite films" },
];

function Rail({
  core: c = [],
  unexpected: u = [],
  anchors = ONE_ANCHOR,
}: {
  core?: Pick[];
  unexpected?: Pick[];
  anchors?: { id: number; title: string }[];
}) {
  return <PickRail anchors={anchors} recommendations={[...c, ...u]} />;
}

describe("PickRail", () => {
  test("renders every kept pick as a card with badge, score and why", () => {
    renderWithIntl(
      <Rail
        core={[core(1, 0.8)]}
        unexpected={[unexpected(2, 0.7), unexpected(3, 0.5)]}
      />,
    );

    expect(screen.getByText("Pick 1")).toBeInTheDocument();
    expect(screen.getByText("Pick 2")).toBeInTheDocument();
    expect(screen.getByText("Pick 3")).toBeInTheDocument();
    expect(screen.getByText("DPOLY · core")).toBeInTheDocument();
    expect(screen.getAllByText("DLS · unexpected")).toHaveLength(2);
    expect(screen.getByText("80%")).toBeInTheDocument();
  });

  test("caps unexpected picks at 3 and core picks at 2", () => {
    renderWithIntl(
      <Rail
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
      <Rail
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
      <Rail core={[]} unexpected={[unexpected(2), unexpected(3)]} />,
    );

    expect(screen.getByText("No core match cleared the bar.")).toBeInTheDocument();
  });

  test("with no matches at all shows the rail-level empty state", () => {
    renderWithIntl(<Rail />);

    expect(
      screen.getByText("No matches cleared the bar for this talk."),
    ).toBeInTheDocument();
    expect(screen.queryByText("No core match cleared the bar.")).toBeNull();
  });

  test("renders one position dot per rail item, including the empty slot", () => {
    const { container } = renderWithIntl(
      <Rail
        core={[core(1)]}
        unexpected={[unexpected(2), unexpected(3), unexpected(4)]}
      />,
    );

    expect(container.querySelectorAll('[data-slot="rail-dot"]')).toHaveLength(5);
  });

  test("formats the card time in Denver local time and links to that calendar day", () => {
    renderWithIntl(<Rail core={[core(1)]} />);

    expect(screen.getByText("Wed 3/18 · 1:24 PM")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Calendar" })).toHaveAttribute(
      "href",
      "/calendar?date=2026-03-18",
    );
  });

  test("caps keep the highest-scoring picks of each kind", () => {
    renderWithIntl(
      <Rail
        core={[core(1, 0.3), core(2, 0.9), core(3, 0.7)]}
        unexpected={[
          unexpected(4, 0.2),
          unexpected(5, 0.8),
          unexpected(6, 0.6),
          unexpected(7, 0.5),
        ]}
      />,
    );

    expect(screen.queryByText("Pick 1")).toBeNull();
    expect(screen.queryByText("Pick 4")).toBeNull();
    expect(screen.getAllByText(/^Pick \d+$/).map((el) => el.textContent)).toEqual(
      ["Pick 2", "Pick 5", "Pick 3", "Pick 6", "Pick 7"],
    );
  });

  test("renders each shared method as a chip", () => {
    renderWithIntl(
      <Rail
        core={[
          pick({
            candidate_id: 1,
            cross_domain: false,
            shared_methods: ["transient photocurrent", "self-assembly"],
          }),
        ]}
      />,
    );

    const group = screen.getByRole("group", { name: "Shared methods" });
    expect(within(group).getByText("transient photocurrent")).toBeInTheDocument();
    expect(within(group).getByText("self-assembly")).toBeInTheDocument();
  });

  test("omits the shared-method group when there are none", () => {
    renderWithIntl(<Rail core={[core(1)]} />);

    expect(screen.queryByRole("group", { name: "Shared methods" })).toBeNull();
  });

  test("a single-anchor presenter sees no anchor chip", () => {
    renderWithIntl(<Rail core={[core(1)]} unexpected={[unexpected(2)]} />);

    expect(screen.queryByText(/for your talk on/)).toBeNull();
  });

  test("a multi-anchor presenter sees which of their talks each pick is for", () => {
    renderWithIntl(
      <Rail
        anchors={TWO_ANCHORS}
        core={[pick({ candidate_id: 1, cross_domain: false, for_talk_id: 0 })]}
        unexpected={[pick({ candidate_id: 2, for_talk_id: 1 })]}
      />,
    );

    expect(
      screen.getByText("for your talk on Porphyrin nanorods"),
    ).toBeInTheDocument();
    // The chip may be visually truncated; the full title stays reachable.
    expect(
      screen.getByText(
        "for your talk on Ultrafast carrier dynamics in perovskite films",
      ),
    ).toHaveAttribute(
      "title",
      "Ultrafast carrier dynamics in perovskite films",
    );
  });

  test("merges a candidate matched under two anchors, keeping its best score", () => {
    renderWithIntl(
      <Rail
        anchors={TWO_ANCHORS}
        unexpected={[
          pick({ candidate_id: 5, for_talk_id: 0, score: 0.4 }),
          pick({ candidate_id: 5, for_talk_id: 1, score: 0.9 }),
        ]}
      />,
    );

    expect(screen.getAllByText("Pick 5")).toHaveLength(1);
    expect(screen.getByText("90%")).toBeInTheDocument();
    expect(screen.queryByText("40%")).toBeNull();
    expect(
      screen.getByText(
        "for your talk on Ultrafast carrier dynamics in perovskite films",
      ),
    ).toBeInTheDocument();
  });

  test("a multi-anchor presenter with no matches reads in the plural", () => {
    renderWithIntl(<Rail anchors={TWO_ANCHORS} />);

    expect(
      screen.getByText("No matches cleared the bar for your talks."),
    ).toBeInTheDocument();
  });

  test("equal scores under two anchors keep the first match", () => {
    renderWithIntl(
      <Rail
        anchors={TWO_ANCHORS}
        unexpected={[
          pick({ candidate_id: 5, for_talk_id: 0, score: 0.5 }),
          pick({ candidate_id: 5, for_talk_id: 1, score: 0.5 }),
        ]}
      />,
    );

    expect(screen.getAllByText("Pick 5")).toHaveLength(1);
    expect(
      screen.getByText("for your talk on Porphyrin nanorods"),
    ).toBeInTheDocument();
    expect(screen.queryByText(/perovskite films/)).toBeNull();
  });

  test.each([
    [0, "0%"],
    [1, "100%"],
    [0.005, "1%"],
  ])("score %s renders as %s", (score, text) => {
    renderWithIntl(<Rail core={[core(1, score)]} />);

    expect(screen.getByText(text)).toBeInTheDocument();
  });
});
