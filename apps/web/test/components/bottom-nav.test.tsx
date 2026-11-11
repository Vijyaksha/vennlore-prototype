// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

const path = vi.hoisted(() => ({ current: "/" }));
vi.mock("next/navigation", () => ({ usePathname: () => path.current }));

import { BottomNav } from "../../components/bottom-nav";
import { renderWithIntl } from "./intl";

describe("BottomNav", () => {
  test.each([
    ["/", "Picks"],
    ["/calendar", "Calendar"],
    ["/search", "Search"],
    ["/themes", "Themes"],
  ])("on %s marks %s as the current page", (pathname, label) => {
    path.current = pathname;
    renderWithIntl(<BottomNav />);
    expect(screen.getByRole("link", { name: label })).toHaveAttribute("aria-current", "page");
    expect(screen.getAllByRole("link").filter((l) => l.getAttribute("aria-current") === "page")).toHaveLength(1);
    expect(screen.getByRole("link", { name: "Search" })).toHaveAttribute("href", "/search");
    expect(screen.getByRole("link", { name: "Themes" })).toHaveAttribute("href", "/themes");
  });
});
