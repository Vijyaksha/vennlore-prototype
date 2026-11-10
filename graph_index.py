"""Indexing: everything GraphRAG prepares BEFORE a user asks anything.

1. Load sessions (topics/methods come from extract_topics.py, i.e. LLM-extracted)
2. Build the knowledge graph       Session -- Topic / Method / Track
3. Build the text index            embeddings, or typo-tolerant TF-IDF as a fallback
4. Detect communities              groups of tightly connected concepts = research themes
5. Summarize each community        LLM-written theme summaries (cached in communities.json)
"""

import hashlib
import json
import os

import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.community import louvain_communities
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import llm

EMBED_MODEL = "all-MiniLM-L6-v2"


# ---------------------------------------------------------------- 1-2. Sessions and graph
def load_sessions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).fillna("")
    for col in ("topics", "methods"):
        df[col] = df[col].apply(lambda s: [x.strip().lower() for x in s.split(";") if x.strip()])
    df["doc"] = (
        df.title
        + ". "
        + df.track
        + ". "
        + df.abstract
        + " "
        + df.topics.apply(" ".join)
        + " "
        + df.methods.apply(" ".join)
    )
    return df


def build_graph(df: pd.DataFrame) -> nx.Graph:
    g = nx.Graph()
    for _, r in df.iterrows():
        sid = r.session_id
        g.add_node(sid, kind="session", title=r.title, track=r.track, abstract=r.abstract)
        g.add_node("track:" + r.track, kind="track", label=r.track.lower())
        g.add_edge(sid, "track:" + r.track, rel="in_track")
        for t in r.topics:
            g.add_node("topic:" + t, kind="topic", label=t)
            g.add_edge(sid, "topic:" + t, rel="about")
        for m in r.methods:
            g.add_node("method:" + m, kind="method", label=m)
            g.add_edge(sid, "method:" + m, rel="uses")
    return g


# ---------------------------------------------------------------- 3. Text index
class Embedder:
    """Sentence embeddings if installed (best), otherwise character TF-IDF (typo-tolerant)."""

    def __init__(self, corpus: list[str]):
        self.mode = "tfidf"
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(EMBED_MODEL)
            self.mode = "embeddings"
        except Exception:
            self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
            self.vec.fit(corpus)

    def encode(self, texts):
        if self.mode == "embeddings":
            return self.model.encode(list(texts), normalize_embeddings=True)
        return self.vec.transform(list(texts))

    def sim(self, query, matrix):
        q = self.encode([query])
        if self.mode == "embeddings":
            return np.asarray(matrix @ q[0]).ravel()
        return cosine_similarity(q, matrix)[0]


# ---------------------------------------------------------------- 4-5. Communities
def detect_communities(g: nx.Graph, seed: int = 7) -> list[dict]:
    """Louvain community detection on the concept graph: two concepts are linked when
    sessions share them. Each community is a research theme spanning sessions."""
    concept_graph = nx.Graph()
    for s, d in g.nodes(data=True):
        if d["kind"] != "session":
            continue
        concepts = [n for n in g.neighbors(s) if g.nodes[n]["kind"] in ("topic", "method")]
        for i, a in enumerate(concepts):
            concept_graph.add_node(a)
            for b in concepts[i + 1 :]:
                w = concept_graph.get_edge_data(a, b, {"weight": 0})["weight"]
                concept_graph.add_edge(a, b, weight=w + 1)
    groups = louvain_communities(concept_graph, weight="weight", seed=seed)
    communities = []
    for i, nodes in enumerate(sorted(groups, key=len, reverse=True)):
        sessions = sorted({s for n in nodes for s in g.neighbors(n) if g.nodes[s]["kind"] == "session"})
        communities.append(
            {
                "id": f"C{i + 1}",
                # most-shared concepts first: they best describe the theme
                "concepts": [g.nodes[n]["label"] for n in sorted(nodes, key=lambda n: (-g.degree(n), n))],
                "sessions": sessions,
            }
        )
    return communities


def _fallback_summary(c: dict, g: nx.Graph) -> dict:
    titles = [g.nodes[s]["title"] for s in c["sessions"]]
    tracks = sorted({g.nodes[s]["track"] for s in c["sessions"]})
    return {
        "title": " / ".join(c["concepts"][:3]).title(),
        "summary": (
            f"Sessions in {', '.join(tracks)} connected by {', '.join(c['concepts'][:6])}. "
            f"Includes: {'; '.join(titles[:4])}."
        ),
    }


def summarize_communities(
    communities: list[dict], g: nx.Graph, cache_path: str, data_hash: str
) -> list[dict]:
    """LLM writes a title and 2-3 sentence summary per theme. Cached so it runs once per dataset."""
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cached = json.load(f)
        if cached.get("data_hash") == data_hash and cached.get("llm") == llm.available():
            return cached["communities"]
    for c in communities:
        result = None
        if llm.available():
            sessions = "\n".join(
                f"- {g.nodes[s]['title']} ({g.nodes[s]['track']}): {g.nodes[s]['abstract']}"
                for s in c["sessions"]
            )
            result = llm.complete_json(
                "These conference sessions form one research theme, linked by the concepts: "
                f"{', '.join(c['concepts'])}.\n{sessions}\n\n"
                'Return {"title": "<theme name, max 6 words>", "summary": "<2-3 sentences: what ties '
                'these sessions together and who should attend>"}',
                max_tokens=400,
            )
        c.update(result if isinstance(result, dict) and "summary" in result else _fallback_summary(c, g))
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"data_hash": data_hash, "llm": llm.available(), "communities": communities}, f, indent=2)
    return communities


# ---------------------------------------------------------------- Build everything
def build_index(sessions_path: str, cache_path: str) -> dict:
    df = load_sessions(sessions_path)
    g = build_graph(df)
    concepts = [n for n, d in g.nodes(data=True) if d["kind"] in ("topic", "method", "track")]
    labels = [g.nodes[n]["label"] for n in concepts]
    emb = Embedder(list(df.doc) + labels)
    with open(sessions_path, "rb") as f:
        data_hash = hashlib.md5(f.read()).hexdigest()
    communities = summarize_communities(detect_communities(g), g, cache_path, data_hash)
    session_community = {s: c["id"] for c in communities for s in c["sessions"]}
    return {
        "df": df,
        "g": g,
        "emb": emb,
        "sessions": list(df.session_id),
        "session_mat": emb.encode(df.doc),
        "concepts": concepts,
        "concept_mat": emb.encode(labels),
        "communities": communities,
        "session_community": session_community,
        "community_mat": emb.encode(
            [c["title"] + ". " + c["summary"] + " " + " ".join(c["concepts"]) for c in communities]
        ),
    }
