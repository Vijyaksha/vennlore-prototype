import type { Subject } from "@repo/contracts";

// App identity and conference facts. Brand names stay constants, not messages.
export const APP_NAME = "Kindred";
export const MEETING_LABEL = "APS GPS 2026";
export const TIME_ZONE = "America/Denver";

// Who the app shows picks for: exactly one of a presenter (every talk they
// present is an anchor) or a single anchor talk. The server's Subject schema
// is strict, so the object carries exactly one key.
export type { Subject };

// The claimed anchor talk (the porphyrin-nanorod photoconductivity paper),
// seeded as talk id 0. Used when no subject is configured.
const DEFAULT_SUBJECT: Subject = { talk_id: 0 };

/** The trimmed value, or null when the variable is unset or blank. */
function setValue(raw: string | undefined): string | null {
  const trimmed = raw?.trim() ?? "";
  return trimmed === "" ? null : trimmed;
}

/** Parses a set value as an integer id of at least `min`, or throws naming the variable. */
function parseId(name: string, raw: string, value: string, min: number): number {
  const id = /^\d+$/.test(value) ? Number(value) : NaN;
  if (!Number.isSafeInteger(id) || id < min) {
    throw new Error(
      `${name}=${JSON.stringify(raw)} is not an integer >= ${min}. Fix or unset it.`,
    );
  }
  return id;
}

// Console noise only helps while developing; production visitors never see it.
const devWarn = (message: string) => {
  // Set by Next itself, not a build input we choose, so it stays out of turbo's hash.
  // eslint-disable-next-line turbo/no-undeclared-env-vars
  if (process.env.NODE_ENV !== "production") console.warn(message);
};

/**
 * Builds the subject from the public env. Unset or blank values count as
 * unset. A set but malformed value throws, so a bad deploy fails at build
 * (prerender) instead of silently showing someone else's picks. A presenter
 * id wins over an anchor talk id; when both are set, `warn` reports it.
 */
export function subjectFromEnv(
  env: { presenterId?: string; anchorTalkId?: string },
  warn: (message: string) => void = devWarn,
): Subject {
  const presenterValue = setValue(env.presenterId);
  const talkValue = setValue(env.anchorTalkId);
  const presenterId =
    presenterValue === null
      ? null
      : parseId("NEXT_PUBLIC_PRESENTER_ID", env.presenterId!, presenterValue, 1);
  const talkId =
    talkValue === null
      ? null
      : parseId("NEXT_PUBLIC_ANCHOR_TALK_ID", env.anchorTalkId!, talkValue, 0);

  if (presenterId !== null) {
    if (talkId !== null) {
      warn(
        `Both NEXT_PUBLIC_PRESENTER_ID and NEXT_PUBLIC_ANCHOR_TALK_ID are set; NEXT_PUBLIC_ANCHOR_TALK_ID is ignored and presenter ${presenterId} is used.`,
      );
    }
    return { presenter_id: presenterId };
  }
  return talkId !== null ? { talk_id: talkId } : DEFAULT_SUBJECT;
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
