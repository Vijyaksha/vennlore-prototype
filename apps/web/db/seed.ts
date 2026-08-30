import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { sql } from "drizzle-orm";

import { getDb } from "./index";
import { locations, recommendations, talks } from "./schema";
import {
  toLocationInsert,
  toRecommendationInsert,
  toSeedFile,
  toTalkInsert,
} from "./transform";

const SEED_PATH = join(
  dirname(fileURLToPath(import.meta.url)),
  "../../../pipeline/out/app_seed.json",
);
const BATCH_SIZE = 500;

function excluded(columnName: string) {
  return sql.raw(`excluded."${columnName}"`);
}

function* batches<T>(rows: T[]): Generator<T[]> {
  for (let i = 0; i < rows.length; i += BATCH_SIZE) {
    yield rows.slice(i, i + BATCH_SIZE);
  }
}

async function main() {
  let raw: string;
  try {
    raw = readFileSync(SEED_PATH, "utf8");
  } catch {
    console.error(
      `Seed file not found at ${SEED_PATH} — run pipeline/scripts/export_app_seed.py first`,
    );
    process.exit(1);
  }
  const seed = toSeedFile(JSON.parse(raw));

  const talkRows = seed.talks.map(toTalkInsert);
  const locationRows = seed.locations.map(toLocationInsert);
  const recommendationRows = seed.recommendations.map(toRecommendationInsert);

  const db = getDb();

  for (const batch of batches(talkRows)) {
    await db
      .insert(talks)
      .values(batch)
      .onConflictDoUpdate({
        target: talks.id,
        set: {
          title: excluded("title"),
          sessionTitle: excluded("session_title"),
          units: excluded("units"),
          start: excluded("start"),
          end: excluded("end"),
          building: excluded("building"),
          room: excluded("room"),
          abstract: excluded("abstract"),
        },
      });
  }
  console.log(`Seeded ${talkRows.length} talks`);

  for (const batch of batches(locationRows)) {
    await db
      .insert(locations)
      .values(batch)
      .onConflictDoUpdate({
        target: locations.id,
        set: {
          building: excluded("building"),
          room: excluded("room"),
        },
      });
  }
  console.log(`Seeded ${locationRows.length} locations`);

  for (const batch of batches(recommendationRows)) {
    await db
      .insert(recommendations)
      .values(batch)
      .onConflictDoUpdate({
        target: [recommendations.forTalkId, recommendations.candidateId],
        set: {
          sameMethod: excluded("same_method"),
          specificity: excluded("specificity"),
          usageParallel: excluded("usage_parallel"),
          score: excluded("score"),
          match: excluded("is_match"),
          crossDomain: excluded("cross_domain"),
          why: excluded("why"),
          strongestParallel: excluded("strongest_parallel"),
        },
      });
  }
  console.log(`Seeded ${recommendationRows.length} recommendations`);

  process.exit(0);
}

main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
