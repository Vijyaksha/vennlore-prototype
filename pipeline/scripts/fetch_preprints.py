"""Download recent preprints from arXiv, bioRxiv and medRxiv as contract Talk rows.
GATED: a download, so only with Rupert's go. Free, no API keys.

  uv run python scripts/fetch_preprints.py
  uv run python scripts/fetch_preprints.py --arxiv cs.LG,physics.optics --biorxiv biophysics,neuroscience --medrxiv all --days 90 --limit 300

Writes out/preprints.json ({"talks": [...]}); add_engine_to_seed.py --extra out/preprints.json
then offers the papers as candidates next to the programme's talks.
Progress: out/preprints/status.json. Every page is checkpointed under out/preprints/pages/,
so a rerun resumes instead of refetching. Waits 3 s between live requests (arXiv's rule)."""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.checkpoint import content_key  # noqa: E402
from gps_core.progress import Status  # noqa: E402
from gps_data.preprints import dedupe, parse_arxiv, parse_rxiv  # noqa: E402
from gps_data.talk import to_row  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out"
PAGE = 100
DEFAULTS = {  # areas a physics meeting's attendees cross into
    "arxiv": "cs.LG,physics.optics,cond-mat.mtrl-sci,quant-ph,physics.bio-ph",
    "biorxiv": "biophysics,bioengineering,neuroscience,synthetic biology",
    "medrxiv": "radiology and imaging,health informatics",
}


def make_plan(arxiv: str = "", biorxiv: str = "", medrxiv: str = "") -> list[tuple[str, str]]:
    plan = []
    for source, cats in (("arxiv", arxiv), ("biorxiv", biorxiv), ("medrxiv", medrxiv)):
        for c in (x.strip() for x in cats.split(",") if x.strip()):
            plan.append((source, "" if c == "all" else c))
    return plan


def _url(source: str, cat: str, cursor: int, frm: str, to: str) -> str:
    if source == "arxiv":
        q = f"cat:{cat} AND submittedDate:[{frm.replace('-', '')}0000 TO {to.replace('-', '')}2359]"
        return "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"search_query": q, "start": cursor, "max_results": PAGE,
             "sortBy": "submittedDate", "sortOrder": "descending"})
    url = f"https://api.biorxiv.org/details/{source}/{frm}/{to}/{cursor}"
    return url + (f"?category={cat.replace(' ', '_')}" if cat else "")


def _live_fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "vennlore-conferenceapp (class project)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def fetch_all(plan: list[tuple[str, str]], limit: int, days: int, out: Path, work: Path,
              fetch: Callable[[str], str] = _live_fetch, sleep: Callable = time.sleep,
              today: str | None = None) -> list[dict]:
    to = today or date.today().isoformat()
    frm = (date.fromisoformat(to) - timedelta(days=days)).isoformat()
    status = Status(work)
    talks = []
    for n, (source, cat) in enumerate(plan, 1):
        got, cursor = [], 0
        while len(got) < limit:
            url = _url(source, cat, cursor, frm, to)
            page_file = work / "pages" / f"{content_key(url)}.txt"
            if page_file.exists():
                text = page_file.read_text(encoding="utf-8")
            else:
                text = fetch(url)
                page_file.parent.mkdir(parents=True, exist_ok=True)
                page_file.write_text(text, encoding="utf-8")
                sleep(3)
            page = parse_arxiv(text) if source == "arxiv" else parse_rxiv(text)
            got += page
            cursor += PAGE if source == "arxiv" else len(page)
            status.set(f"{source} {cat or 'all'} ({n}/{len(plan)}): {min(len(got), limit)} papers")
            if not page:
                break
            if source != "arxiv":
                total = int((json.loads(text).get("messages") or [{}])[0].get("total") or 0)
                if cursor >= total:
                    break
        talks += got[:limit]
    rows = [to_row(t) for t in dedupe(talks)]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"talks": rows}, indent=1), encoding="utf-8")
    status.set(f"wrote {len(rows)} papers to {out}")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    for source, cats in DEFAULTS.items():
        ap.add_argument(f"--{source}", default=cats, help="comma-separated categories, 'all', or ''")
    ap.add_argument("--days", type=int, default=90, help="how far back to look")
    ap.add_argument("--limit", type=int, default=200, help="max papers per category")
    ap.add_argument("--out", default=str(OUT / "preprints.json"))
    a = ap.parse_args()
    plan = make_plan(a.arxiv, a.biorxiv, a.medrxiv)
    rows = fetch_all(plan, a.limit, a.days, Path(a.out), OUT / "preprints")
    counts = {}
    for r in rows:
        counts[r["type"]] = counts.get(r["type"], 0) + 1
    print("papers:", ", ".join(f"{k.split(':')[1]} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
