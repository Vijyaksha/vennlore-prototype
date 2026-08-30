import { describe, expect, test } from "vitest";

import { connection, walkMinutes, type Loc } from "../lib/walk";

const loc = (building: string | null, room: string | null): Loc => ({
  building,
  room,
});

describe("walkMinutes", () => {
  test("identical building and room is 5", () => {
    const a = loc("Convention Center", "Bluebird 2C");
    expect(walkMinutes(a, loc("Convention Center", "Bluebird 2C"))).toBe(5);
  });

  test("same cluster and floor is 10", () => {
    expect(
      walkMinutes(
        loc("Convention Center", "Bluebird 2A"),
        loc("Convention Center", "Bluebird 2C"),
      ),
    ).toBe(10);
  });

  test("same cluster, different floor is 15", () => {
    expect(
      walkMinutes(
        loc("Convention Center", "Bluebird 2A"),
        loc("Convention Center", "Bluebird 3C"),
      ),
    ).toBe(15);
  });

  test("different cluster in the same building is 15", () => {
    expect(
      walkMinutes(
        loc("Convention Center", "Bluebird 3C"),
        loc("Convention Center", "Exhibit Hall D, E & F, Level 2"),
      ),
    ).toBe(15);
  });

  test("slash room numbers use the first digit as floor: 708/710 vs 201 is 15", () => {
    expect(
      walkMinutes(
        loc("Convention Center", "Meeting Room 708/710"),
        loc("Convention Center", "Meeting Room 201"),
      ),
    ).toBe(15);
  });

  test("different buildings is 22", () => {
    expect(
      walkMinutes(
        loc("Convention Center", "Bluebird 2A"),
        loc("Hyatt Regency", "Capitol 1"),
      ),
    ).toBe(22);
  });

  test("Offsite on either side is 60", () => {
    const offsite = loc("Offsite", "Denver Museum of Nature and Science");
    const inside = loc("Convention Center", "Bluebird 2A");
    expect(walkMinutes(inside, offsite)).toBe(60);
    expect(walkMinutes(offsite, inside)).toBe(60);
  });

  test("null building or room on either side is 15", () => {
    expect(walkMinutes(loc(null, null), loc("Convention Center", "Bluebird 2A"))).toBe(
      15,
    );
    expect(walkMinutes(loc("Convention Center", "Bluebird 2A"), loc(null, null))).toBe(
      15,
    );
    expect(
      walkMinutes(loc("Convention Center", null), loc("Convention Center", "Agate")),
    ).toBe(15);
  });

  test("same cluster with no digits in either room counts as same floor", () => {
    expect(
      walkMinutes(
        loc("Hyatt Regency", "Bellco Theatre A"),
        loc("Hyatt Regency", "Bellco Theatre B"),
      ),
    ).toBe(10);
  });

  test("Level suffix carries the floor: Exhibit Hall Level 2 rooms share floor 2", () => {
    expect(
      walkMinutes(
        loc("Convention Center", "Exhibit Hall D, E & F, Level 2"),
        loc("Convention Center", "Exhibit Hall A, Level 2"),
      ),
    ).toBe(10);
  });
});

describe("connection", () => {
  test("computes slack as gap minus walk", () => {
    expect(connection(36, 15)).toEqual({ walk: 15, slack: 21, tight: false });
  });

  test("flags slack under 15 as tight", () => {
    expect(connection(20, 10)).toEqual({ walk: 10, slack: 10, tight: true });
  });

  test("negative slack is tight", () => {
    expect(connection(10, 22)).toEqual({ walk: 22, slack: -12, tight: true });
  });
});
