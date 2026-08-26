"""Corpus loading: join presentation records with their parent session/event
metadata to produce the Talk objects consumed by later pipeline stages."""
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Talk:
    id: int
    title: str
    abstract: str
    topics: tuple[str, ...]
    units: tuple[str, ...]
    session_title: str
    start: str | None
    end: str | None


def load_talks(archive: Path, only_ids: set[int] | None = None) -> dict[int, Talk]:
    sess_by_pid: dict[int, dict] = {}
    for f in (archive / "events").glob("*.json"):
        e = json.loads(f.read_text())
        for pid in e.get("presentation_ids", []):
            sess_by_pid[pid] = e
    talks: dict[int, Talk] = {}
    for f in (archive / "presentations").glob("*.json"):
        p = json.loads(f.read_text())
        pid = p["id"]
        if p.get("is_withdrawn") or (only_ids is not None and pid not in only_ids):
            continue
        s = sess_by_pid.get(pid, {})
        talks[pid] = Talk(
            id=pid,
            title=p.get("title") or "",
            abstract=p.get("abstract") or "",
            topics=tuple(p.get("topics") or []),
            units=tuple(s.get("sponsor_units") or []),
            session_title=s.get("title") or "",
            start=p.get("start"), end=p.get("end"),
        )
    return talks
