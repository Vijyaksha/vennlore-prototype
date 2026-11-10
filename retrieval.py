"""Query time: GraphRAG retrieval + generation.

Local search  - for a specific attendee: match concepts -> walk the graph -> rank sessions,
                find cross-field sessions -> LLM writes grounded reasons and a short plan.
Global search - for broad questions ("what are the big themes?"): rank community
                summaries -> LLM answers from them (map-reduce style).
"""

import numpy as np

import llm

CONCEPT_THRESHOLD = {"embeddings": 0.45, "tfidf": 0.45}
TEXT_FLOOR = {"embeddings": 0.25, "tfidf": 0.08}


# ---------------------------------------------------------------- Local search: retrieval
def match_concepts(query: str, idx: dict, top_k: int = 8) -> list[tuple[str, float]]:
    emb = idx["emb"]
    sims = emb.sim(query, idx["concept_mat"])
    thr = CONCEPT_THRESHOLD[emb.mode]
    return [(idx["concepts"][i], float(sims[i])) for i in np.argsort(-sims)[:top_k] if sims[i] >= thr]


def local_retrieve(query: str, idx: dict, n_relevant: int = 5, n_unexpected: int = 2) -> tuple:
    g, emb = idx["g"], idx["emb"]
    seeds = match_concepts(query, idx)
    seed_ids = {n for n, _ in seeds}
    text_sim = dict(zip(idx["sessions"], emb.sim(query, idx["session_mat"]), strict=True))

    # score = text similarity + 0.5 x strength of each matched concept the session links to (1 hop)
    scores = {sid: {"score": float(s), "via": []} for sid, s in text_sim.items() if s >= TEXT_FLOOR[emb.mode]}
    for concept, sim in seeds:
        for sid in g.neighbors(concept):
            if g.nodes[sid]["kind"] == "session":
                entry = scores.setdefault(sid, {"score": float(text_sim[sid]), "via": []})
                entry["score"] += 0.5 * sim
                entry["via"].append(g.nodes[concept]["label"])
    top = sorted(scores.items(), key=lambda x: -x[1]["score"])[:n_relevant]
    if top:
        best = top[0][1]["score"]
        top = [(s, i) for s, i in top if i["score"] >= 0.25 * best]
    top_ids = {s for s, _ in top}
    top_tracks = {g.nodes[s]["track"] for s in top_ids}

    # 3 hops: relevant session -> shared method -> session in a DIFFERENT track
    unexpected = {}
    for s, info in top:
        for m in g.neighbors(s):
            if g.nodes[m]["kind"] != "method" or m in seed_ids:
                continue
            for other in g.neighbors(m):
                d = g.nodes[other]
                if d["kind"] != "session" or other in top_ids or d["track"] in top_tracks:
                    continue
                score = info["score"] * 0.5
                if other not in unexpected or unexpected[other]["score"] < score:
                    unexpected[other] = {"score": score, "bridge": g.nodes[m]["label"], "from": s}
    surprise = sorted(unexpected.items(), key=lambda x: -x[1]["score"])[:n_unexpected]
    return seeds, top, surprise


# ---------------------------------------------------------------- Local search: generation
def template_reason(g, sid: str, info: dict, unexpected: bool = False) -> str:
    if unexpected:
        return (
            f"A different field ({g.nodes[sid]['track']}), but it uses {info['bridge']}, the same method "
            f"as \"{g.nodes[info['from']]['title']}\", which matches your interests."
        )
    if info["via"]:
        return "Matches your interest in " + ", ".join(dict.fromkeys(info["via"])) + "."
    return "Closely related to how you described your research."


def path_text(g, sid: str, info: dict, unexpected: bool) -> str:
    if unexpected:
        return (
            f"your interests -> \"{g.nodes[info['from']]['title']}\" -> method: {info['bridge']} "
            f"-> this session (track: {g.nodes[sid]['track']})"
        )
    return (
        "your interests -> "
        + (", ".join(dict.fromkeys(info["via"])) or "similar wording")
        + " -> this session"
    )


def build_context(idx: dict, top: list, surprise: list) -> list[dict]:
    """The retrieved graph context handed to the LLM: sessions, abstracts, paths and themes."""
    g = idx["g"]
    themes = {c["id"]: c for c in idx["communities"]}
    items = []
    for kind, results in (("relevant", top), ("unexpected", surprise)):
        for sid, info in results:
            theme = themes.get(idx["session_community"].get(sid), {})
            items.append(
                {
                    "id": sid,
                    "kind": kind,
                    "title": g.nodes[sid]["title"],
                    "track": g.nodes[sid]["track"],
                    "abstract": g.nodes[sid]["abstract"],
                    "graph_path": path_text(g, sid, info, kind == "unexpected"),
                    "theme": theme.get("title", ""),
                }
            )
    return items


def generate_recommendations(query: str, idx: dict, top: list, surprise: list) -> dict:
    """GraphRAG generation: the LLM sees ONLY the retrieved context, so its reasons stay grounded."""
    g = idx["g"]
    fallback = {
        "reasons": {s: template_reason(g, s, i) for s, i in top}
        | {s: template_reason(g, s, i, True) for s, i in surprise},
        "plan": None,
        "generated": False,
    }
    if not llm.available() or not top:
        return fallback
    context = build_context(idx, top, surprise)
    lines = "\n".join(f"{c['id']} | {c['title']} | {c['track']} | link: {c['graph_path']}" for c in context)
    ids = [c["id"] for c in context]
    out = llm.complete_lines(
        f'An attendee researches: "{query}"\n\nSessions found for them in our knowledge graph:\n{lines}\n\n'
        "For EACH session write one short sentence on why it fits, based on its link. "
        "Use exactly this format, one line per session:\n"
        + "\n".join(f"{i} | <reason>" for i in ids)
        + "\nThen one last line:\nPLAN | <2 sentences on which sessions to attend first and why>",
        ids + ["PLAN"],
    )
    reasons = {k: v for k, v in out.items() if k in ids and 10 <= len(v) <= 400}
    if not reasons:
        return fallback
    return {"reasons": fallback["reasons"] | reasons, "plan": out.get("PLAN"), "generated": True}


# ---------------------------------------------------------------- Global search
def global_search(question: str, idx: dict, top_k: int = 3) -> dict:
    """Answer broad questions from community (theme) summaries."""
    sims = idx["emb"].sim(question, idx["community_mat"])
    ranked = [idx["communities"][i] for i in np.argsort(-sims)[:top_k]]
    if not llm.available():
        return {"answer": None, "themes": ranked}
    themes = "\n".join(
        f"- {c['title']}: {c['summary'][:300]} Sessions: "
        + "; ".join(idx["g"].nodes[s]["title"] for s in c["sessions"][:5])
        for c in ranked
    )
    answer = llm.complete(
        f"Conference research themes:\n{themes}\n\nUsing ONLY these themes, answer in 3-5 sentences and "
        f"name the themes and sessions you use.\nQuestion: {question}",
        max_tokens=500,
    )
    return {"answer": answer, "themes": ranked}
