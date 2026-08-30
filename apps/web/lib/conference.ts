// App identity and conference facts. Brand names stay constants, not messages.
export const APP_NAME = "Kindred";
export const MEETING_LABEL = "APS GPS 2026";
export const TIME_ZONE = "America/Denver";
export const SCORE_MAX = 15;

// Denver-local conference days, Sun Mar 15 through Fri Mar 20 2026, keyed the
// same way the agenda procedure keys its day groups (en-CA YYYY-MM-DD).
export const CONFERENCE_DAYS = [
  "2026-03-15",
  "2026-03-16",
  "2026-03-17",
  "2026-03-18",
  "2026-03-19",
  "2026-03-20",
] as const;

// Noon-06:00 is mid-day MDT on every conference day, so formatting this
// instant with the Denver time zone always lands on the intended day.
export function dayDate(dayKey: string): Date {
  return new Date(`${dayKey}T12:00:00-06:00`);
}

const denverDay = new Intl.DateTimeFormat("en-CA", {
  timeZone: TIME_ZONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

export function denverDayKey(instant: Date): string {
  return denverDay.format(instant);
}
