"""Load Talk records from the crawled GPS archive (data/gps2026): join each
presentation to its event (session) and the event's first location. Withdrawn
talks are excluded here, once, for everyone."""
import html
import json
import re
from pathlib import Path

from gps_data.talk import Talk

_TAG = re.compile(r"<[^>]+>")


def clean_text(s: str | None) -> str:
    # Tags first, entities second: escaped angle brackets (&lt;) stay text.
    s = _TAG.sub("", s or "")
    s = html.unescape(s)
    return " ".join(s.split())


def _opt(s) -> str | None:
    s = clean_text(s) if isinstance(s, str) else s
    return s or None


def _read_dir(d: Path) -> list[dict]:
    return [json.loads(f.read_text()) for f in sorted(d.glob("*.json"))]


def load_talks(archive: Path, only_ids: set[int] | None = None) -> dict[int, Talk]:
    events = _read_dir(archive / "events")
    locations = {l["id"]: l for l in _read_dir(archive / "locations")} \
        if (archive / "locations").exists() else {}
    event_by_pid = {pid: e for e in events for pid in e.get("presentation_ids") or []}
    talks: dict[int, Talk] = {}
    for p in _read_dir(archive / "presentations"):
        pid = p["id"]
        if p.get("is_withdrawn") or (only_ids is not None and pid not in only_ids):
            continue
        e = event_by_pid.get(pid)
        loc = None
        if e and e.get("location_ids"):
            loc = locations.get(e["location_ids"][0])
        talks[pid] = Talk(
            id=pid,
            external_id=p.get("external_id") or None,
            title=clean_text(p.get("title")),
            abstract=clean_text(p.get("abstract")),
            units=tuple((e or {}).get("sponsor_units") or []),
            topics=tuple(p.get("topics") or []),
            type=p.get("type") or None,
            is_invited=bool(p.get("is_invited")),
            is_withdrawn=bool(p.get("is_withdrawn")),
            start=p.get("start"), end=p.get("end"),
            sort_order=p.get("sort_order"),
            presentation_location=_opt(p.get("presentation_location")),
            author_ids=tuple(p.get("author_ids") or []),
            presenter_ids=tuple(p.get("presenter_ids") or []),
            publication_reference=_opt(p.get("publication_reference")),
            funding_acknowledgement=_opt(p.get("funding_acknowledgement")),
            team_acknowledgement=_opt(p.get("team_acknowledgement")),
            session_id=e["id"] if e else None,
            session_title=_opt(e.get("title")) if e else None,
            session_code=(e.get("code") or None) if e else None,
            session_type=(e.get("type") or None) if e else None,
            session_topics=tuple((e or {}).get("topics") or []),
            building=(loc or {}).get("building") or None,
            room=(loc or {}).get("room") or None,
        )
    return talks


def anchors_for(talks: dict[int, Talk], presenter_id: int) -> list[Talk]:
    """The talks a presenter presents, in id order."""
    return sorted((t for t in talks.values() if presenter_id in t.presenter_ids),
                  key=lambda t: t.id)


def authored_by(talks: dict[int, Talk], presenter_id: int) -> set[int]:
    """Every talk the person is an author on — the exclusion set."""
    return {t.id for t in talks.values() if presenter_id in t.author_ids}
