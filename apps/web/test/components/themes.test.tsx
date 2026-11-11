// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { fireEvent, screen, within } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import type { Theme } from "@repo/contracts";

import { AskBox } from "../../components/ask-box";
import { ThemeCard } from "../../components/theme-card";
import { renderWithIntl } from "./intl";

const THEME: Theme = {
  id: "T1", title: "Light-driven charge transport", summary: "Talks that read out charge with light.",
  concepts: ["transient photocurrent", "excitons"],
  talks: [
    { id: 2802, title: "Memristive DNA devices", type: "Oral-In-person" },
    { id: 1600000000, title: "GNNs for excitons", type: "preprint:arxiv" },
  ],
};

describe("ThemeCard", () => {
  test("shows title, summary, concepts and counts talks and papers separately", () => {
    renderWithIntl(<ThemeCard theme={THEME} />);
    expect(screen.getByRole("heading", { name: "Light-driven charge transport" })).toBeInTheDocument();
    expect(screen.getByText("Talks that read out charge with light.")).toBeInTheDocument();
    const concepts = screen.getByRole("group", { name: "Concepts" });
    expect(within(concepts).getByText("excitons")).toBeInTheDocument();
    expect(screen.getByText("1 talk · 1 paper")).toBeInTheDocument();
  });
  test("lists its talks and papers on demand, papers flagged by archive", () => {
    renderWithIntl(<ThemeCard theme={THEME} />);
    fireEvent.click(screen.getByRole("button", { name: "Show talks and papers" }));
    const list = screen.getByRole("list");
    expect(within(list).getByText("Memristive DNA devices")).toBeInTheDocument();
    expect(within(list).getByText("arXiv")).toBeInTheDocument();
  });
});

describe("AskBox", () => {
  test("asks once a question is typed", () => {
    const onAsk = vi.fn();
    renderWithIntl(<AskBox pending={false} error={null} onAsk={onAsk} />);
    const button = screen.getByRole("button", { name: "Ask" });
    expect(button).toBeDisabled();
    fireEvent.change(screen.getByRole("textbox", { name: "Ask the conference" }),
      { target: { value: "Which themes combine AI and physics?" } });
    fireEvent.click(button);
    expect(onAsk).toHaveBeenCalledWith("Which themes combine AI and physics?");
  });
  test("shows errors", () => {
    renderWithIntl(<AskBox pending={false} error="down" onAsk={() => {}} />);
    expect(screen.getByRole("alert")).toHaveTextContent("down");
  });
});
