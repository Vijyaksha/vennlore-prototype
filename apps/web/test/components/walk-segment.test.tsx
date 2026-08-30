// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { WalkSegment } from "../../components/walk-segment";
import { renderWithIntl } from "./intl";

describe("WalkSegment", () => {
  test("renders the dotted route with walk minutes and destination room", () => {
    const { container } = renderWithIntl(
      <WalkSegment walk={25} slack={20} tight={false} room="Exhibit Hall A" />,
    );

    expect(screen.getByText("25 min walk · Exhibit Hall A")).toBeInTheDocument();
    expect(container.querySelector(".route-dots")).not.toBeNull();
  });

  test("tight connection turns amber and shows minutes to spare", () => {
    const { container } = renderWithIntl(
      <WalkSegment walk={25} slack={11} tight={true} room="Hall B2" />,
    );

    const sub = screen.getByText("tight connection — 11 min to spare");
    expect(sub).toHaveClass("text-surprise");
    expect(container.querySelector('[data-tight="true"]')).not.toBeNull();
  });

  test("a long non-tight gap shows the open-time line", () => {
    renderWithIntl(
      <WalkSegment walk={8} slack={78} tight={false} room="Hall B2" />,
    );

    expect(screen.getByText("then 1 h 18 min open")).toBeInTheDocument();
    expect(screen.queryByText(/tight connection/)).toBeNull();
  });

  test("a short non-tight gap shows minutes to spare on arrival", () => {
    renderWithIntl(
      <WalkSegment walk={12} slack={20} tight={false} room="Room 251A" />,
    );

    expect(screen.getByText("arrive with 20 min to spare")).toBeInTheDocument();
  });

  test("omits the room when it is unknown", () => {
    renderWithIntl(<WalkSegment walk={15} slack={30} tight={false} room={null} />);

    expect(screen.getByText("15 min walk")).toBeInTheDocument();
  });
});
