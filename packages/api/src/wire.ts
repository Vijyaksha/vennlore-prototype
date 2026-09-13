import type { Pick, Recommendation, Talk } from "@repo/contracts";

import type { MatchRow, RecRow, TalkRow } from "./repo";

const iso = (d: Date | null) => (d === null ? null : d.toISOString());

/** The inverse of transform.toTalkInsert: Drizzle property names -> contract field names, Date -> ISO. */
export function toTalk(r: TalkRow): Talk {
  return {
    id: r.id, external_id: r.externalId, title: r.title, abstract: r.abstract,
    units: r.units, topics: r.topics, type: r.type, is_invited: r.isInvited,
    is_withdrawn: r.isWithdrawn, start: iso(r.start), end: iso(r.end),
    sort_order: r.sortOrder, presentation_location: r.presentationLocation,
    author_ids: r.authorIds, presenter_ids: r.presenterIds,
    publication_reference: r.publicationReference,
    funding_acknowledgement: r.fundingAcknowledgement,
    team_acknowledgement: r.teamAcknowledgement, session_id: r.sessionId,
    session_title: r.sessionTitle, session_code: r.sessionCode,
    session_type: r.sessionType, session_topics: r.sessionTopics,
    building: r.building, room: r.room,
  };
}

export function toRecommendation(r: RecRow): Recommendation {
  return {
    for_talk_id: r.forTalkId, candidate_id: r.candidateId, score: r.score, rank: r.rank,
    match: r.match, cross_domain: r.crossDomain, why: r.why,
    strongest_parallel: r.strongestParallel, shared_methods: r.sharedMethods,
    evidence: r.evidence, engine_id: r.engineId, run_id: r.runId,
    // The column is a plain integer; the contract pins it to the literal 1.
    // getMatches filters on CONTRACT_VERSION, so every served row already
    // carries it, and the .output() validator rejects any other value at runtime.
    contract_version: r.contractVersion as Recommendation["contract_version"],
  };
}

export function toPick(m: MatchRow): Pick {
  return { ...toRecommendation(m), candidate: toTalk(m.candidate) };
}
