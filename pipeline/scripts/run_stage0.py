# pipeline/scripts/run_stage0.py
"""End-to-end Stage-0 eval on the micro-corpus. GATED: live LLM spend —
do not run without Rupert's explicit go and ANTHROPIC_API_KEY set.
Checkpoints every artifact (skip-if-exists); rerun resumes.
Progress probeable at pipeline/out/stage0/status.json."""
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engine.corpus import Talk, load_talks  # noqa: E402
from gps_engine.funnel import candidates  # noqa: E402
from gps_engine.graph import MethodGraph  # noqa: E402
from gps_engine.li_extraction import build_extractor, extract_methods_li  # noqa: E402
from gps_engine.llm import AnthropicLLM  # noqa: E402
from gps_engine.recommend import assemble  # noqa: E402
from gps_engine.rubric import Judgment, judge_candidate  # noqa: E402
from gps_engine.similarity import apply_verdicts, judge_pair, propose_pairs, sbert_embedder  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out" / "stage0"
EXTRACT_MODEL = "claude-haiku-4-5-20251001"
JUDGE_MODEL = "claude-sonnet-5"
t0 = time.time()


def status(msg: str) -> None:
    (OUT / "status.json").write_text(json.dumps(
        {"phase": msg, "elapsed_s": round(time.time() - t0)}))
    print(f"[{round(time.time() - t0)}s] {msg}", flush=True)


# Checkpoints key by talk-id / pair-hash ONLY — not by prompt or model.
# After changing a prompt or model, delete the matching out/stage0/ subdir
# (methods/ for extraction, verdicts/ for the similarity judge,
# judgments/ for the rubric) or stale results will be silently reused.
def checkpointed(path: Path, fn):
    if path.exists():
        return json.loads(path.read_text())
    result = fn()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result))
    tmp.rename(path)
    return result


def pair_key(a: str, b: str) -> str:
    return hashlib.sha256(f"{a}||{b}".encode()).hexdigest()[:24]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ("methods", "verdicts", "judgments"):
        (OUT / sub).mkdir(exist_ok=True)

    mc = json.loads((ROOT / "datasets" / "micro-corpus.json").read_text())
    neg = mc["negatives"]
    positive_ids = {p["id"] for p in mc["positives"]}
    ids = (positive_ids
           | set(neg["random_unrelated"])
           | set(neg["same_domain_different_method"]))
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)
    missing = ids - set(talks)
    if missing:
        raise SystemExit(f"micro-corpus ids missing from archive: {sorted(missing)}")

    # The anchor is an external paper: represent it as a pseudo-talk (id 0).
    anchor = Talk(
        id=0, title=mc["anchor"]["title"],
        abstract=("Self-assembled porphyrin nanorods; photoconductivity with "
                  "fast on/off transients and slow growth/decay; bias-training "
                  "produces reversed short-circuit photocurrent (memory); "
                  "conduction through coupled LUMOs of stacked molecules."),
        topics=(), units=("DPOLY",), session_title="", start=None, end=None)
    talks[0] = anchor

    judge_llm = AnthropicLLM(JUDGE_MODEL)

    status("extraction")
    g = MethodGraph()
    for i, t in enumerate(sorted(talks.values(), key=lambda t: t.id)):
        # Build a fresh extractor per talk rather than reusing one across the
        # loop: SchemaLLMPathExtractor.__call__ does asyncio.run(...) per
        # invocation, and reusing one Anthropic client's httpx transport
        # across separate event loops is unsafe (the transport binds to the
        # loop it was first used on). Construction is cheap and offline.
        ms = checkpointed(OUT / "methods" / f"{t.id}.json",
                          lambda t=t: extract_methods_li(t, build_extractor(EXTRACT_MODEL)))
        for m in ms:
            g.link_talk(t.id, m)
        if i % 5 == 0:
            status(f"extraction {i + 1}/{len(talks)}")

    status("similarity")
    names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
    pairs = propose_pairs(names, embed=sbert_embedder())
    status(f"similarity: {len(names)} names, {len(pairs)} proposed pairs")
    verdicts = []
    for i, (a, b) in enumerate(pairs):
        v = checkpointed(OUT / "verdicts" / f"{pair_key(a, b)}.json",
                         lambda a=a, b=b: judge_pair(a, b, judge_llm))
        verdicts.append((a, b, v))
        if i % 5 == 0:
            status(f"verdicts {i + 1}/{len(pairs)}")
    apply_verdicts(g, verdicts)
    g.save(OUT / "graph.json")

    status("funnel+rubric")
    cands = candidates(g, talk_id=0)
    status(f"rubric: {len(cands)} candidates")
    judgments = []
    for i, cid in enumerate(sorted(cands)):
        j = checkpointed(OUT / "judgments" / f"{cid}.json",
                         lambda cid=cid: judge_candidate(anchor, talks[cid], judge_llm).__dict__)
        judgments.append(Judgment(**j))
        if i % 5 == 0:
            status(f"rubric {i + 1}/{len(cands)}")

    picks = assemble(judgments)
    matched_ids = {j.candidate_id for j in judgments if j.match}
    report = {
        "corpus_size": len(talks),
        "funnel_candidates": sorted(cands),
        "matches": [j.__dict__ for j in judgments if j.match],
        "picks": {"core": [j.__dict__ for j in picks.core],
                  "unexpected": [j.__dict__ for j in picks.unexpected]},
        "expected_positives": sorted(positive_ids),
        "hit_positives": sorted(matched_ids & positive_ids),
        "missed_positives": sorted(positive_ids - matched_ids),
        "positives_not_in_funnel": sorted(positive_ids - cands),
        "false_positives": sorted(matched_ids - positive_ids),
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=1))
    status("done — see pipeline/out/stage0/report.json")


if __name__ == "__main__":
    main()
