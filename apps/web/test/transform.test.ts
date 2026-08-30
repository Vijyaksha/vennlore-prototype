import { describe, expect, test } from "vitest";

import {
  toLocationInsert,
  toRecommendationInsert,
  toSeedFile,
  toTalkInsert,
} from "../db/transform";

const seedTalk = {
  id: 7,
  title: "Photoconductivity of Self-Assembled Porphyrin Nanorods",
  session_title: "Organic Electronics",
  units: ["DPOLY", "DCMP"],
  start: "2026-03-19T15:12:00.000Z",
  end: "2026-03-19T15:24:00.000Z",
  building: "Convention Center",
  room: "Meeting Room 404",
  abstract: "The photoconductivity of nanorods is described.",
};

const seedRecommendation = {
  for_talk_id: 0,
  candidate_id: 1846,
  same_method: 1,
  specificity: 2,
  usage_parallel: 3,
  score: 6,
  match: true,
  cross_domain: false,
  why: "Shared pump-probe apparatus.",
  strongest_parallel: "Both use 488 nm excitation.",
};

const seedLocation = {
  id: 4109684556,
  building: "Convention Center",
  room: "Meeting Room 704",
};

describe("toTalkInsert", () => {
  test("maps seed fields to schema columns and parses ISO dates", () => {
    const row = toTalkInsert(seedTalk);

    expect(row).toEqual({
      id: 7,
      title: "Photoconductivity of Self-Assembled Porphyrin Nanorods",
      sessionTitle: "Organic Electronics",
      units: ["DPOLY", "DCMP"],
      start: new Date("2026-03-19T15:12:00.000Z"),
      end: new Date("2026-03-19T15:24:00.000Z"),
      building: "Convention Center",
      room: "Meeting Room 404",
      abstract: "The photoconductivity of nanorods is described.",
    });
    expect(row.start).toBeInstanceOf(Date);
    expect(row.start?.toISOString()).toBe("2026-03-19T15:12:00.000Z");
  });

  test("keeps null start/end/session_title/building/room as null", () => {
    const row = toTalkInsert({
      ...seedTalk,
      session_title: null,
      start: null,
      end: null,
      building: null,
      room: null,
    });

    expect(row.sessionTitle).toBeNull();
    expect(row.start).toBeNull();
    expect(row.end).toBeNull();
    expect(row.building).toBeNull();
    expect(row.room).toBeNull();
  });

  test("throws naming the talk id when title is missing", () => {
    expect(() => toTalkInsert({ ...seedTalk, title: "" })).toThrow(/talk 7/);
  });

  test("throws naming the talk id on an unparseable date", () => {
    expect(() => toTalkInsert({ ...seedTalk, start: "not-a-date" })).toThrow(
      /talk 7/,
    );
  });

  test("throws naming the talk id when id is missing", () => {
    const withoutId = Object.fromEntries(
      Object.entries(seedTalk).filter(([k]) => k !== "id"),
    );
    expect(() => toTalkInsert(withoutId)).toThrow(/talk/);
  });
});

describe("toRecommendationInsert", () => {
  test("maps seed fields to schema columns, including match booleans", () => {
    expect(toRecommendationInsert(seedRecommendation)).toEqual({
      forTalkId: 0,
      candidateId: 1846,
      sameMethod: 1,
      specificity: 2,
      usageParallel: 3,
      score: 6,
      match: true,
      crossDomain: false,
      why: "Shared pump-probe apparatus.",
      strongestParallel: "Both use 488 nm excitation.",
    });
  });

  test("defaults missing why/strongest_parallel to empty strings", () => {
    const row = toRecommendationInsert({
      ...seedRecommendation,
      why: undefined,
      strongest_parallel: undefined,
    });

    expect(row.why).toBe("");
    expect(row.strongestParallel).toBe("");
  });

  test("throws naming the pair when a score field is missing", () => {
    expect(() =>
      toRecommendationInsert({ ...seedRecommendation, score: undefined }),
    ).toThrow(/0.*1846/);
  });
});

describe("toSeedFile", () => {
  const validSeed = {
    talks: [seedTalk],
    locations: [seedLocation],
    recommendations: [seedRecommendation],
  };

  test("accepts a file with talks/locations/recommendations arrays", () => {
    expect(toSeedFile(validSeed)).toBe(validSeed);
  });

  test("throws naming the missing array", () => {
    expect(() => toSeedFile({ ...validSeed, talks: undefined })).toThrow(
      /seed file.*talks/,
    );
    expect(() => toSeedFile({ ...validSeed, locations: "nope" })).toThrow(
      /seed file.*locations/,
    );
    expect(() => toSeedFile({ ...validSeed, recommendations: null })).toThrow(
      /seed file.*recommendations/,
    );
  });

  test("throws on a non-object payload", () => {
    expect(() => toSeedFile(null)).toThrow(/seed file/);
    expect(() => toSeedFile([])).toThrow(/seed file/);
  });
});

describe("toLocationInsert", () => {
  test("maps seed fields and preserves ids beyond int32", () => {
    expect(toLocationInsert(seedLocation)).toEqual({
      id: 4109684556,
      building: "Convention Center",
      room: "Meeting Room 704",
    });
  });

  test("throws naming the location id when building is missing", () => {
    expect(() => toLocationInsert({ ...seedLocation, building: "" })).toThrow(
      /location 4109684556/,
    );
  });
});
