import { describe, expect, test } from "vitest";

import { isNotFound, retryUnlessNotFound } from "../../lib/query-errors";

const trpcError = (code: string) => ({ data: { code } });

describe("isNotFound", () => {
  test("recognises a tRPC NOT_FOUND error", () => {
    expect(isNotFound(trpcError("NOT_FOUND"))).toBe(true);
  });

  test.each([
    ["another code", trpcError("INTERNAL_SERVER_ERROR")],
    ["no data", { message: "network" }],
    ["null", null],
  ])("is false for %s", (_label, error) => {
    expect(isNotFound(error)).toBe(false);
  });
});

describe("retryUnlessNotFound", () => {
  test("never retries NOT_FOUND", () => {
    expect(retryUnlessNotFound(0, trpcError("NOT_FOUND"))).toBe(false);
  });

  test("retries other errors once", () => {
    const error = trpcError("INTERNAL_SERVER_ERROR");
    expect(retryUnlessNotFound(0, error)).toBe(true);
    expect(retryUnlessNotFound(1, error)).toBe(false);
  });
});
