"""Pure transforms that shape the archived GPS data + Stage-0 judgments into
the single seed JSON consumed by the web app. Offline: no LLM, no network."""
import html
import re

_TAG = re.compile(r"<[^>]+>")


def clean_text(s: str) -> str:
    # Tags first, entities second: escaped angle brackets (&lt;) stay text.
    s = _TAG.sub("", s)
    s = html.unescape(s)
    return " ".join(s.split())


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
        "match": j["match"],
        "cross_domain": j["cross_domain"],
        "why": j["why"],
        "strongest_parallel": j.get("strongest_parallel", ""),
    } for j in sorted(judgments, key=lambda j: j["candidate_id"])]

    location_rows = [{"id": l["id"], "building": l["building"], "room": l["room"]}
                     for l in locations]
    return {"talks": talks, "locations": location_rows,
            "recommendations": recommendations}
