// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { AnchorHeading } from "../../components/anchor-heading";
import { renderWithIntl } from "./intl";

describe("AnchorHeading", () => {
  test("a single anchor is the heading as-is", () => {
    renderWithIntl(<AnchorHeading titles={["Porphyrin nanorods"]} />);

    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      /^Porphyrin nanorods$/,
    );
  });

  test("several anchors join with the localized separator", () => {
    renderWithIntl(
      <AnchorHeading
        titles={["Porphyrin nanorods", "Perovskite films", "Ionic gels"]}
      />,
    );

    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe(
      "Porphyrin nanorods · Perovskite films · Ionic gels",
    );
  });
});
