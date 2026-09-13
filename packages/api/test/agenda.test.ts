import { describe, expect, test } from "vitest";

import { groupByDenverDay } from "../src/agenda";

const item = (id: number, start: string | null, end: string | null, building = "Convention Center", room = "Bluebird 3C") =>
  ({ id, title: `T${id}`, sessionTitle: null, start: start ? new Date(start) : null, end: end ? new Date(end) : null, building, room });

describe("groupByDenverDay", () => {
  test("groups by Denver date, sorts by start, annotates transit after the first item", () => {
    const days = groupByDenverDay([
      item(2, "2026-03-19T16:00:00Z", "2026-03-19T16:12:00Z", "Convention Center", "Exhibit Hall D, E & F, Level 2"),
      item(1, "2026-03-19T15:12:00Z", "2026-03-19T15:24:00Z"),
      item(3, "2026-03-19T05:30:00Z", "2026-03-19T05:42:00Z", "Hyatt Regency", "Capitol 1"),
      item(4, null, null),
    ]);
    expect(days.map((d) => d.date)).toEqual(["2026-03-18", "2026-03-19"]);
    expect(days[1]?.items.map((i) => i.id)).toEqual([1, 2]);
    expect(days[1]?.items[0]?.transit).toBeNull();
    expect(days[1]?.items[1]?.transit).toEqual({ walk: 15, slack: 21, tight: false });
  });
});
