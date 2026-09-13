// App identity and conference facts. Brand names stay constants, not messages.
export const APP_NAME = "Kindred";
export const MEETING_LABEL = "APS GPS 2026";
export const TIME_ZONE = "America/Denver";

// Who the app shows picks for: exactly one of a presenter (every talk they
// present is an anchor) or a single anchor talk. The server's Subject schema
// is strict, so the object carries exactly one key.
export type Subject = { presenterId: number } | { talkId: number };

// The claimed anchor talk (the porphyrin-nanorod photoconductivity paper),
// seeded as talk id 0. Used when no subject is configured or a value is bad.
const DEFAULT_SUBJECT: Subject = { talkId: 0 };

/** Parses a non-negative integer id, or null when the value is malformed. */
function parseId(raw: string): number | null {
  const trimmed = raw.trim();
  if (!/^\d+$/.test(trimmed)) return null;
  const id = Number(trimmed);
  return Number.isSafeInteger(id) ? id : null;
}

/**
 * Builds the subject from the public env. A presenter id wins over an anchor
 * talk id; when both are set, the ignored one is reported through `warn`.
 * A malformed value is reported and treated as unset, so nothing valid
 * configured means the default anchor talk.
 */
export function subjectFromEnv(
  env: { presenterId?: string; anchorTalkId?: string },
  warn: (message: string) => void = console.warn,
): Subject {
  if (env.presenterId !== undefined) {
    const presenterId = parseId(env.presenterId);
    if (presenterId !== null && presenterId >= 1) {
      if (env.anchorTalkId !== undefined) {
        warn(
          `Both NEXT_PUBLIC_PRESENTER_ID and NEXT_PUBLIC_ANCHOR_TALK_ID are set; NEXT_PUBLIC_ANCHOR_TALK_ID is ignored and presenter ${presenterId} is used.`,
        );
      }
      return { presenterId };
    }
    warn(
      `NEXT_PUBLIC_PRESENTER_ID=${JSON.stringify(env.presenterId)} is not a positive integer; ignoring it.`,
    );
  }
  if (env.anchorTalkId !== undefined) {
    const talkId = parseId(env.anchorTalkId);
    if (talkId !== null) return { talkId };
    warn(
      `NEXT_PUBLIC_ANCHOR_TALK_ID=${JSON.stringify(env.anchorTalkId)} is not a non-negative integer; using the default anchor talk.`,
    );
  }
  return DEFAULT_SUBJECT;
}

// Direct process.env.NEXT_PUBLIC_* references so Next inlines them at build.
export const SUBJECT: Subject = subjectFromEnv({
  presenterId: process.env.NEXT_PUBLIC_PRESENTER_ID,
  anchorTalkId: process.env.NEXT_PUBLIC_ANCHOR_TALK_ID,
});

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
