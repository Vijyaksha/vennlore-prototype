import { connection, walkMinutes, type Connection } from "./walk";

export interface AgendaInput {
  id: number;
  title: string;
  sessionTitle: string | null;
  start: Date | null;
  end: Date | null;
  building: string | null;
  room: string | null;
}

/** An input item that has a start time, annotated with the connection from the
 *  previous item on the same Denver day (null for the first item of the day). */
export type TimedItem<T extends AgendaInput = AgendaInput> = T & { start: Date; transit: Connection | null };

const denverDate = new Intl.DateTimeFormat("en-CA", {
  timeZone: "America/Denver",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

/** Drops untimed items, sorts by start (then `tiebreak`, then id), groups by
 *  conference-local (Denver) date and annotates each item after the first with
 *  walk time and slack. Extra fields on the input items are carried through. */
export function groupByDenverDay<T extends AgendaInput>(
  items: T[],
  tiebreak: (a: T, b: T) => number = () => 0,
): { date: string; items: TimedItem<T>[] }[] {
  const timed = items
    .filter((t): t is T & { start: Date } => t.start !== null)
    .sort((a, b) => a.start.getTime() - b.start.getTime() || tiebreak(a, b) || a.id - b.id);
  const byDate = new Map<string, TimedItem<T>[]>();
  for (const t of timed) {
    const date = denverDate.format(t.start);
    const list = byDate.get(date) ?? [];
    const prev = list.at(-1);
    let transit: Connection | null = null;
    if (prev !== undefined) {
      const departure = prev.end ?? prev.start;
      const gapMinutes = (t.start.getTime() - departure.getTime()) / 60_000;
      transit = connection(gapMinutes, walkMinutes(prev, t));
    }
    list.push({ ...t, transit });
    byDate.set(date, list);
  }
  return [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, dayItems]) => ({ date, items: dayItems }));
}
