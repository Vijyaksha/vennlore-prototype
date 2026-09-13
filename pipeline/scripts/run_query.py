# pipeline/scripts/run_query.py
"""Query the Stage-1 graph with an external anchor paper. GATED: live LLM
spend — run only with Rupert's go and DEEPSEEK_API_KEY set.

Usage: uv run python scripts/run_query.py <anchor.json>
  anchor.json: {"title": "...", "abstract": "..."}

Flow: anchor extraction/gleaning/claims -> PhySH filing -> bipartite cascade
(anchor methods x indexed methods) -> pair verdicts -> funnel walk from the
anchor -> deepseek-reasoner rubric with claims -> ranked recommendations.
Checkpoints under out/query-<slug>/ keyed by the anchor title; rerun resumes.
Progress probeable at out/query-<slug>/status.json."""
import hashlib
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engine.cascade import decide_pairs_cross  # noqa: E402
from gps_engine.claims import claims_digest, extract_claims  # noqa: E402
from gps_engine.corpus import Talk, load_talks  # noqa: E402
from gps_engine.filing import candidate_shortlist, embed_targets, file_method  # noqa: E402
from gps_engine.funnel import candidates  # noqa: E402
from gps_engine.graph import MethodGraph  # noqa: E402
from gps_engine.li_extraction import extract_methods_json, glean_and_describe  # noqa: E402
from gps_core.llm import DeepSeekLLM, LLMRefusal  # noqa: E402
from gps_engine.physh import load_physh  # noqa: E402
from gps_engine.rubric import judge_candidate  # noqa: E402
from gps_engine.similarity import apply_verdicts, judge_pair, sbert_embedder  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INDEX = Path(__file__).resolve().parents[1] / "out" / "stage1-deepseek"
EXTRACT_MODEL = "deepseek-chat"
PAIR_JUDGE_MODEL = "deepseek-chat"
RUBRIC_MODEL = "deepseek-reasoner"
MATCH_MIN_SCORE = 5   # calibrated on the 10+47 ground truth
WORKERS = 24
ANCHOR_ID = 0
t0 = time.time()


