import type { Pick, Recommendation, Talk } from "@repo/contracts";

import type { MatchRow, RecRow, TalkRow } from "./repo";

const iso = (d: Date | null) => (d === null ? null : d.toISOString());

/** The store's row shape is the contract's, so only the timestamps change. */
export function toTalk(r: TalkRow): Talk {
  return { ...r, start: iso(r.start), end: iso(r.end) };
}

export function toRecommendation(r: RecRow): Recommendation {
  return {
    ...r,
    // The column is a plain integer; the contract pins it to the literal 1.
    // getMatches filters on CONTRACT_VERSION, so every served row already
    // carries it, and the .output() validator rejects any other value at runtime.
    contract_version: r.contract_version as Recommendation["contract_version"],
  };
}

export function toPick(m: MatchRow): Pick {
  const { candidate, ...rec } = m;
  return { ...toRecommendation(rec), candidate: toTalk(candidate) };
}
