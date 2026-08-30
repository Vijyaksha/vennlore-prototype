// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import { DayStrip } from "../../components/day-strip";
import { renderWithIntl } from "./intl";

const days = [
  { date: "2026-03-15", pips: [] },
  { date: "2026-03-16", pips: ["surprise"] },
  { date: "2026-03-17", pips: [] },
  { date: "2026-03-18", pips: ["surprise", "surprise"] },
  { date: "2026-03-19", pips: ["core", "surprise", "mine"] },
  { date: "2026-03-20", pips: ["surprise"] },
] as const;

describe("DayStrip", () => {
  test("renders all six conference days Sun 15 through Fri 20", () => {
    renderWithIntl(
      <DayStrip days={[...days]} activeIndex={3} onSelect={() => {}} />,
    );

    expect(screen.getByText("Sun")).toBeInTheDocument();
    expect(screen.getByText("15")).toBeInTheDocument();
    expect(screen.getByText("Fri")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
    expect(screen.getAllByRole("button")).toHaveLength(6);
  });

  test("marks the active day and reports clicks", () => {
    const onSelect = vi.fn();
    renderWithIntl(
      <DayStrip days={[...days]} activeIndex={3} onSelect={onSelect} />,
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons[3]).toHaveAttribute("aria-current", "date");
    fireEvent.click(buttons[4]!);
    expect(onSelect).toHaveBeenCalledWith(4);
  });

  test("renders amber pips for surprises and accent pips for core and mine", () => {
    const { container } = renderWithIntl(
      <DayStrip days={[...days]} activeIndex={0} onSelect={() => {}} />,
    );

    const day19 = container.querySelectorAll('[data-slot="day-pips"]')[4]!;
    expect(day19.querySelectorAll(".bg-surprise")).toHaveLength(1);
    expect(day19.querySelectorAll(".bg-primary")).toHaveLength(2);
  });
});
