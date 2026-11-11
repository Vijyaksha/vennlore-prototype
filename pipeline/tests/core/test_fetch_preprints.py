"""scripts/fetch_preprints.py: pages through arXiv / bioRxiv / medRxiv listings,
checkpoints every page (a rerun resumes without refetching), and writes contract
Talk rows. A fake fetcher stands in for the network."""
import importlib.util
import json
from pathlib import Path

from gps_core.contracts import validate

spec = importlib.util.spec_from_file_location(
    "fetch_preprints", Path(__file__).resolve().parents[2] / "scripts" / "fetch_preprints.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def arxiv_page(start: int, n: int) -> str:
    entries = "".join(
        f"""<entry><id>http://arxiv.org/abs/2511.{start + i:05d}v1</id>
        <published>2025-11-03T00:00:00Z</published><title>Paper {start + i}</title>
        <summary>Abstract {start + i}.</summary>
        <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cs.LG"/></entry>"""
        for i in range(n))
    return f'<feed xmlns="http://www.w3.org/2005/Atom">{entries}</feed>'


def rxiv_page(server: str, cursor: int, n: int, total: int) -> str:
    return json.dumps({"messages": [{"status": "ok", "cursor": cursor, "count": n, "total": total}],
                       "collection": [{"doi": f"10.1101/{server}.{cursor + i}", "title": f"P{cursor + i}",
                                       "abstract": "A.", "date": "2025-11-01",
                                       "category": "neuroscience", "server": server}
                                      for i in range(n)]})


class FakeNet:
    def __init__(self):
        self.urls: list[str] = []

    def __call__(self, url: str) -> str:
        self.urls.append(url)
        if "export.arxiv.org" in url:
            start = int(url.split("start=")[1].split("&")[0])
            return arxiv_page(start, max(0, min(100, 150 - start)))   # 150 papers exist
        server = "bioRxiv" if "/biorxiv/" in url else "medRxiv"
        cursor = int(url.split("?")[0].rstrip("/").rsplit("/", 1)[1])
        return rxiv_page(server, cursor, max(0, min(100, 120 - cursor)), 120)


def plan():
    return [("arxiv", "cs.LG"), ("biorxiv", "neuroscience"), ("medrxiv", "neuroscience")]


def test_pages_until_the_limit_and_writes_valid_talk_rows(tmp_path):
    net = FakeNet()
    out = tmp_path / "preprints.json"
    rows = mod.fetch_all(plan(), limit=130, days=30, fetch=net, work=tmp_path / "work",
                         out=out, sleep=lambda s: None, today="2025-11-10")
    by_type = {}
    for r in rows:
        validate("talk", r)
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    assert by_type == {"preprint:arxiv": 130, "preprint:biorxiv": 120, "preprint:medrxiv": 120}
    assert json.loads(out.read_text())["talks"] == rows
    assert any("2025-10-11/2025-11-10" in u for u in net.urls)          # the date window
    assert any("category=neuroscience" in u for u in net.urls)
    assert json.loads((tmp_path / "work" / "status.json").read_text())["phase"]


def test_rerun_resumes_from_checkpointed_pages(tmp_path):
    kw = dict(limit=130, days=30, work=tmp_path / "work", out=tmp_path / "p.json",
              sleep=lambda s: None, today="2025-11-10")
    mod.fetch_all(plan(), fetch=FakeNet(), **kw)
    again = FakeNet()
    rows = mod.fetch_all(plan(), fetch=again, **kw)
    assert again.urls == [] and len(rows) == 370


def test_plan_from_args_covers_all_three_archives():
    p = mod.make_plan(arxiv="cs.LG,physics.optics", biorxiv="neuroscience", medrxiv="all")
    assert p == [("arxiv", "cs.LG"), ("arxiv", "physics.optics"),
                 ("biorxiv", "neuroscience"), ("medrxiv", "")]
