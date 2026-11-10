"""GraphRAG step 1 (indexing): an LLM reads each session and extracts topics and methods,
which become the nodes and edges of the knowledge graph.

Input:  raw_sessions.csv with columns session_id,title,track,abstract
Output: sessions.csv with topics and methods filled in

Run (with LM Studio running, or LLM_API_URL / LLM_API_KEY / LLM_MODEL set):
    python extract_topics.py raw_sessions.csv
"""

import sys

import pandas as pd

import llm

if not llm.available():
    sys.exit("No LLM found. Start LM Studio's local server, or set LLM_API_URL, LLM_API_KEY and LLM_MODEL.")
print("Using", llm.describe())

df = pd.read_csv(sys.argv[1]).fillna("")
vocab = set()  # reuse earlier names so sessions share nodes (keeps the graph connected)
topics, methods = [], []
for _, r in df.iterrows():
    hint = ", ".join(sorted(vocab)[:80]) or "none yet"
    data = (
        llm.complete_json(
            "Extract from this conference session 2-4 research TOPICS and 1-3 METHODS as short lowercase "
            "noun phrases (e.g. 'drug discovery', 'graph neural networks'). Reuse a phrase from this list "
            f"when it fits: {hint}\n\nTitle: {r.title}\nAbstract: {r.abstract}\n\n"
            'Return {"topics": [...], "methods": [...]}',
            max_tokens=300,
        )
        or {}
    )
    t = [x.strip().lower() for x in data.get("topics", []) if isinstance(x, str)]
    m = [x.strip().lower() for x in data.get("methods", []) if isinstance(x, str)]
    vocab.update(t + m)
    topics.append(";".join(t))
    methods.append(";".join(m))
    print(f"{r.session_id}: {t} | {m}")
df["topics"], df["methods"] = topics, methods
df.to_csv("sessions.csv", index=False)
print(f"Wrote sessions.csv with {len(df)} sessions and {len(vocab)} concepts")
