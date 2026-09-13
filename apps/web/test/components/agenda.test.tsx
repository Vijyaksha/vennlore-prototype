// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import type { AgendaItem } from "@repo/contracts";

import { Agenda } from "../../components/agenda";
import { renderWithIntl } from "./intl";

const entry = (
  overrides: Partial<AgendaItem> & { id: number },
): AgendaItem => ({
  title: `Talk ${overrides.id}`,
  session_title: "Some Session",
  start: "2026-03-19T15:12:00.000Z",
  end: "2026-03-19T15:24:00.000Z",
  building: "Convention Center",
  room: "Bluebird 3C",
  transit: null,
  kind: "surprise",
  units: ["DLS"],
  ...overrides,
});

describe("Agenda", () => {
  test("an empty day renders the dashed empty state", () => {
    renderWithIntl(<Agenda items={[]} />);

    expect(screen.getByText("No picks this day.")).toBeInTheDocument();
  });

  test("renders start and end on the time axis in Denver local time", () => {
    renderWithIntl(<Agenda items={[entry({ id: 1 })]} />);

    // 15:12Z / 15:24Z are 9:12 / 9:24 AM in Denver (MDT).
    expect(screen.getByText("9:12 AM")).toBeInTheDocument();
    expect(screen.getByText("9:24 AM")).toBeInTheDocument();
    expect(screen.getByText("Some Session")).toBeInTheDocument();
  });

  test("the user's own talk renders the outlined 'mine' variant", () => {
    const { container } = renderWithIntl(
      <Agenda
        items={[entry({ id: 1 }), entry({ id: 7, kind: "mine", units: [] })]}
      />,
    );

    expect(container.querySelector('[data-kind="mine"]')).not.toBeNull();
    expect(screen.getByText("YOUR TALK")).toBeInTheDocument();
    expect(screen.getByText("You're presenting")).toBeInTheDocument();
  });

  test("renders a walking segment between consecutive items, never before the first", () => {
    const { container } = renderWithIntl(
      <Agenda
        items={[
          entry({ id: 1 }),
          entry({
            id: 2,
            room: "Exhibit Hall A",
            transit: { walk: 25, slack: 11, tight: true },
          }),
        ]}
      />,
    );

    expect(screen.getByText("25 min walk · Exhibit Hall A")).toBeInTheDocument();
    expect(screen.getByText("tight connection — 11 min to spare")).toBeInTheDocument();
    expect(container.querySelectorAll('[data-tight]')).toHaveLength(1);
  });
});