def main() -> None:
    anchor_spec = json.loads(Path(sys.argv[1]).read_text())
    slug = re.sub(r"[^a-z0-9]+", "-",
                  anchor_spec["title"].lower())[:48].strip("-")
    out = Path(__file__).resolve().parents[1] / "out" / f"query-{slug}"
    out.mkdir(parents=True, exist_ok=True)
    for sub in ("verdicts", "judgments"):
        (out / sub).mkdir(exist_ok=True)

    def status(msg: str) -> None:
        (out / "status.json").write_text(json.dumps(
            {"phase": msg, "elapsed_s": round(time.time() - t0)}))
        print(f"[{round(time.time() - t0)}s] {msg}", flush=True)

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

    sample = json.loads((ROOT / "datasets" / "sample-500.json").read_text())
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=set(sample["ids"]))
    anchor = Talk(id=ANCHOR_ID, title=anchor_spec["title"],
                  abstract=anchor_spec["abstract"], topics=(),
                  units=tuple(anchor_spec.get("units", [])),
                  session_title="", start=None, end=None)
    talks[ANCHOR_ID] = anchor

    g = MethodGraph.load(INDEX / "graph.json")
    name_context = json.loads((INDEX / "name_context.json").read_text())
    extract_llm = DeepSeekLLM(EXTRACT_MODEL)
    pair_llm = DeepSeekLLM(PAIR_JUDGE_MODEL)
    rubric_llm = DeepSeekLLM(RUBRIC_MODEL)

    status("anchor extraction")
    ms = checkpointed(out / "methods.json",
                      lambda: extract_methods_json(anchor, extract_llm))
    all_ms, descs = checkpointed(
        out / "enrich.json",
        lambda: list(glean_and_describe(anchor, ms, extract_llm)))
    anchor_claims = checkpointed(out / "claims.json",
                                 lambda: extract_claims(anchor, extract_llm))
    status(f"anchor methods: {all_ms}")

    existing = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
    new_names = [m for m in all_ms if m not in existing]
    for m in all_ms:
        g.link_talk(ANCHOR_ID, m)
        key = " ".join(str(m).casefold().split())
        if key not in name_context:
            d = descs.get(m) or descs.get(key) or ""
            name_context[key] = (f'in "{anchor.title[:70]}": {d}' if d
                                 else f'used in "{anchor.title[:70]}"')

    status("anchor filing + bipartite cascade")
    physh = load_physh()
    embed = sbert_embedder()
    target_vecs = embed_targets(physh, embed)
    filings = {}
    def file_lookup(name):
        p = INDEX / "filings" / f"{pair_key(name, 'FILE')}.json"
        if p.exists():
            return json.loads(p.read_text())
        return None
    for n in existing:
        filings[n] = file_lookup(n) or []
    for n in new_names:
        key = " ".join(n.casefold().split())
        ctx = name_context.get(key, "")
        filings[n] = checkpointed(
            out / f"filing-{pair_key(n, 'FILE')}.json",
            lambda n=n, ctx=ctx: file_method(
                n, ctx, candidate_shortlist(n, ctx, physh, embed, target_vecs),
                physh, extract_llm))

    texts = {n: f"{n}: {name_context.get(' '.join(n.casefold().split()), '')}"
             for n in set(existing) | set(all_ms)}
    ds = decide_pairs_cross(all_ms, existing, filings, physh, embed, texts)
    autos = [d for d in ds if d.action in ("auto-same", "auto-related")]
    to_judge = [d for d in ds if d.action == "judge"]
    status(f"cascade: {len(autos)} auto, {len(to_judge)} to judge")

    evidence = {(d.a, d.b): d.evidence for d in to_judge}

    def judge_or_refusal(a: str, b: str) -> dict:
        try:
            nrm = lambda n: " ".join(n.casefold().split())  # noqa: E731
            return judge_pair(a, b, pair_llm,
                              context_a=name_context.get(nrm(a), ""),
                              context_b=name_context.get(nrm(b), ""),
                              evidence=evidence.get((a, b), ""))
        except LLMRefusal:
            status(f"REFUSAL (defaulting to no-edge): {a!r} vs {b!r}")
            return {"verdict": "unrelated",
                    "why": "API REFUSAL; defaulted to no-edge"}

    pairs = [(d.a, d.b) for d in to_judge]
    vs = parallel("verdicts", pairs,
                  lambda ab: checkpointed(out / "verdicts" / f"{pair_key(*ab)}.json",
                                          lambda: judge_or_refusal(*ab)))
    verdicts = [(a, b, v) for (a, b), v in zip(pairs, vs)]
    for d in autos:
        verdicts.append((d.a, d.b, {
            "verdict": "same" if d.action == "auto-same" else "related",
            "strength": d.strength, "why": d.why, "provenance": d.provenance}))
    apply_verdicts(g, verdicts)

    cands = candidates(g, talk_id=ANCHOR_ID, min_strength=0)
    status(f"rubric: {len(cands)} funnel candidates")
    claims_by_talk = {}
    for cid in cands:
        p = INDEX / "claims" / f"{cid}.json"
        claims_by_talk[cid] = json.loads(p.read_text()) if p.exists() else []
    anchor_digest = claims_digest(anchor_claims)

    def rubric_one(cid: int):
        def judge():
            try:
                return judge_candidate(
                    anchor, talks[cid], rubric_llm,
                    mine_claims=anchor_digest,
                    cand_claims=claims_digest(claims_by_talk.get(cid, []))
                ).__dict__
            except LLMRefusal:
                status(f"REFUSAL (rubric, defaulting to no-match): talk {cid}")
                c = talks[cid]
                return {"candidate_id": cid, "same_method": 0,
                        "specificity": 0, "usage_parallel": 0, "match": False,
                        "cross_domain": bool(anchor.units) and bool(c.units)
                        and not (set(anchor.units) & set(c.units)),
                        "why": "API REFUSAL; defaulted to no-match"}
        return checkpointed(out / "judgments" / f"{cid}.json", judge)

    judgments = parallel("rubric", sorted(cands), rubric_one)
    rows = []
    for j in judgments:
        score = j["same_method"] + j["specificity"] + j["usage_parallel"]
        t = talks[j["candidate_id"]]
        rows.append({**j, "score": score, "match": score >= MATCH_MIN_SCORE,
                     "title": t.title, "units": list(t.units),
                     "session": t.session_title})
    rows.sort(key=lambda r: (-r["score"], r["candidate_id"]))
    (out / "recommendations.json").write_text(json.dumps(rows, indent=1))
    n_match = sum(1 for r in rows if r["match"])
    status(f"done — {n_match} matches of {len(rows)} candidates; "
           f"see {out / 'recommendations.json'}")


if __name__ == "__main__":
    main()
