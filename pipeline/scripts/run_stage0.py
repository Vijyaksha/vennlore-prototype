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
from gps_engine.cascade import decide_pairs  # noqa: E402
from gps_engine.claims import claims_digest, extract_claims  # noqa: E402
from gps_engine.filing import candidate_shortlist, embed_targets, file_method  # noqa: E402
from gps_engine.physh import load_physh  # noqa: E402
from gps_engine.corpus import Talk, load_talks  # noqa: E402
from gps_engine.funnel import candidates  # noqa: E402
from gps_engine.graph import MethodGraph  # noqa: E402
from gps_engine.li_extraction import build_extractor, extract_methods_li, glean_and_describe  # noqa: E402
from gps_engine.llm import AnthropicLLM, LLMRefusal  # noqa: E402
from gps_engine.recommend import assemble  # noqa: E402
from gps_engine.rubric import Judgment, judge_candidate  # noqa: E402
from gps_engine.similarity import apply_verdicts, judge_pair, sbert_embedder  # noqa: E402

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
    for sub in ("methods", "enrich", "claims", "filings", "verdicts", "judgments"):
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

    # The anchor is an external paper: represent it as a pseudo-talk (id 0)
    # carrying its REAL published abstract (Nano Lett. 2004, 4, 1261-1265,
    # doi 10.1021/nl049421v) so talk 0 is held to the same standard as every
    # crawled talk. (Earlier stand-ins — a 3-line stub, then stub+category-
    # language method axes — starved the rubric and then made extraction go
    # generic, respectively.)
    anchor = Talk(
        id=0, title=mc["anchor"]["title"],
        abstract=(
            "The photoconductivity of nanorods self-assembled from "
            "meso-tetrakis(4-sulfonatophenyl)porphine is described. The "
            "nanorods are insulating in the dark. Upon illumination with "
            "488 nm light, the nanorods become photoconductive, exhibiting "
            "a rapid turn on/off (<100 ms) of the current when the light is "
            "turned on/off. This photoconductivity grows over hundreds of "
            "seconds with light exposure and decays slowly when the light "
            "is off. The nanorods can be trained via an applied bias to "
            "exhibit a short-circuit photocurrent (with corresponding "
            "open-circuit photovoltage) that flows in the direction "
            "opposite that of the training bias. A qualitative model is "
            "proposed, in which conduction occurs through the tightly "
            "coupled LUMOs of close-packed porphyrin molecules."),
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

    status("filing")
    names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
    physh = load_physh()
    embed = sbert_embedder()
    target_vecs = embed_targets(physh, embed)

    def file_one(name: str):
        key = " ".join(name.casefold().split())
        ctx = name_context.get(key, "")
        return checkpointed(
            OUT / "filings" / f"{pair_key(name, 'FILE')}.json",
            lambda: file_method(
                name, ctx,
                candidate_shortlist(name, ctx, physh, embed, target_vecs),
                physh, extract_llm))

    filed = parallel("filing", names, file_one)
    filings = dict(zip(names, filed))
    n_filed = sum(1 for f in filed if f)
    status(f"filing: {n_filed}/{len(names)} methods filed onto PhySH")

    status("cascade")
    texts = {n: f"{n}: {name_context.get(' '.join(n.casefold().split()), '')}"
             for n in names}
    decisions = decide_pairs(names, filings, physh, embed, texts)
    autos = [d for d in decisions if d.action in ("auto-same", "auto-related")]
    to_judge = [d for d in decisions if d.action == "judge"]
    from collections import Counter
    cascade_stats = Counter(d.provenance for d in decisions)
    status(f"cascade: {len(autos)} auto, {len(to_judge)} to judge, "
           f"{len(decisions) - len(autos) - len(to_judge)} dropped")
    pairs = [(d.a, d.b) for d in to_judge]
    evidence = {(d.a, d.b): d.evidence for d in to_judge}
    def judge_or_refusal(a: str, b: str) -> dict:
        # The API's safety layer occasionally refuses an innocuous pair
        # (observed live: "hydrogen bonding modulation" vs "intra-monomer
        # hydrogen bonding design"). Policy: no edge, loudly marked — a
        # refusal must never silently masquerade as a real verdict.
        try:
            nrm = lambda n: " ".join(n.casefold().split())  # noqa: E731
            return judge_pair(a, b, judge_llm,
                              context_a=name_context.get(nrm(a), ""),
                              context_b=name_context.get(nrm(b), ""),
                              evidence=evidence.get((a, b), ""))
        except LLMRefusal:
            status(f"REFUSAL (defaulting to no-edge): {a!r} vs {b!r}")
            return {"verdict": "unrelated",
                    "why": "API REFUSAL (stop_reason=refusal); defaulted to "
                           "no-edge, not a real judgment"}

    vs = parallel("verdicts", pairs,
                  lambda ab: checkpointed(OUT / "verdicts" / f"{pair_key(*ab)}.json",
                                          lambda: judge_or_refusal(*ab)))
    verdicts = [(a, b, v) for (a, b), v in zip(pairs, vs)]
    # tree-decided edges join the LLM verdicts with their provenance kept
    for d in autos:
        verdicts.append((d.a, d.b, {
            "verdict": "same" if d.action == "auto-same" else "related",
            "strength": d.strength, "why": d.why, "provenance": d.provenance}))
    apply_verdicts(g, verdicts)
    g.save(OUT / "graph.json")

    status("funnel+rubric")
    cands = candidates(g, talk_id=0, min_strength=MIN_EDGE_STRENGTH)
    status(f"rubric: {len(cands)} candidates")
    anchor_digest = claims_digest(talk_claims.get(0, []))

    def rubric_one(cid: int):
        def judge():
            try:
                return judge_candidate(
                    anchor, talks[cid], judge_llm,
                    mine_claims=anchor_digest,
                    cand_claims=claims_digest(talk_claims.get(cid, []))).__dict__
            except LLMRefusal:
                # Same policy as the pair judge: no match, loudly marked —
                # never fabricated, never fatal.
                status(f"REFUSAL (rubric, defaulting to no-match): talk {cid}")
                c = talks[cid]
                return {"candidate_id": cid, "same_method": 0,
                        "specificity": 0, "usage_parallel": 0, "match": False,
                        "cross_domain": bool(anchor.units) and bool(c.units)
                        and not (set(anchor.units) & set(c.units)),
                        "why": "API REFUSAL (stop_reason=refusal); defaulted "
                               "to no-match, not a real judgment"}
        return checkpointed(OUT / "judgments" / f"{cid}.json", judge)

    # Decision rule: the match verdict is OURS, derived from the scores,
    # not the LLM's own boolean. Calibrated on the 10+47 ground truth
    # (2026-08-30): positives score 5-11 total, negatives top out at 4.
    from dataclasses import replace
    MATCH_MIN_SCORE = 5
    judgments = [
        (lambda j: replace(j, match=j.score >= MATCH_MIN_SCORE))(Judgment(**j))
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
        "cascade_stats": dict(cascade_stats),
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=1))
    status("done — see pipeline/out/stage0/report.json")


if __name__ == "__main__":
    main()
