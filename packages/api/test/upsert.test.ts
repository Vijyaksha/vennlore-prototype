import { PgDialect } from "drizzle-orm/pg-core";
import type { SQL } from "drizzle-orm";
import { describe, expect, test } from "vitest";

import { recommendations, runs, talks } from "../src/db/schema";
import { batches, excluded, updateSet } from "../src/db/upsert";

const render = (fragment: SQL) => new PgDialect().sqlToQuery(fragment).sql;

describe("excluded", () => {
  test("renders a quoted excluded column reference", () => {
    expect(render(excluded("session_topics"))).toBe(
      'excluded."session_topics"',
    );
  });
});

describe("updateSet (skip takes SQL column names)", () => {
  test("talks: the 24 non-id columns, keyed by the contract's field names", () => {
    const set = updateSet(talks, ["id"]);
    const keys = Object.keys(set);
    expect(keys).toHaveLength(24);
    expect(keys).not.toContain("id");
    expect(keys).toContain("external_id");
    expect(keys).toContain("session_topics");
    expect(keys).not.toContain("externalId");
    expect(keys).not.toContain("sessionTopics");
  });

  test("each value renders excluded.<sql name> of its own column", () => {
    const set = updateSet(talks, ["id"]);
    expect(render(set.session_topics!)).toBe('excluded."session_topics"');
    expect(render(set.external_id!)).toBe('excluded."external_id"');
    expect(render(set.end!)).toBe('excluded."end"');
  });

  test("recommendations: the 10 non-PK columns", () => {
    const set = updateSet(recommendations, [
      "engine_id",
      "for_talk_id",
      "candidate_id",
    ]);
    expect(Object.keys(set).sort()).toEqual(
      [
        "score",
        "rank",
        "match",
        "cross_domain",
        "why",
        "strongest_parallel",
        "shared_methods",
        "evidence",
        "run_id",
        "contract_version",
      ].sort(),
    );
    expect(render(set.contract_version!)).toBe('excluded."contract_version"');
  });

  test("runs: the 10 non-PK columns", () => {
    const set = updateSet(runs, ["run_id"]);
    expect(Object.keys(set)).toHaveLength(10);
    expect(Object.keys(set)).not.toContain("run_id");
  });
});

describe("batches", () => {
  test("splits 1001 rows into 500, 500 and 1", () => {
    const rows = Array.from({ length: 1001 }, (_, i) => i);
    expect([...batches(rows)].map((b) => b.length)).toEqual([500, 500, 1]);
  });
});
