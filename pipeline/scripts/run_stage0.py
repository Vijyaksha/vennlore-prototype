# pipeline/scripts/run_stage0.py
"""End-to-end Stage-0 eval on the micro-corpus. GATED: live LLM spend —
do not run without Rupert's explicit go and ANTHROPIC_API_KEY set.
Checkpoints every artifact (skip-if-exists); rerun resumes.
Progress probeable at pipeline/out/stage0/status.json."""
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engine.claims import claims_digest, extract_claims  # noqa: E402
from gps_engine.corpus import Talk, load_talks  # noqa: E402
from gps_engine.funnel import candidates  # noqa: E402
from gps_engine.graph import MethodGraph  # noqa: E402
from gps_engine.li_extraction import build_extractor, extract_methods_li, glean_and_describe  # noqa: E402
from gps_engine.llm import AnthropicLLM, LLMRefusal  # noqa: E402
from gps_engine.recommend import assemble  # noqa: E402
from gps_engine.rubric import Judgment, judge_candidate  # noqa: E402
from gps_engine.similarity import apply_verdicts, judge_pair, propose_pairs, sbert_embedder  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out" / "stage0"
EXTRACT_MODEL = "claude-haiku-4-5-20251001"
JUDGE_MODEL = "claude-sonnet-5"
WORKERS = 8
MIN_EDGE_STRENGTH = 0  # query-time tightness dial; 0 walks every judged edge
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


def parallel(label: str, items, fn):
    """Run fn(item) across a thread pool, preserving input order in the
    returned list. Progress via status() every few completions."""
    done = 0
    lock = threading.Lock()

    def wrapped(item):
        nonlocal done
        r = fn(item)
        with lock:
            done += 1
            if done % 10 == 0 or done == len(items):
                status(f"{label} {done}/{len(items)}")
        return r

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(wrapped, items))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ("methods", "enrich", "claims", "verdicts", "judgments"):
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
    # Its text = summary + the Rupert-approved method axes from the dataset —
    # the first live runs showed a 3-line stub starves the rubric (it judged
    # M1/M3-based positives against an anchor that appeared not to have
    # those methods).
    axes = "\n".join(mc["anchor"]["method_axes"])
    anchor = Talk(
        id=0, title=mc["anchor"]["title"],
        abstract=("Self-assembled porphyrin nanorods; photoconductivity with "
                  "fast on/off transients and slow growth/decay; bias-training "
                  "produces reversed short-circuit photocurrent (memory); "
                  "conduction through coupled LUMOs of stacked molecules.\n"
                  "Methods of this work:\n" + axes),
        topics=(), units=("DPOLY",), session_title="", start=None, end=None)
    talks[0] = anchor

    judge_llm = AnthropicLLM(JUDGE_MODEL)
    extract_llm = AnthropicLLM(EXTRACT_MODEL)

    status("extraction")

    def extract_one(t: Talk):
        # Fresh extractor per talk: SchemaLLMPathExtractor.__call__ does
        # asyncio.run(...) per invocation, and reusing one Anthropic client's
        # httpx transport across event loops (or threads) is unsafe.
        ms = checkpointed(OUT / "methods" / f"{t.id}.json",
                          lambda: extract_methods_li(t, build_extractor(EXTRACT_MODEL)))
        # Gleaning pass (recall sweep) + per-method usage descriptions.
        enriched = checkpointed(OUT / "enrich" / f"{t.id}.json",
                                lambda: list(glean_and_describe(t, ms, extract_llm)))
        cl = checkpointed(OUT / "claims" / f"{t.id}.json",
                          lambda: extract_claims(t, extract_llm))
        return t, enriched[0], enriched[1], cl

    ordered = sorted(talks.values(), key=lambda t: t.id)
    extracted = parallel("extraction", ordered, extract_one)

    g = MethodGraph()
    name_context: dict[str, str] = {}  # normalized method name -> judge context
    talk_claims: dict[int, list] = {}
    for t, all_ms, descs, cl in extracted:  # serial: graph is not thread-safe
        talk_claims[t.id] = cl
        for m in all_ms:
            g.link_talk(t.id, m)
            key = " ".join(str(m).casefold().split())
            if key not in name_context:
                d = descs.get(m) or descs.get(key) or ""
                name_context[key] = (f'in "{t.title[:70]}": {d}' if d
                                     else f'used in "{t.title[:70]}"')

    status("similarity")
    names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
    # 0.75 (the library default) proposed zero anchor-adjacent pairs on the
    # first live run: sbert scores "self-assembly" vs "self-assembled
    # monolayers" at ~0.51 and the photocurrent-name family at 0.60-0.73.
    # The embedding gate only has to be generous enough to SHOW pairs to the
    # LLM judge — the judge is the discriminator.
    pairs = propose_pairs(names, embed=sbert_embedder(), threshold=0.50)
    status(f"similarity: {len(names)} names, {len(pairs)} proposed pairs")
    def judge_or_refusal(a: str, b: str) -> dict:
        # The API's safety layer occasionally refuses an innocuous pair
        # (observed live: "hydrogen bonding modulation" vs "intra-monomer
        # hydrogen bonding design"). Policy: no edge, loudly marked — a
        # refusal must never silently masquerade as a real verdict.
        try:
            nrm = lambda n: " ".join(n.casefold().split())  # noqa: E731
            return judge_pair(a, b, judge_llm,
                              context_a=name_context.get(nrm(a), ""),
                              context_b=name_context.get(nrm(b), ""))
        except LLMRefusal:
            status(f"REFUSAL (defaulting to no-edge): {a!r} vs {b!r}")
            return {"verdict": "unrelated",
                    "why": "API REFUSAL (stop_reason=refusal); defaulted to "
                           "no-edge, not a real judgment"}

    vs = parallel("verdicts", pairs,
                  lambda ab: checkpointed(OUT / "verdicts" / f"{pair_key(*ab)}.json",
                                          lambda: judge_or_refusal(*ab)))
    verdicts = [(a, b, v) for (a, b), v in zip(pairs, vs)]
    apply_verdicts(g, verdicts)
    g.save(OUT / "graph.json")

    status("funnel+rubric")
    cands = candidates(g, talk_id=0, min_strength=MIN_EDGE_STRENGTH)
    status(f"rubric: {len(cands)} candidates")
    anchor_digest = claims_digest(talk_claims.get(0, []))

    def rubric_one(cid: int):
        return checkpointed(
            OUT / "judgments" / f"{cid}.json",
            lambda: judge_candidate(
                anchor, talks[cid], judge_llm,
                mine_claims=anchor_digest,
                cand_claims=claims_digest(talk_claims.get(cid, []))).__dict__)

    judgments = [Judgment(**j)
                 for j in parallel("rubric", sorted(cands), rubric_one)]

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
