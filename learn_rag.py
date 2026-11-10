"""LEARN RAG IN 40 LINES  -  run:  python learn_rag.py

Plain RAG (Retrieval-Augmented Generation) has exactly three steps:
  STEP 1  INDEX     turn every document into numbers (vectors)          - done once
  STEP 2  RETRIEVE  turn the question into a vector, find the closest documents
  STEP 3  GENERATE  give ONLY those documents to an LLM and ask it to answer

Read each step, run the file, then try the exercises at the bottom.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import llm

QUESTION = "machine learning in quantum computing"
K = 3  # how many documents to retrieve

# ---------------------------------------------------------------- STEP 1: INDEX
docs = pd.read_csv("sessions.csv").fillna("")
texts = (docs.title + ". " + docs.abstract).tolist()
vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
doc_vectors = vectorizer.fit_transform(texts)  # one row of numbers per session
print(f"STEP 1  Indexed {len(texts)} documents into vectors of size {doc_vectors.shape[1]}\n")

# ---------------------------------------------------------------- STEP 2: RETRIEVE
question_vector = vectorizer.transform([QUESTION])
scores = cosine_similarity(question_vector, doc_vectors)[0]  # 0 = unrelated, 1 = identical
best = scores.argsort()[::-1][:K]  # indices of the top K
print(f"STEP 2  Top {K} documents for: '{QUESTION}'")
for i in best:
    print(f"   score {scores[i]:.2f}  {docs.title[i]}")

# ---------------------------------------------------------------- STEP 3: GENERATE
context = "\n".join(f"[{docs.session_id[i]}] {docs.title[i]}: {docs.abstract[i]}" for i in best)
prompt = (
    f"Answer using ONLY these conference sessions. Cite session ids.\n\n{context}\n\n"
    f"Question: Which sessions should someone interested in '{QUESTION}' attend, and why?"
)
print(
    "\nSTEP 3  The prompt sent to the LLM (this is the 'augmented' part):\n"
    + "-" * 60
    + f"\n{prompt}\n"
    + "-" * 60
)
answer = llm.complete(prompt)
print(
    "\nLLM answer:\n" + (answer or "(No LLM running. Start LM Studio's server to see the generated answer.)")
)

# ---------------------------------------------------------------- EXERCISES (do these yourself)
# 1. Change K to 1, then to 10. What happens to the prompt and the answer? Why might too many hurt?
# 2. Change QUESTION to "GPU kernels and distributed training". Are the top 3 sensible?
# 3. Type a question with a typo ("quantim computng"). Does retrieval still work? Why? (hint: char_wb)
# 4. Hard one: plain RAG here never returns "Bayesian Optimization for Materials Discovery" for the
#    quantum question, but our GraphRAG app can. What does the graph know that these vectors don't?
