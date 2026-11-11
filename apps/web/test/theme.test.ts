import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const css = readFileSync(
  fileURLToPath(new URL("../app/globals.css", import.meta.url)),
  "utf8",
);

/** The first top-level `:root { … }` block: the palette every visitor gets by default. */
function defaultRoot(): string {
  const match = css.match(/^:root\s*\{([^}]*)\}/m);
  if (!match) throw new Error("no bare :root block in globals.css");
  return match[1] ?? "";
}

describe("Kindred theme", () => {
  it("is light (white) by default, whatever the system setting", () => {
    expect(defaultRoot()).toMatch(/--background:\s*#ffffff;/);
    expect(defaultRoot()).toMatch(/--card:\s*#ffffff;/);
    expect(css).toMatch(/html\s*\{\s*color-scheme:\s*light;/);
  });

  it("does not switch to dark from the system preference", () => {
    expect(css).not.toMatch(/prefers-color-scheme:\s*dark/);
    expect(css).not.toMatch(/prefers-color-scheme:\s*light/);
  });

  it("keeps the opt-in .dark class for a dark view", () => {
    expect(css).toMatch(/\.dark\s*\{[^}]*--background:\s*#0e0b10;/);
  });
});
