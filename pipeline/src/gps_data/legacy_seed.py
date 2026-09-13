"""Pure transforms that shape the archived GPS data + Stage-0 judgments into
the single seed JSON consumed by the web app. Offline: no LLM, no network."""
from gps_data.archive import clean_text

__all__ = ["clean_text", "build_talk_row", "build_seed", "legacy_seed"]


def build_talk_row(presentation: dict, event: dict | None,
                   location: dict | None) -> dict:
    return {
        "id": presentation["id"],
        "title": clean_text(presentation.get("title") or ""),
        "session_title": clean_text(event["title"]) if event and event.get("title") else None,
        "units": list(event.get("sponsor_units") or []) if event else [],
        "start": presentation.get("start"),
        "end": presentation.get("end"),
        "building": location.get("building") if location else None,
        "room": location.get("room") if location else None,
        "abstract": clean_text(presentation.get("abstract") or ""),
    }


# The match decision is OURS, derived from the calibrated score sum — the
# rubric checkpoints store the LLM's own (unused) boolean. Keep in sync with
# MATCH_MIN_SCORE in src/gps_engines/graph_v1/engine.py.
MATCH_MIN_SCORE = 5


def build_seed(presentations: list[dict], events: list[dict],
               locations: list[dict], judgments: list[dict],
               anchor_row: dict) -> dict:
    event_by_pid = {pid: e for e in events for pid in e.get("presentation_ids", [])}
    loc_by_id = {l["id"]: l for l in locations}

    talks = [anchor_row]
    for p in presentations:
        e = event_by_pid.get(p["id"])
        loc = loc_by_id.get(e["location_ids"][0]) if e and e.get("location_ids") else None
        talks.append(build_talk_row(p, e, loc))
    talks.sort(key=lambda t: t["id"])

    recommendations = [{
        "for_talk_id": 0,
        "candidate_id": j["candidate_id"],
        "same_method": j["same_method"],
        "specificity": j["specificity"],
        "usage_parallel": j["usage_parallel"],
        "score": j["same_method"] + j["specificity"] + j["usage_parallel"],
        "match": (j["same_method"] + j["specificity"] + j["usage_parallel"])
                 >= MATCH_MIN_SCORE,
        "cross_domain": j["cross_domain"],
        "why": j["why"],
        "strongest_parallel": j.get("strongest_parallel", ""),
    } for j in sorted(judgments, key=lambda j: j["candidate_id"])]

    location_rows = [{"id": l["id"], "building": l["building"], "room": l["room"]}
                     for l in locations]
    return {"talks": talks, "locations": location_rows,
            "recommendations": recommendations}


def legacy_seed(talks, rows, locations) -> dict:
    """The pre-contract shape the current web app seeds from. Plan 2 deletes this."""
    talk_rows = [{
        "id": t.id, "title": t.title, "session_title": t.session_title,
        "units": list(t.units), "start": t.start, "end": t.end,
        "building": t.building, "room": t.room, "abstract": t.abstract,
    } for t in sorted(talks, key=lambda t: t.id)]
    rec_rows = [{
        "for_talk_id": r.for_talk_id, "candidate_id": r.candidate_id,
        "same_method": r.evidence.get("same_method", 0),
        "specificity": r.evidence.get("specificity", 0),
        "usage_parallel": r.evidence.get("usage_parallel", 0),
        "score": r.evidence.get("rubric_sum", round(r.score * 15)),
        "match": r.match, "cross_domain": r.cross_domain,
        "why": r.why, "strongest_parallel": r.strongest_parallel,
    } for r in sorted(rows, key=lambda r: r.candidate_id)]
    return {"talks": talk_rows, "locations": locations, "recommendations": rec_rows}
