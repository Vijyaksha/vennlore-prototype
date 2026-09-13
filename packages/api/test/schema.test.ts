import { getTableColumns } from "drizzle-orm";
import { describe, expect, test } from "vitest";

import { RecommendationSchema, RunSchema, TalkSchema } from "@repo/contracts";

import { recommendations, runs, talks } from "../src/db/schema";

const sqlNames = (table: Parameters<typeof getTableColumns>[0]) =>
  Object.values(getTableColumns(table))
    .map((c) => c.name)
    .sort();

describe("store schema is derived from the contract", () => {
  test("talks has exactly the 25 Talk fields", () => {
    expect(sqlNames(talks)).toEqual(Object.keys(TalkSchema.shape).sort());
  });
  test("recommendations has exactly the 13 Recommendation fields", () => {
    expect(sqlNames(recommendations)).toEqual(
      Object.keys(RecommendationSchema.shape).sort(),
    );
  });
  test("runs has exactly the Run fields", () => {
    expect(sqlNames(runs)).toEqual(Object.keys(RunSchema.shape).sort());
  });
});
