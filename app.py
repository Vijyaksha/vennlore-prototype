"""Vennlore Conference - GraphRAG prototype (v3).

Run:  streamlit run app.py

  graph_index.py  INDEXING   graph, text index, communities + LLM theme summaries
  retrieval.py    QUERYING   local search (recommendations) and global search (themes)
  llm.py          LLM        free local model (LM Studio / Ollama) or free cloud API, else offline
  app.py          INTERFACE  this file: three tabs + feedback
"""

import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

import llm
from graph_index import build_index
from retrieval import generate_recommendations, global_search, local_retrieve

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "sessions.csv")
CACHE_FILE = os.path.join(HERE, "communities.json")
FEEDBACK_FILE = os.path.join(HERE, "feedback.csv")


@st.cache_resource(show_spinner="Building the knowledge graph and theme summaries...")
def get_index() -> dict:
    return build_index(DATA_FILE, CACHE_FILE)


# ---------------------------------------------------------------- Feedback
def save_feedback(query: str, sid: str, kind: str, vote: str) -> None:
    new = not os.path.exists(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "query", "session_id", "kind", "vote"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), query, sid, kind, vote])
    st.session_state.voted.add((query, sid))


def feedback_summary() -> dict | None:
    if not os.path.exists(FEEDBACK_FILE):
        return None
    fb = pd.read_csv(FEEDBACK_FILE)
    if fb.empty:
        return None
    out = {"total": len(fb), "pct": 100 * (fb.vote == "up").mean()}
    for kind in ("relevant", "unexpected"):
        part = fb[fb.kind == kind]
        out[kind] = (len(part), 100 * (part.vote == "up").mean() if len(part) else 0)
    return out


# ---------------------------------------------------------------- Display helpers
MATCHING_LABEL = {"embeddings": "sentence embeddings", "tfidf": "typo-tolerant TF-IDF"}
COLORS = {"session": "#2C5DE5", "topic": "#F2A33A", "method": "#3BA272", "track": "#999999"}


def draw_paths(g: nx.Graph, seeds: list, top: list, surprise: list) -> plt.Figure:
    keep = {n for n, _ in seeds if g.nodes[n]["kind"] != "track"}
    keep |= {s for s, _ in top} | {s for s, _ in surprise}
    keep |= {"method:" + info["bridge"] for _, info in surprise}
    sub = g.subgraph(keep)
    labels = {n: (d.get("title") or d.get("label"))[:26] for n, d in sub.nodes(data=True)}
    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.spring_layout(sub, seed=7, k=1.6 / max(1, len(sub)) ** 0.5)
    nx.draw_networkx_edges(sub, pos, ax=ax, alpha=0.5, width=1.4)
    nx.draw_networkx_nodes(
        sub, pos, ax=ax, node_size=520, node_color=[COLORS[sub.nodes[n]["kind"]] for n in sub]
    )
    nx.draw_networkx_labels(
        sub, pos, labels, ax=ax, font_size=8, bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=1)
    )
    for kind in ("session", "topic", "method"):
        ax.scatter([], [], c=COLORS[kind], label=kind)
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    ax.margins(0.15)
    ax.axis("off")
    return fig


def show_rec(idx: dict, query: str, sid: str, reasons: dict, kind: str) -> None:
    g = idx["g"]
    d = g.nodes[sid]
    theme = next((c["title"] for c in idx["communities"] if c["id"] == idx["session_community"].get(sid)), "")
    st.markdown(
        f"**{d['title']}**  \n*{d['track']}*"
        + (f" · theme: {theme}" if theme else "")
        + f"  \n{reasons.get(sid, '')}"
    )
    if (query, sid) in st.session_state.voted:
        st.caption("Thanks for the feedback.")
        return
    c1, c2, _ = st.columns([1, 1, 8])
    c1.button(
        "👍", key=f"up_{sid}", help="Relevant to me", on_click=save_feedback, args=(query, sid, kind, "up")
    )
    c2.button(
        "👎", key=f"down_{sid}", help="Not relevant", on_click=save_feedback, args=(query, sid, kind, "down")
    )


# ---------------------------------------------------------------- Page
st.set_page_config(page_title="Vennlore Conference", layout="wide")
st.session_state.setdefault("voted", set())
st.session_state.setdefault("results", None)
idx = get_index()
G = idx["g"]

