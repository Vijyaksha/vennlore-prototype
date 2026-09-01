# pipeline/scripts/run_stage1_index.py
"""Stage-1 graph build over the stratified 500-talk sample. GATED: live LLM
spend — run only with Rupert's go and DEEPSEEK_API_KEY set.
Checkpoints every artifact (skip-if-exists); rerun resumes.
Progress probeable at pipeline/out/stage1-deepseek/status.json.

Indexing only: extraction -> gleaning+descriptions -> claims -> PhySH filing
-> edge cascade -> graph.json. The query flow (anchor paper -> funnel ->
rubric) is a separate script run when the anchor arrives."""
import hashlib
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

from gps_engine.cascade import decide_pairs_bulk  # noqa: E402
from gps_engine.claims import extract_claims  # noqa: E402
from gps_engine.corpus import Talk, load_talks  # noqa: E402
from gps_engine.filing import candidate_shortlist, embed_targets, file_method  # noqa: E402
from gps_engine.graph import MethodGraph  # noqa: E402
from gps_engine.li_extraction import extract_methods_json, glean_and_describe  # noqa: E402
from gps_engine.llm import DeepSeekLLM, LLMRefusal  # noqa: E402
from gps_engine.physh import load_physh  # noqa: E402
from gps_engine.similarity import apply_verdicts, judge_pair, sbert_embedder  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out" / "stage1-deepseek"
EXTRACT_MODEL = "deepseek-chat"
PAIR_JUDGE_MODEL = "deepseek-chat"   # narrow task with structural evidence;
                                     # the 10/10 funnel recall was achieved
                                     # on chat pair-verdicts (reasoner is
                                     # reserved for the query-time rubric)
WORKERS = 24
t0 = time.time()


def status(msg: str) -> None:
    (OUT / "status.json").write_text(json.dumps(
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
            if done % 25 == 0 or done == len(items):
                status(f"{label} {done}/{len(items)}")
        return r

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(wrapped, items))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ("methods", "enrich", "claims", "filings", "verdicts"):
        (OUT / sub).mkdir(exist_ok=True)

    sample = json.loads((ROOT / "datasets" / "sample-500.json").read_text())
    ids = set(sample["ids"])
    talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)
    missing = ids - set(talks)
    if missing:
        raise SystemExit(f"sample ids missing from archive: {sorted(missing)[:10]}")
    status(f"loaded {len(talks)} talks")

    extract_llm = DeepSeekLLM(EXTRACT_MODEL)
    judge_llm = DeepSeekLLM(PAIR_JUDGE_MODEL)

    status("extraction")

    def extract_one(t: Talk):
        ms = checkpointed(OUT / "methods" / f"{t.id}.json",
                          lambda: extract_methods_json(t, extract_llm))
        enriched = checkpointed(OUT / "enrich" / f"{t.id}.json",
                                lambda: list(glean_and_describe(t, ms, extract_llm)))
        checkpointed(OUT / "claims" / f"{t.id}.json",
                     lambda: extract_claims(t, extract_llm))
        return t, enriched[0], enriched[1]

    ordered = sorted(talks.values(), key=lambda t: t.id)
    extracted = parallel("extraction", ordered, extract_one)

    g = MethodGraph()
    name_context: dict[str, str] = {}
    for t, all_ms, descs in extracted:  # serial: graph is not thread-safe
        for m in all_ms:
            g.link_talk(t.id, m)
            key = " ".join(str(m).casefold().split())
            if key not in name_context:
                d = descs.get(m) or descs.get(key) or ""
                name_context[key] = (f'in "{t.title[:70]}": {d}' if d
                                     else f'used in "{t.title[:70]}"')

    status("filing")
    names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
    status(f"filing: {len(names)} distinct method names")
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
    status(f"filing: {sum(1 for f in filed if f)}/{len(names)} filed onto PhySH")

    status("cascade (bulk decide)")
    texts = {n: f"{n}: {name_context.get(' '.join(n.casefold().split()), '')}"
             for n in names}
    kept, n_dropped = decide_pairs_bulk(names, filings, physh, embed, texts)
    autos = [d for d in kept if d.action in ("auto-same", "auto-related")]
    to_judge = [d for d in kept if d.action == "judge"]
    status(f"cascade: {len(autos)} auto, {len(to_judge)} to judge, "
           f"{n_dropped} dropped")

    evidence = {(d.a, d.b): d.evidence for d in to_judge}

    def judge_or_refusal(a: str, b: str) -> dict:
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

    pairs = [(d.a, d.b) for d in to_judge]
    vs = parallel("verdicts", pairs,
                  lambda ab: checkpointed(OUT / "verdicts" / f"{pair_key(*ab)}.json",
                                          lambda: judge_or_refusal(*ab)))
    verdicts = [(a, b, v) for (a, b), v in zip(pairs, vs)]
    for d in autos:
        verdicts.append((d.a, d.b, {
            "verdict": "same" if d.action == "auto-same" else "related",
            "strength": d.strength, "why": d.why, "provenance": d.provenance}))
    apply_verdicts(g, verdicts)
    g.save(OUT / "graph.json")
    (OUT / "name_context.json").write_text(json.dumps(name_context))
    n_edges = sum(1 for _, _, v in verdicts if v.get("verdict") != "unrelated")
    status(f"done — graph saved: {len(names)} methods, {n_edges} edges "
           f"({len(autos)} tree-auto), {len(talks)} talks")


if __name__ == "__main__":
    main()
