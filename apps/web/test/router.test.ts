import { describe, expect, test } from "vitest";

import { appRouter } from "../server/router";
import { createCallerFactory } from "../server/trpc";
import { type Repo, type RecRow, type TalkRow } from "../server/data";

const talk = (overrides: Partial<TalkRow> & { id: number }): TalkRow => ({
  title: `Talk ${overrides.id}`,
  sessionTitle: null,
  units: [],
  start: null,
  end: null,
  building: null,
  room: null,
  abstract: "",
  ...overrides,
});

const rec = (
  candidate: TalkRow,
  overrides: Partial<RecRow> = {},
): RecRow & { talk: TalkRow } => ({
  forTalkId: 0,
  candidateId: candidate.id,
  sameMethod: 1,
  specificity: 1,
  usageParallel: 1,
  score: 3,
  match: true,
  crossDomain: false,
  why: "shared method",
  strongestParallel: "same probe",
  talk: candidate,
  ...overrides,
});

// Real GPS 2026 values: 2802 (Bluebird 3C), 12342 (Exhibit Hall D, E & F,
// Level 2), 12772 (Meeting Room 708/710); anchor talk 0 has no times.
const anchor = talk({ id: 0, title: "Anchor talk on porphyrin nanorods" });
const bluebird = talk({
  id: 2802,
  title: "Bluebird talk",
  sessionTitle: "Organic Electronics",
  units: ["DPOLY"],
  start: new Date("2026-03-19T15:12:00.000Z"),
  end: new Date("2026-03-19T15:24:00.000Z"),
  building: "Convention Center",
  room: "Bluebird 3C",
});
const exhibitHall = talk({
  id: 12342,
  title: "Exhibit hall talk",
  start: new Date("2026-03-19T16:00:00.000Z"),
  end: new Date("2026-03-19T16:12:00.000Z"),
  building: "Convention Center",
  room: "Exhibit Hall D, E & F, Level 2",
});
const meetingRoom = talk({
  id: 12772,
  title: "Meeting room talk",
  start: new Date("2026-03-18T19:24:00.000Z"),
  end: new Date("2026-03-18T19:36:00.000Z"),
  building: "Convention Center",
  room: "Meeting Room 708/710",
});
const untimed = talk({ id: 9001, title: "Untimed poster" });
// 05:30 UTC on 03-19 is 23:30 on 03-18 in America/Denver (MDT, UTC-6).
const lateNight = talk({
  id: 9002,
  title: "Late night talk",
  start: new Date("2026-03-19T05:30:00.000Z"),
  end: new Date("2026-03-19T05:42:00.000Z"),
  building: "Hyatt Regency",
  room: "Capitol 1",
});

// Same score as exhibitHall (5) but a lower candidate id: pins the tiebreak.
const tiedPoster = talk({ id: 100, title: "Tied-score poster" });

const allTalks = [
  anchor,
  bluebird,
  exhibitHall,
  meetingRoom,
  untimed,
  lateNight,
  tiedPoster,
];
const allRecs = [
  rec(bluebird, { score: 6 }),
  rec(exhibitHall, { score: 5 }),
  rec(tiedPoster, { score: 5 }),
  rec(untimed, { score: 4 }),
  rec(meetingRoom, { score: 6, crossDomain: true }),
  rec(lateNight, { score: 5, crossDomain: true }),
  rec(talk({ id: 7777, title: "Rejected candidate" }), { score: 9, match: false }),
  rec(exhibitHall, { forTalkId: 2802, score: 4 }),
];

function fakeRepo(): Repo {
  return {
    getTalk: (id) => Promise.resolve(allTalks.find((t) => t.id === id) ?? null),
    getMatches: (forTalkId) =>
      Promise.resolve(
        allRecs
          .filter((r) => r.forTalkId === forTalkId && r.match)
          .sort((a, b) => b.score - a.score || a.candidateId - b.candidateId),
      ),
  };
}

const caller = createCallerFactory(appRouter)({ repo: fakeRepo() });

describe("picks", () => {
  test("splits matches into core and unexpected by crossDomain, score desc", async () => {
    const result = await caller.picks({ talkId: 0 });

    expect(result.talk.id).toBe(0);
    expect(result.core.map((p) => p.candidateId)).toEqual([2802, 100, 12342, 9001]);
    expect(result.unexpected.map((p) => p.candidateId)).toEqual([12772, 9002]);
  });

  test("equal-score picks order by candidateId ascending", async () => {
    const result = await caller.picks({ talkId: 0 });
    const fives = result.core.filter((p) => p.score === 5).map((p) => p.candidateId);
    expect(fives).toEqual([100, 12342]);
  });

  test("excludes non-match rows", async () => {
    const result = await caller.picks({ talkId: 0 });
    const ids = [...result.core, ...result.unexpected].map((p) => p.candidateId);
    expect(ids).not.toContain(7777);
  });

  test("maps pick fields from the recommendation and candidate talk", async () => {
    const result = await caller.picks({ talkId: 0 });
    expect(result.core[0]).toEqual({
      candidateId: 2802,
      title: "Bluebird talk",
      sessionTitle: "Organic Electronics",
      units: ["DPOLY"],
      start: new Date("2026-03-19T15:12:00.000Z"),
      end: new Date("2026-03-19T15:24:00.000Z"),
      building: "Convention Center",
      room: "Bluebird 3C",
      score: 6,
      sameMethod: 1,
      specificity: 1,
      usageParallel: 1,
      why: "shared method",
      strongestParallel: "same probe",
      crossDomain: false,
    });
  });

  test("throws NOT_FOUND for an unknown talk", async () => {
    await expect(caller.picks({ talkId: 424242 })).rejects.toThrow(/not found/i);
  });
});

describe("agenda", () => {
  test("groups items by Denver-local date, sorted by start", async () => {
    const result = await caller.agenda({ talkId: 0 });

    expect(result.days.map((d) => d.date)).toEqual(["2026-03-18", "2026-03-19"]);
    expect(result.days[0]?.items.map((i) => i.id)).toEqual([12772, 9002]);
    expect(result.days[1]?.items.map((i) => i.id)).toEqual([2802, 12342]);
  });

  test("puts a UTC time after midnight on the previous Denver day", async () => {
    const result = await caller.agenda({ talkId: 0 });
    const day18 = result.days.find((d) => d.date === "2026-03-18");
    expect(day18?.items.map((i) => i.id)).toContain(9002);
  });

  test("excludes untimed picks and the untimed claimed talk", async () => {
    const result = await caller.agenda({ talkId: 0 });
    const ids = result.days.flatMap((d) => d.items.map((i) => i.id));
    expect(ids).not.toContain(9001);
    expect(ids).not.toContain(0);
  });

  test("first item of a day has no transit, later items carry the connection", async () => {
    const result = await caller.agenda({ talkId: 0 });
    const day19 = result.days.find((d) => d.date === "2026-03-19");

    expect(day19?.items[0]?.transit).toBeNull();
    // 15:24Z end to 16:00Z start = 36 min gap; Bluebird 3C to Exhibit Hall = 15.
    expect(day19?.items[1]?.transit).toEqual({ walk: 15, slack: 21, tight: false });
  });

  test("includes the claimed talk itself when it has a start time", async () => {
    const result = await caller.agenda({ talkId: 2802 });
    const ids = result.days.flatMap((d) => d.items.map((i) => i.id));
    expect(ids).toEqual(expect.arrayContaining([2802, 12342]));
  });
});
