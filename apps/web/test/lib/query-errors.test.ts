import { describe, expect, test } from "vitest";

import { isNotFound, retryUnlessNotFound, searchErrorKind } from "../../lib/query-errors";

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

  test("never retries BAD_REQUEST", () => {
    expect(retryUnlessNotFound(0, trpcError("BAD_REQUEST"))).toBe(false);
  });

  test("retries other errors once", () => {
    const error = trpcError("INTERNAL_SERVER_ERROR");
    expect(retryUnlessNotFound(0, error)).toBe(true);
    expect(retryUnlessNotFound(1, error)).toBe(false);
  });
});

describe("searchErrorKind", () => {
  test.each([
    ["SERVICE_UNAVAILABLE", "unavailable"],
    ["BAD_REQUEST", "bad_request"],
    ["BAD_GATEWAY", "failed"],
    ["INTERNAL_SERVER_ERROR", "failed"],
  ])("maps %s to %s", (c, kind) => {
    expect(searchErrorKind(trpcError(c))).toBe(kind);
  });
  test("a network error with no tRPC code is a failure", () => {
    expect(searchErrorKind(new Error("fetch failed"))).toBe("failed");
  });
});
