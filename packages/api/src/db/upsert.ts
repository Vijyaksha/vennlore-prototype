import { getTableColumns, sql, type SQL } from "drizzle-orm";

const BATCH_SIZE = 500;

type Table = Parameters<typeof getTableColumns>[0];

/** `excluded."<sqlName>"` — the proposed row's value inside ON CONFLICT DO UPDATE. */
export function excluded(sqlName: string): SQL {
  return sql.raw(`excluded."${sqlName}"`);
}

/** Yield rows in slices of at most 500 (keeps each INSERT under Postgres parameter limits). */
export function* batches<T>(rows: T[]): Generator<T[]> {
  for (let i = 0; i < rows.length; i += BATCH_SIZE) {
    yield rows.slice(i, i + BATCH_SIZE);
  }
}

/**
 * The `set` map for onConflictDoUpdate: every column except `skip`, keyed by the
 * column's property name (what Drizzle's `set` expects) and valued
 * `excluded."<sql name>"`, so every upsert overwrites the whole row. Since the
 * rename, a column's property name and its SQL name are the same string.
 */
export function updateSet(table: Table, skip: string[]): Record<string, SQL> {
  return Object.fromEntries(
    Object.entries(getTableColumns(table))
      .filter(([, column]) => !skip.includes(column.name))
      .map(([property, column]) => [property, excluded(column.name)]),
  );
}
