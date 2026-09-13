import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { inArray } from "drizzle-orm";

import { getDb } from "./index";
import { locations, recommendations, runs, talks } from "./schema";
import { resolveSeedPath } from "./seed-path";
import { toRunInsert, toSeedFile, toTalkInsert } from "./transform";
import { batches, updateSet } from "./upsert";

const DEFAULT_SEED_PATH = join(
  dirname(fileURLToPath(import.meta.url)),
  "../../../../pipeline/out/app_seed.v2.json",
);

const SEED_PATH = resolveSeedPath(process.env, DEFAULT_SEED_PATH);

/** Idempotent upsert of the v2 contract seed in one transaction: talks,
 *  locations, runs, then each seeded engine's recommendations replaced whole. */
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
  const locationRows = seed.locations;
  const runRows = seed.runs.map(toRunInsert);
  const recommendationRows = seed.recommendations;

  const db = getDb();
  const engineIds = [...new Set(recommendationRows.map((r) => r.engine_id))];

  // One transaction: a failed reseed leaves the store exactly as it was.
  await db.transaction(async (tx) => {
    for (const batch of batches(talkRows)) {
      await tx
        .insert(talks)
        .values(batch)
        .onConflictDoUpdate({ target: talks.id, set: updateSet(talks, ["id"]) });
    }
    console.log(`Seeded ${talkRows.length} talks`);

    for (const batch of batches(locationRows)) {
      await tx
        .insert(locations)
        .values(batch)
        .onConflictDoUpdate({
          target: locations.id,
          set: updateSet(locations, ["id"]),
        });
    }
    console.log(`Seeded ${locationRows.length} locations`);

    for (const batch of batches(runRows)) {
      await tx
        .insert(runs)
        .values(batch)
        .onConflictDoUpdate({
          target: runs.run_id,
          set: updateSet(runs, ["run_id"]),
        });
    }
    console.log(`Seeded ${runRows.length} runs`);

    // Delete first, so an engine's rows are replaced rather than merged: a
    // candidate dropped by a rerun does not survive as a stale row. Talks, runs
    // and locations are already in place, and the foreign keys are ON DELETE no
    // action, so nothing else is touched.
    if (engineIds.length > 0) {
      await tx.delete(recommendations).where(inArray(recommendations.engine_id, engineIds));
      console.log(`Replaced recommendations for engines: ${engineIds.join(", ")}`);
    }

    for (const batch of batches(recommendationRows)) {
      await tx
        .insert(recommendations)
        .values(batch)
        .onConflictDoUpdate({
          target: [
            recommendations.engine_id,
            recommendations.for_talk_id,
            recommendations.candidate_id,
          ],
          set: updateSet(recommendations, [
            "engine_id",
            "for_talk_id",
            "candidate_id",
          ]),
        });
    }
    console.log(`Seeded ${recommendationRows.length} recommendations`);
  });

  process.exit(0);
}

main().catch((error: unknown) => {
  // Our own errors read best as a message; database errors carry code/detail/constraint, so print them whole.
  console.error(error instanceof Error && !("code" in error) ? error.message : error);
  process.exit(1);
});
