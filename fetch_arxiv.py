"""Download real research papers from arXiv to use as stand-in conference sessions.

Each arXiv category becomes a "track"; each paper becomes a "session".
Free, no API key. Uses the public arXiv API (https://info.arxiv.org/help/api/).

Run:   python fetch_arxiv.py            (5 papers per track, about 30 in total)
       python fetch_arxiv.py 8          (8 papers per track)
Output: raw_sessions.csv  ->  then run:  python extract_topics.py raw_sessions.csv
"""

import csv
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

TRACKS = {
    "Machine Learning": "cs.LG",
    "Photonics": "physics.optics",
    "Materials Science": "cond-mat.mtrl-sci",
    "Quantum Computing": "quant-ph",
    "Computational Biology": "q-bio.BM",
    "Space Science": "astro-ph.EP",
}
PER_TRACK = int(sys.argv[1]) if len(sys.argv) > 1 else 5
API = "http://export.arxiv.org/api/query?"
NS = {"a": "http://www.w3.org/2005/Atom"}


def clean(text: str | None) -> str:
    return " ".join((text or "").split())


def parse(xml_text: str) -> list[tuple[str, str, str]]:
    """Return a list of (title, abstract, url) from an arXiv Atom feed."""
    root = ET.fromstring(xml_text)
    return [
        (
            clean(e.findtext("a:title", namespaces=NS)),
            clean(e.findtext("a:summary", namespaces=NS)),
            clean(e.findtext("a:id", namespaces=NS)),
        )
        for e in root.findall("a:entry", NS)
    ]


def fetch(category: str, n: int) -> list[tuple[str, str, str]]:
    params = urllib.parse.urlencode(
        {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": n,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    req = urllib.request.Request(API + params, headers={"User-Agent": "vennlore-prototype (class project)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return parse(r.read().decode("utf-8"))


if __name__ == "__main__":
    rows = []
    for i, (track, cat) in enumerate(TRACKS.items()):
        if i:
            time.sleep(3)  # arXiv asks for a 3-second pause between requests
        papers = fetch(cat, PER_TRACK)
        print(f"{track:22s} ({cat}): {len(papers)} papers")
        for title, abstract, url in papers:
            rows.append(
                {
                    "session_id": f"S{len(rows) + 1:02d}",
                    "title": title,
                    "track": track,
                    "abstract": abstract[:1500],
                    "url": url,
                }
            )
    with open("raw_sessions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["session_id", "title", "track", "abstract", "url"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {len(rows)} sessions to raw_sessions.csv")
    print("Next: start LM Studio's server, then run  python extract_topics.py raw_sessions.csv")
