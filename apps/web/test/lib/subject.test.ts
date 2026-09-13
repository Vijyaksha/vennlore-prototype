import { afterEach, describe, expect, test, vi } from "vitest";

import { subjectFromEnv } from "../../lib/conference";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("subjectFromEnv", () => {
  test("defaults to the seeded anchor talk when nothing is set", () => {
    expect(subjectFromEnv({})).toEqual({ talkId: 0 });
  });

  test("uses the presenter when only the presenter id is set", () => {
    expect(subjectFromEnv({ presenterId: "42" })).toEqual({ presenterId: 42 });
  });

  test("uses the anchor talk when only the talk id is set", () => {
    expect(subjectFromEnv({ anchorTalkId: "2802" })).toEqual({ talkId: 2802 });
  });

  test("trims surrounding whitespace", () => {
    expect(subjectFromEnv({ presenterId: " 42 " })).toEqual({ presenterId: 42 });
    expect(subjectFromEnv({ anchorTalkId: " 7 " })).toEqual({ talkId: 7 });
  });

  test("builds an object with exactly one key", () => {
    expect(Object.keys(subjectFromEnv({ presenterId: "42" }))).toEqual([
      "presenterId",
    ]);
    expect(Object.keys(subjectFromEnv({ anchorTalkId: "7" }))).toEqual([
      "talkId",
    ]);
  });

  test("presenter wins when both are set, and says so", () => {
    const warn = vi.fn();
    expect(
      subjectFromEnv({ presenterId: "42", anchorTalkId: "7" }, warn),
    ).toEqual({ presenterId: 42 });
    expect(warn).toHaveBeenCalledOnce();
    expect(warn.mock.calls[0]![0]).toMatch(/NEXT_PUBLIC_ANCHOR_TALK_ID.*ignored/);
  });

  test.each(["", "   "])("an empty presenter id %j counts as unset", (presenterId) => {
    const warn = vi.fn();
    expect(subjectFromEnv({ presenterId }, warn)).toEqual({ talkId: 0 });
    expect(subjectFromEnv({ presenterId, anchorTalkId: "7" }, warn)).toEqual({
      talkId: 7,
    });
    expect(warn).not.toHaveBeenCalled();
  });

  test.each(["", "   "])("an empty talk id %j counts as unset", (anchorTalkId) => {
    expect(subjectFromEnv({ anchorTalkId })).toEqual({ talkId: 0 });
  });

  test.each(["abc", "1.5", "0", "-3", "42abc"])(
    "a malformed presenter id %j throws naming the variable and value",
    (presenterId) => {
      expect(() => subjectFromEnv({ presenterId })).toThrow(
        `NEXT_PUBLIC_PRESENTER_ID=${JSON.stringify(presenterId)}`,
      );
    },
  );

  test.each(["abc", "2.5", "-1"])(
    "a malformed talk id %j throws naming the variable and value",
    (anchorTalkId) => {
      expect(() => subjectFromEnv({ anchorTalkId })).toThrow(
        `NEXT_PUBLIC_ANCHOR_TALK_ID=${JSON.stringify(anchorTalkId)}`,
      );
    },
  );

  test("a malformed presenter id throws even when the talk id is valid", () => {
    expect(() =>
      subjectFromEnv({ presenterId: "abc", anchorTalkId: "7" }),
    ).toThrow("NEXT_PUBLIC_PRESENTER_ID");
  });

  test("stays quiet for a well-formed single value", () => {
    const warn = vi.fn();
    subjectFromEnv({ presenterId: "42" }, warn);
    subjectFromEnv({ anchorTalkId: "0" }, warn);
    expect(warn).not.toHaveBeenCalled();
  });

  test("the default warning is silent in production builds", () => {
    vi.stubEnv("NODE_ENV", "production");
    const consoleWarn = vi.spyOn(console, "warn").mockImplementation(() => {});
    subjectFromEnv({ presenterId: "42", anchorTalkId: "7" });
    expect(consoleWarn).not.toHaveBeenCalled();
  });

  test("the default warning reaches the console outside production", () => {
    vi.stubEnv("NODE_ENV", "development");
    const consoleWarn = vi.spyOn(console, "warn").mockImplementation(() => {});
    subjectFromEnv({ presenterId: "42", anchorTalkId: "7" });
    expect(consoleWarn).toHaveBeenCalledOnce();
  });
});