with st.sidebar:
    st.header("Pilot feedback")
    summary = feedback_summary()
    if summary:
        st.metric("Recommendations rated relevant", f"{summary['pct']:.0f}%", f"{summary['total']} ratings")
        for kind, name in (("relevant", "Direct matches"), ("unexpected", "Unexpected connections")):
            n, p = summary[kind]
            st.write(f"{name}: {p:.0f}% relevant ({n} ratings)" if n else f"{name}: no ratings yet")
    else:
        st.write("No ratings yet. Use 👍 / 👎 on each recommendation.")
    st.divider()
    st.caption(
        f"LLM: {llm.describe()}  \n"
        f"Matching: {MATCHING_LABEL[idx['emb'].mode]}  \n"
        f"{len(idx['df'])} sessions · {G.number_of_nodes()} nodes · {G.number_of_edges()} edges · "
        f"{len(idx['communities'])} themes"
    )
    if not llm.available():
        st.info("Start LM Studio's local server for AI-written explanations, plans and answers.")

st.title("Vennlore Conference")
st.caption("Personalized session recommendations, powered by GraphRAG")

tab_rec, tab_ask, tab_themes = st.tabs(
    ["🎯 Recommend sessions", "💬 Ask the conference", "🗺️ Research themes"]
)

# ---- Tab 1: local search
with tab_rec:
    query = st.text_area(
        "Describe your research interests, or paste an abstract:",
        "I use graph neural networks for drug discovery and protein structure",
    )
    if st.button("Recommend sessions", type="primary") and query.strip():
        with st.spinner("Searching the knowledge graph..."):
            seeds, top, surprise = local_retrieve(query, idx)
            gen = generate_recommendations(query, idx, top, surprise)
        st.session_state.results = (query, seeds, top, surprise, gen)

    if st.session_state.results:
        q, seeds, top, surprise, gen = st.session_state.results
        if not top:
            st.warning("No matching sessions found. Try describing your research differently.")
        else:
            shown = list(dict.fromkeys(G.nodes[n]["label"] for n, _ in seeds))
            if shown:
                st.write("**Matched concepts in the graph:** " + ", ".join(shown))
            if gen.get("plan"):
                st.info("**Your conference plan:** " + gen["plan"])
            col1, col2 = st.columns([3, 2])
            with col1:
                st.subheader("Recommended for you")
                for s, _ in top:
                    show_rec(idx, q, s, gen["reasons"], "relevant")
                if surprise:
                    st.subheader("Unexpected connections")
                    for s, _ in surprise:
                        show_rec(idx, q, s, gen["reasons"], "unexpected")
            with col2:
                st.subheader("Why: the graph paths")
                st.pyplot(draw_paths(G, seeds, top, surprise))
            st.caption(
                "Explanations: "
                + (
                    "written by the LLM from the retrieved graph context"
                    if gen.get("generated")
                    else "templates from the graph paths (offline)"
                )
            )

# ---- Tab 2: global search
with tab_ask:
    question = st.text_input(
        "Ask a broad question about the conference:",
        "What are the main research themes that combine AI with the physical sciences?",
    )
    if st.button("Ask", type="primary") and question.strip():
        with st.spinner("Reading theme summaries..."):
            res = global_search(question, idx)
        if res["answer"]:
            st.markdown(res["answer"])
        else:
            st.caption("No LLM running, so here are the most relevant themes from the graph:")
        st.write("**Themes used:**")
        for c in res["themes"]:
            with st.expander(f"{c['title']} ({len(c['sessions'])} sessions)"):
                st.write(c["summary"])
                st.write("Sessions: " + "; ".join(G.nodes[s]["title"] for s in c["sessions"]))

# ---- Tab 3: communities
with tab_themes:
    st.write(
        "Themes found automatically by community detection (Louvain) on the knowledge graph. "
        "Each theme groups concepts that sessions use together, often across different tracks."
    )
    for c in idx["communities"]:
        tracks = sorted({G.nodes[s]["track"] for s in c["sessions"]})
        with st.expander(f"**{c['title']}** · {len(c['sessions'])} sessions · {len(tracks)} tracks"):
            st.write(c["summary"])
            st.caption("Concepts: " + ", ".join(c["concepts"]))
            for s in c["sessions"]:
                st.write(f"- {G.nodes[s]['title']} *({G.nodes[s]['track']})*")

with st.expander("About this prototype"):
    st.write(
        "Sample sessions written for demonstration; replace sessions.csv with a real conference program "
        "(see extract_topics.py). Ratings are saved to feedback.csv. Theme summaries are cached in "
        "communities.json; delete it to regenerate."
    )
