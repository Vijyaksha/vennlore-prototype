import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { getDb } from "./index";
import { locations, recommendations, runs, talks } from "./schema";
import { resolveSeedPath } from "./seed-path";
import {
  toLocationInsert,
  toRecommendationInsert,
  toRunInsert,
  toSeedFile,
  toTalkInsert,
} from "./transform";
import { batches, updateSet } from "./upsert";

const DEFAULT_SEED_PATH = join(
  dirname(fileURLToPath(import.meta.url)),
  "../../../../pipeline/out/app_seed.v2.json",
);

const SEED_PATH = resolveSeedPath(process.env, DEFAULT_SEED_PATH);

/** Idempotent upsert of the v2 contract seed: talks, locations, runs, then recommendations. */
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
  const runRows = seed.runs.map(toRunInsert);
  const recommendationRows = seed.recommendations.map(toRecommendationInsert);

  const db = getDb();

  for (const batch of batches(talkRows)) {
    await db
      .insert(talks)
      .values(batch)
      .onConflictDoUpdate({ target: talks.id, set: updateSet(talks, ["id"]) });
  }
  console.log(`Seeded ${talkRows.length} talks`);

  for (const batch of batches(locationRows)) {
    await db
      .insert(locations)
      .values(batch)
      .onConflictDoUpdate({
        target: locations.id,
        set: updateSet(locations, ["id"]),
      });
  }
  console.log(`Seeded ${locationRows.length} locations`);

  for (const batch of batches(runRows)) {
    await db
      .insert(runs)
      .values(batch)
      .onConflictDoUpdate({
        target: runs.runId,
        set: updateSet(runs, ["run_id"]),
      });
  }
  console.log(`Seeded ${runRows.length} runs`);

  for (const batch of batches(recommendationRows)) {
    await db
      .insert(recommendations)
      .values(batch)
      .onConflictDoUpdate({
        target: [
          recommendations.engineId,
          recommendations.forTalkId,
          recommendations.candidateId,
        ],
        set: updateSet(recommendations, [
          "engine_id",
          "for_talk_id",
          "candidate_id",
        ]),
      });
  }
  console.log(`Seeded ${recommendationRows.length} recommendations`);

  process.exit(0);
}

main().catch((error: unknown) => {
  // Our own errors read best as a message; database errors carry code/detail/constraint, so print them whole.
  console.error(error instanceof Error && !("code" in error) ? error.message : error);
  process.exit(1);
});
