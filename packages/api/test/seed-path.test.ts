import { describe, expect, test } from "vitest";

import { resolveSeedPath } from "../src/db/seed-path";

describe("resolveSeedPath", () => {
  test("uses SEED_PATH when set", () => {
    expect(resolveSeedPath({ SEED_PATH: "/tmp/x.json" }, "/default.json")).toBe(
      "/tmp/x.json",
    );
  });

  test("falls back to the default when unset or blank", () => {
    expect(resolveSeedPath({}, "/default.json")).toBe("/default.json");
    expect(resolveSeedPath({ SEED_PATH: "  " }, "/default.json")).toBe(
      "/default.json",
    );
  });
});
