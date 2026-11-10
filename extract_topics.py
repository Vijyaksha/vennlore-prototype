"""GraphRAG step 1 (indexing): an LLM reads each session and extracts topics and methods,
which become the nodes and edges of the knowledge graph.

Input:  raw_sessions.csv with columns session_id,title,track,abstract
Output: sessions.csv with topics and methods filled in

Run (with LM Studio running, or LLM_API_URL / LLM_API_KEY / LLM_MODEL set):
    python extract_topics.py raw_sessions.csv
"""

import re
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
    hint = ", ".join(sorted(vocab)[:40]) or "none yet"
    data = llm.complete_fields(
        "From this conference session, list 2-4 research topics and 1-3 methods as short lowercase "
        f"phrases separated by semicolons. Reuse these existing phrases when they fit: {hint}\n\n"
        f"Title: {r.title}\nAbstract: {r.abstract[:1200]}",
        ["TOPICS", "METHODS"],
    ) or {"TOPICS": "", "METHODS": ""}
    t = [x.strip(" .'\"").lower() for x in re.split(r"[;,]", data["TOPICS"]) if x.strip()][:4]
    m = [x.strip(" .'\"").lower() for x in re.split(r"[;,]", data["METHODS"]) if x.strip()][:3]
    vocab.update(t + m)
    topics.append(";".join(t))
    methods.append(";".join(m))
    print(f"{r.session_id}: {t} | {m}")
df["topics"], df["methods"] = topics, methods
df.to_csv("sessions.csv", index=False)
print(f"Wrote sessions.csv with {len(df)} sessions and {len(vocab)} concepts")
