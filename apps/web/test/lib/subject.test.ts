import { describe, expect, test, vi } from "vitest";

import { subjectFromEnv } from "../../lib/conference";

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

  test.each(["abc", "", "1.5", "0", "-3"])(
    "a malformed presenter id %j falls back to the default anchor",
    (presenterId) => {
      const warn = vi.fn();
      expect(subjectFromEnv({ presenterId }, warn)).toEqual({ talkId: 0 });
    },
  );

  test.each(["abc", "", "2.5", "-1"])(
    "a malformed talk id %j falls back to the default anchor",
    (anchorTalkId) => {
      const warn = vi.fn();
      expect(subjectFromEnv({ anchorTalkId }, warn)).toEqual({ talkId: 0 });
    },
  );

  test("warns about a malformed value", () => {
    const warn = vi.fn();
    subjectFromEnv({ presenterId: "abc" }, warn);
    expect(warn).toHaveBeenCalledOnce();
    expect(warn.mock.calls[0]![0]).toMatch(/NEXT_PUBLIC_PRESENTER_ID/);
  });

  test("stays quiet for a well-formed single value", () => {
    const warn = vi.fn();
    subjectFromEnv({ presenterId: "42" }, warn);
    subjectFromEnv({ anchorTalkId: "0" }, warn);
    expect(warn).not.toHaveBeenCalled();
  });
});
