"""Walk the CCS conference-paper retrieval system and count every meeting.

Checkpointed: each meeting's counts are written to chem/ccs/meetings.json as soon
as they are parsed, and a rerun skips anything already recorded. Progress is in
chem/ccs/STATUS.json, probeable at any time.

Usage: python3 ccs_crawl.py
"""
import json
import time
import urllib.request
import http.cookiejar
from pathlib import Path

import ccslib

OUT = Path("chem/ccs")
OUT.mkdir(parents=True, exist_ok=True)
MEETINGS = OUT / "meetings.json"
INDEX = OUT / "index.json"
STATUS = OUT / "STATUS.json"
DELAY = 0.7

_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))


def fetch(url, referer=ccslib.BASE):
    req = urllib.request.Request(url, headers={
        "User-Agent": ccslib.UA, "Referer": referer,
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    with _opener.open(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def status(**kw):
    save(STATUS, kw)


def build_index():
    """All 210 meetings, crawled once and cached."""
    cached = load(INDEX, None)
    if cached:
        return cached
    fetch(ccslib.BASE)                      # establish the session cookie
    first = fetch(ccslib.BASE)
    pages = ccslib.parse_page_count(first) or 1
    meetings = ccslib.parse_meeting_list(first)
    for p in range(2, pages + 1):
        status(phase="index", page=p, of=pages, meetings_so_far=len(meetings))
        meetings += ccslib.parse_meeting_list(fetch(f"{ccslib.BASE}?page={p}"))
        time.sleep(DELAY)
    save(INDEX, meetings)
    return meetings


def main():
    meetings = build_index()
    done = load(MEETINGS, {})
    todo = [m for m in meetings if str(m["id"]) not in done]
    print(f"{len(meetings)} meetings indexed, {len(done)} already counted, "
          f"{len(todo)} to go")

    for i, m in enumerate(todo, 1):
        status(phase="meetings", done=len(done), total=len(meetings),
               in_flight=m["name"], year=m["year"])
        try:
            page = fetch(f"{ccslib.BASE}meeting.php?id={m['id']}")
            volumes = ccslib.parse_volumes(page)
            done[str(m["id"])] = {
                **m,
                "volumes": len(volumes),
                "total": ccslib.total_abstracts(page),
                "invited": ccslib.invited_abstracts(page),
                "contributed": ccslib.contributed_abstracts(page),
                "url": f"{ccslib.BASE}meeting.php?id={m['id']}",
            }
        except Exception as e:                      # a dead record is recorded as such
            done[str(m["id"])] = {**m, "error": repr(e),
                                  "url": f"{ccslib.BASE}meeting.php?id={m['id']}"}
        save(MEETINGS, done)                        # checkpoint every single row
        if i % 10 == 0 or i == len(todo):
            print(f"  {len(done)}/{len(meetings)}  last: {m['name'][:40]}")
        time.sleep(DELAY)

    status(phase="complete", done=len(done), total=len(meetings), in_flight=None)
    print("complete")


if __name__ == "__main__":
    main()
