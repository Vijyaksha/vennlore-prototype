# Stage-0 Matching Engine Implementation Plan (Plan 1 of 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the methods-only graph + GraphRAG recommendation engine and prove it against the ground-truth micro-corpus (anchor ↔ 10 positives, silence on ~50 negatives).

**Architecture:** A Python package (`pipeline/`) with a strict LLM boundary: every module is unit-tested with a `FakeLLM`; live LLM calls happen only in gated scripts. Flow: corpus → method extraction (LlamaIndex PropertyGraphIndex, schema-constrained) → method graph (merge/related edges via LLM verdicts) → funnel (graph traversal) → interrogation rubric → threshold-gated picks. Graph persists to JSON artifacts in Stage 0; the Postgres loader belongs to Plan 2.

**Tech Stack:** Python 3.12, uv, pytest, `anthropic`, `sentence-transformers` (local embeddings for pair proposal). Extraction uses our own schema-constrained prompt ("Path B", Rupert-approved 2026-08-26 — no LlamaIndex dependency). Models: `claude-haiku-4-5-20251001` for extraction, `claude-sonnet-5` for similarity verdicts and rubric (revisit empirically).

**Rules that bind every task (from CLAUDE.md):** failing test first, watch it fail, minimal code, commit. Scripts that call live LLMs or download data are **gated on Rupert's go**, checkpoint incrementally, and expose probeable progress. Running pytest is always allowed.

**File structure:**

```
pipeline/
  pyproject.toml
  src/gps_engine/
    __init__.py
    llm.py          # LLMClient protocol, FakeLLM, AnthropicLLM
    corpus.py       # Talk dataclass, archive + micro-corpus loading
    graph.py        # MethodGraph: talk→method links, merge, RELATED_TO, JSON persistence
    extraction.py   # extract_methods() — our schema-constrained extraction prompt
    similarity.py   # propose_pairs (embeddings) + judge_pair (LLM) + apply_verdicts
    funnel.py       # candidate talks via graph traversal
    rubric.py       # interrogation rubric judgment of one candidate
    recommend.py    # threshold-gated pick assembly (1–2 core + 2–3 unexpected)
  tests/
    conftest.py     # tiny synthetic talks + FakeLLM fixtures
    test_corpus.py test_graph.py test_extraction.py test_similarity.py
    test_funnel.py test_rubric.py test_recommend.py
  scripts/
    select_negatives.py   # proposes ~50 negatives for review
    run_stage0.py         # gated, checkpointed end-to-end eval on micro-corpus
```

---

### Task 1: Python project scaffold

**Files:**
- Create: `pipeline/pyproject.toml`, `pipeline/src/gps_engine/__init__.py`, `pipeline/tests/test_scaffold.py`

- [ ] **Step 1: Write the failing test**

```python
# pipeline/tests/test_scaffold.py
def test_package_imports():
    import gps_engine
    assert gps_engine.__version__ == "0.1.0"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd pipeline && uv run pytest tests/test_scaffold.py -v` — Expected: FAIL (no module `gps_engine`). If `uv` is missing, install per https://docs.astral.sh/uv/ (`brew install uv`).

- [ ] **Step 3: Create the project**

```toml
# pipeline/pyproject.toml
[project]
name = "gps-engine"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["anthropic>=0.40"]

[dependency-groups]
dev = ["pytest>=8"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/gps_engine"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# pipeline/src/gps_engine/__init__.py
__version__ = "0.1.0"
```

- [ ] **Step 4: Run test to verify it passes** — `cd pipeline && uv run pytest -v` → PASS
- [ ] **Step 5: Commit** — `git add pipeline && git commit -m "feat(pipeline): scaffold gps-engine package"`

---

### Task 2: LLM boundary (`llm.py`)

**Files:** Create: `pipeline/src/gps_engine/llm.py`, `pipeline/tests/test_llm.py`

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/test_llm.py
import json
import pytest
from gps_engine.llm import FakeLLM

def test_fake_llm_returns_queued_json():
    llm = FakeLLM(responses=[{"methods": ["DMRG"]}])
    assert llm.complete_json("extract", schema_hint="methods") == {"methods": ["DMRG"]}

def test_fake_llm_records_prompts():
    llm = FakeLLM(responses=[{"ok": True}])
    llm.complete_json("hello world", schema_hint="x")
    assert "hello world" in llm.prompts[0]

def test_fake_llm_exhausted_raises():
    llm = FakeLLM(responses=[])
    with pytest.raises(IndexError):
        llm.complete_json("p", schema_hint="x")
```

- [ ] **Step 2: Run to verify FAIL** — `uv run pytest tests/test_llm.py -v` → import error.
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/llm.py
"""LLM boundary. Everything above this module is deterministic and unit-tested
with FakeLLM; AnthropicLLM is exercised only by gated scripts."""
import json
import os
from typing import Protocol


class LLMClient(Protocol):
    def complete_json(self, prompt: str, schema_hint: str) -> dict: ...


class FakeLLM:
    def __init__(self, responses: list[dict]):
        self._responses = list(responses)
        self.prompts: list[str] = []

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        self.prompts.append(prompt)
        if not self._responses:
            raise IndexError("FakeLLM has no queued responses")
        return self._responses.pop(0)


class AnthropicLLM:
    def __init__(self, model: str, max_tokens: int = 1024):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model
        self._max_tokens = max_tokens

    def complete_json(self, prompt: str, schema_hint: str) -> dict:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system="Respond with a single JSON object and nothing else. "
                   f"Expected shape: {schema_hint}",
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        return json.loads(text)
```

- [ ] **Step 4: Verify PASS** — `uv run pytest tests/test_llm.py -v`
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): LLM boundary with FakeLLM and AnthropicLLM"`

---

### Task 3: Corpus loading (`corpus.py`)

**Files:** Create: `pipeline/src/gps_engine/corpus.py`, `pipeline/tests/test_corpus.py`, `pipeline/tests/conftest.py`

- [ ] **Step 1: Write fixtures + failing tests**

```python
# pipeline/tests/conftest.py
import json
import pytest

@pytest.fixture
def archive(tmp_path):
    """Mimics data/gps2026 layout: events/*.json + presentations/*.json."""
    (tmp_path / "events").mkdir()
    (tmp_path / "presentations").mkdir()
    (tmp_path / "events" / "1.json").write_text(json.dumps({
        "id": 1, "title": "Session A", "sponsor_units": ["DCMP"],
        "presentation_ids": [10, 11],
        "periods": [{"start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T16:24:00.000Z"}],
    }))
    for pid, title in [(10, "Talk ten"), (11, "Talk eleven")]:
        (tmp_path / "presentations" / f"{pid}.json").write_text(json.dumps({
            "id": pid, "title": title, "abstract": f"Abstract of {title}.",
            "is_withdrawn": False, "topics": ["Condensed Matter"],
            "start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T14:12:00.000Z",
        }))
    return tmp_path
```

```python
# pipeline/tests/test_corpus.py
from gps_engine.corpus import load_talks

def test_load_talks_joins_session_metadata(archive):
    talks = load_talks(archive)
    t = talks[10]
    assert t.title == "Talk ten"
    assert t.units == ("DCMP",)
    assert t.session_title == "Session A"

def test_load_talks_skips_withdrawn(archive):
    import json
    p = archive / "presentations" / "10.json"
    rec = json.loads(p.read_text()); rec["is_withdrawn"] = True
    p.write_text(json.dumps(rec))
    assert 10 not in load_talks(archive)

def test_load_talks_subset(archive):
    talks = load_talks(archive, only_ids={11})
    assert set(talks) == {11}
```

- [ ] **Step 2: Run to verify FAIL** — `uv run pytest tests/test_corpus.py -v`
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/corpus.py
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Talk:
    id: int
    title: str
    abstract: str
    topics: tuple[str, ...]
    units: tuple[str, ...]
    session_title: str
    start: str | None
    end: str | None


def load_talks(archive: Path, only_ids: set[int] | None = None) -> dict[int, Talk]:
    sess_by_pid: dict[int, dict] = {}
    for f in (archive / "events").glob("*.json"):
        e = json.loads(f.read_text())
        for pid in e.get("presentation_ids", []):
            sess_by_pid[pid] = e
    talks: dict[int, Talk] = {}
    for f in (archive / "presentations").glob("*.json"):
        p = json.loads(f.read_text())
        pid = p["id"]
        if p.get("is_withdrawn") or (only_ids is not None and pid not in only_ids):
            continue
        s = sess_by_pid.get(pid, {})
        talks[pid] = Talk(
            id=pid,
            title=p.get("title") or "",
            abstract=p.get("abstract") or "",
            topics=tuple(p.get("topics") or []),
            units=tuple(s.get("sponsor_units") or []),
            session_title=s.get("title") or "",
            start=p.get("start"), end=p.get("end"),
        )
    return talks
```

- [ ] **Step 4: Verify PASS**, then run the whole suite: `uv run pytest -v`
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): corpus loading with session join"`

---

### Task 4: Method graph (`graph.py`)

**Files:** Create: `pipeline/src/gps_engine/graph.py`, `pipeline/tests/test_graph.py`

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/test_graph.py
from gps_engine.graph import MethodGraph

def test_identical_strings_share_a_node():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "DMRG")
    assert g.talks_using(g.node_id("DMRG")) == {1, 2}

def test_merge_unifies_nodes_and_links():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "density-matrix renormalization group")
    g.merge(g.node_id("DMRG"), g.node_id("density-matrix renormalization group"))
    nid = g.node_id("DMRG")
    assert nid == g.node_id("density-matrix renormalization group")
    assert g.talks_using(nid) == {1, 2}

def test_related_edge_is_symmetric():
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "transfer-matrix methods")
    g.add_related(g.node_id("DMRG"), g.node_id("transfer-matrix methods"))
    assert g.node_id("transfer-matrix methods") in g.related_to(g.node_id("DMRG"))
    assert g.node_id("DMRG") in g.related_to(g.node_id("transfer-matrix methods"))

def test_round_trips_through_json(tmp_path):
    g = MethodGraph()
    g.link_talk(1, "DMRG"); g.link_talk(2, "transfer-matrix methods")
    g.merge(g.node_id("DMRG"), g.node_id("transfer-matrix methods"))
    path = tmp_path / "g.json"
    g.save(path)
    g2 = MethodGraph.load(path)
    assert g2.talks_using(g2.node_id("DMRG")) == {1, 2}
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/graph.py
"""Bipartite talk→method graph with merge (same method, different name)
and RELATED_TO edges (kin methods). Method names are normalized only by
casefold/strip — every semantic judgment comes from LLM verdicts upstream."""
import json
from pathlib import Path


class MethodGraph:
    def __init__(self):
        self._canon: dict[str, int] = {}       # normalized name -> node id
        self._names: dict[int, set[str]] = {}  # node id -> all names merged into it
        self._talks: dict[int, set[int]] = {}  # node id -> talk ids
        self._related: dict[int, set[int]] = {}
        self._next = 0

    @staticmethod
    def _norm(name: str) -> str:
        return " ".join(name.casefold().split())

    def node_id(self, name: str) -> int:
        return self._canon[self._norm(name)]

    def link_talk(self, talk_id: int, method_name: str) -> int:
        key = self._norm(method_name)
        if key not in self._canon:
            nid = self._next; self._next += 1
            self._canon[key] = nid
            self._names[nid] = {key}
            self._talks[nid] = set()
            self._related[nid] = set()
        nid = self._canon[key]
        self._talks[nid].add(talk_id)
        return nid

    def merge(self, keep: int, absorb: int) -> None:
        if keep == absorb:
            return
        self._talks[keep] |= self._talks.pop(absorb)
        for name in self._names.pop(absorb):
            self._canon[name] = keep
        self._names[keep] |= {n for n, i in self._canon.items() if i == keep}
        for other in self._related.pop(absorb, set()):
            self._related[other].discard(absorb)
            if other != keep:
                self._related[other].add(keep)
                self._related[keep].add(other)

    def add_related(self, a: int, b: int) -> None:
        if a != b:
            self._related[a].add(b); self._related[b].add(a)

    def talks_using(self, node: int) -> set[int]:
        return set(self._talks[node])

    def related_to(self, node: int) -> set[int]:
        return set(self._related[node])

    def nodes(self) -> list[int]:
        return list(self._talks)

    def names_of(self, node: int) -> set[str]:
        return set(self._names[node])

    def save(self, path: Path) -> None:
        path.write_text(json.dumps({
            "canon": self._canon,
            "talks": {str(k): sorted(v) for k, v in self._talks.items()},
            "related": {str(k): sorted(v) for k, v in self._related.items()},
            "next": self._next,
        }))

    @classmethod
    def load(cls, path: Path) -> "MethodGraph":
        d = json.loads(path.read_text())
        g = cls()
        g._canon = {k: int(v) for k, v in d["canon"].items()}
        g._talks = {int(k): set(v) for k, v in d["talks"].items()}
        g._related = {int(k): set(v) for k, v in d["related"].items()}
        g._names = {}
        for name, nid in g._canon.items():
            g._names.setdefault(nid, set()).add(name)
        g._next = d["next"]
        return g
```

- [ ] **Step 4: Verify PASS** (whole suite)
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): method graph with merge and related edges"`

---

### Task 5: Method extraction (`extraction.py`)

**Files:** Create: `pipeline/src/gps_engine/extraction.py`, `pipeline/tests/test_extraction.py`

This is the production extraction path (Path B, Rupert-approved): our prompt + `LLMClient`, schema-constrained to methods only. The same function runs live in `run_stage0.py` with `AnthropicLLM` swapped in.

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/test_extraction.py
from gps_engine.corpus import Talk
from gps_engine.extraction import extract_methods
from gps_engine.llm import FakeLLM

TALK = Talk(id=1, title="Kondo physics probed by STM",
            abstract="We use scanning tunneling microscopy and DMRG simulations.",
            topics=(), units=("DCMP",), session_title="", start=None, end=None)

def test_extracts_method_list_from_llm():
    llm = FakeLLM(responses=[{"methods": ["scanning tunneling microscopy", "DMRG"]}])
    assert extract_methods(TALK, llm) == ["scanning tunneling microscopy", "DMRG"]

def test_prompt_contains_title_and_abstract():
    llm = FakeLLM(responses=[{"methods": []}])
    extract_methods(TALK, llm)
    assert "Kondo physics" in llm.prompts[0] and "DMRG simulations" in llm.prompts[0]

def test_dedupes_and_drops_blank():
    llm = FakeLLM(responses=[{"methods": ["DMRG", "dmrg ", ""]}])
    assert extract_methods(TALK, llm) == ["DMRG"]
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/extraction.py
from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

PROMPT = """Extract the research METHODS used in this conference abstract.
A method is a technique, algorithm, measurement, fabrication, or theoretical
framework the authors USE (not the system they study, not the phenomenon).
Use the authors' own terminology. Return every distinct method.

Title: {title}
Abstract: {abstract}"""


def extract_methods(talk: Talk, llm: LLMClient) -> list[str]:
    out = llm.complete_json(
        PROMPT.format(title=talk.title, abstract=talk.abstract),
        schema_hint='{"methods": ["string", ...]}',
    )
    seen, result = set(), []
    for m in out.get("methods", []):
        key = " ".join(str(m).casefold().split())
        if key and key not in seen:
            seen.add(key)
            result.append(str(m).strip())
    return result
```

- [ ] **Step 4: Verify PASS**
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): schema-constrained method extraction"`

---

### Task 6: Similarity pair proposal (`similarity.py`, part 1)

**Files:** Create: `pipeline/src/gps_engine/similarity.py`, `pipeline/tests/test_similarity.py`; Modify: `pipeline/pyproject.toml` (add `sentence-transformers>=3` to dependencies)

Never all-pairs: propose only embedding-near name pairs for LLM judgment.

- [ ] **Step 1: Write the failing tests** (embedder injected so tests stay offline)

```python
# pipeline/tests/test_similarity.py
from gps_engine.similarity import propose_pairs

def fake_embed(names):  # 1-D embeddings: distance = alphabetical-ish toy metric
    table = {"dmrg": [1.0, 0.0], "density-matrix renormalization group": [0.98, 0.05],
             "neutron scattering": [0.0, 1.0]}
    return [table[n] for n in names]

def test_proposes_only_near_pairs():
    names = ["dmrg", "density-matrix renormalization group", "neutron scattering"]
    pairs = propose_pairs(names, embed=fake_embed, threshold=0.9)
    assert pairs == [("density-matrix renormalization group", "dmrg")]

def test_no_pairs_when_all_far():
    pairs = propose_pairs(["dmrg", "neutron scattering"], embed=fake_embed, threshold=0.9)
    assert pairs == []
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/similarity.py
import math
from typing import Callable

Embedder = Callable[[list[str]], list[list[float]]]


def _cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def propose_pairs(names: list[str], embed: Embedder, threshold: float = 0.75
                  ) -> list[tuple[str, str]]:
    vecs = embed(names)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if _cos(vecs[i], vecs[j]) >= threshold:
                pairs.append(tuple(sorted((names[i], names[j]))))
    return sorted(set(pairs))


def sbert_embedder() -> Embedder:
    """Live embedder (not unit-tested; used by scripts)."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return lambda names: model.encode(names).tolist()
```

(Name-pair proposal is O(n²) over *distinct method names* — a few hundred to low thousands, trivially cheap locally; the invariant bans all-pairs **LLM** judgments, not local arithmetic.)

- [ ] **Step 4: Verify PASS**
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): embedding-based method pair proposal"`

---

### Task 7: Similarity verdicts (`similarity.py`, part 2)

**Files:** Modify: `pipeline/src/gps_engine/similarity.py`, `pipeline/tests/test_similarity.py`

- [ ] **Step 1: Add failing tests**

```python
# append to pipeline/tests/test_similarity.py
from gps_engine.graph import MethodGraph
from gps_engine.llm import FakeLLM
from gps_engine.similarity import apply_verdicts, judge_pair

def test_judge_pair_parses_verdict():
    llm = FakeLLM(responses=[{"verdict": "same", "why": "acronym"}])
    assert judge_pair("dmrg", "density-matrix renormalization group", llm)["verdict"] == "same"

def test_apply_verdicts_merges_and_relates():
    g = MethodGraph()
    g.link_talk(1, "dmrg"); g.link_talk(2, "density-matrix renormalization group")
    g.link_talk(3, "transfer-matrix methods")
    verdicts = [
        ("dmrg", "density-matrix renormalization group", {"verdict": "same", "why": ""}),
        ("dmrg", "transfer-matrix methods", {"verdict": "related", "why": ""}),
    ]
    apply_verdicts(g, verdicts)
    assert g.talks_using(g.node_id("dmrg")) == {1, 2}
    assert g.node_id("transfer-matrix methods") in g.related_to(g.node_id("dmrg"))

def test_apply_verdicts_ignores_unrelated():
    g = MethodGraph()
    g.link_talk(1, "dmrg"); g.link_talk(2, "neutron scattering")
    apply_verdicts(g, [("dmrg", "neutron scattering", {"verdict": "unrelated", "why": ""})])
    assert g.related_to(g.node_id("dmrg")) == set()
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement (append to `similarity.py`)**

```python
from gps_engine.graph import MethodGraph
from gps_engine.llm import LLMClient

JUDGE_PROMPT = """Two research-method names from physics conference abstracts:
A: {a}
B: {b}
Verdict:
- "same": the same method under different names/spellings/acronyms
- "related": distinct methods that are mathematically or operationally kin
  (one derives from the other, shares core formalism, or routinely substitutes)
- "unrelated": otherwise
Be strict: "related" requires genuine methodological kinship, not co-occurrence."""


def judge_pair(a: str, b: str, llm: LLMClient) -> dict:
    return llm.complete_json(
        JUDGE_PROMPT.format(a=a, b=b),
        schema_hint='{"verdict": "same|related|unrelated", "why": "string"}',
    )


def apply_verdicts(g: MethodGraph, verdicts: list[tuple[str, str, dict]]) -> None:
    for a, b, v in verdicts:
        if v["verdict"] == "same":
            g.merge(g.node_id(a), g.node_id(b))
        elif v["verdict"] == "related":
            g.add_related(g.node_id(a), g.node_id(b))
```

- [ ] **Step 4: Verify PASS**
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): LLM method-similarity verdicts"`

---

### Task 8: Candidate funnel (`funnel.py`)

**Files:** Create: `pipeline/src/gps_engine/funnel.py`, `pipeline/tests/test_funnel.py`

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/test_funnel.py
from gps_engine.funnel import candidates
from gps_engine.graph import MethodGraph

def build():
    g = MethodGraph()
    g.link_talk(1, "self-assembly"); g.link_talk(2, "self-assembly")   # shared node
    g.link_talk(3, "supramolecular assembly")                          # related node
    g.add_related(g.node_id("self-assembly"), g.node_id("supramolecular assembly"))
    g.link_talk(4, "neutron scattering")                               # unconnected
    return g

def test_direct_and_related_hops_found():
    assert candidates(build(), talk_id=1) == {2, 3}

def test_self_excluded():
    assert 1 not in candidates(build(), talk_id=1)

def test_isolated_talk_yields_empty():
    assert candidates(build(), talk_id=4) == set()
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/funnel.py
from gps_engine.graph import MethodGraph


def candidates(g: MethodGraph, talk_id: int) -> set[int]:
    my_nodes = [n for n in g.nodes() if talk_id in g.talks_using(n)]
    out: set[int] = set()
    for n in my_nodes:
        out |= g.talks_using(n)
        for r in g.related_to(n):
            out |= g.talks_using(r)
    out.discard(talk_id)
    return out
```

- [ ] **Step 4: Verify PASS**
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): graph-traversal candidate funnel"`

---

### Task 9: Interrogation rubric (`rubric.py`)

**Files:** Create: `pipeline/src/gps_engine/rubric.py`, `pipeline/tests/test_rubric.py`

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/test_rubric.py
from gps_engine.corpus import Talk
from gps_engine.llm import FakeLLM
from gps_engine.rubric import Judgment, judge_candidate

ME = Talk(id=1, title="Porphyrin nanorod photoconductivity",
          abstract="Self-assembled nanorods; trainable photocurrent.",
          topics=(), units=("DPOLY",), session_title="", start=None, end=None)
OTHER = Talk(id=2, title="Optoelectronic synapses",
             abstract="Photoinduced charge transfer; synaptic memory.",
             topics=(), units=("DMP",), session_title="", start=None, end=None)

def make_llm(match=True):
    return FakeLLM(responses=[{
        "shared_methods": 4, "transferability": 3, "analogous_phenomena": 4,
        "match": match, "why": "both exhibit optically trained conductance memory",
    }])

def test_judgment_fields_populated():
    j = judge_candidate(ME, OTHER, make_llm())
    assert isinstance(j, Judgment) and j.match and j.candidate_id == 2
    assert j.why.startswith("both exhibit")

def test_cross_domain_computed_from_units_not_llm():
    j = judge_candidate(ME, OTHER, make_llm())
    assert j.cross_domain is True          # DPOLY vs DMP: disjoint
    same_unit = Talk(**{**OTHER.__dict__, "units": ("DPOLY",)})
    j2 = judge_candidate(ME, same_unit, make_llm())
    assert j2.cross_domain is False

def test_prompt_contains_both_abstracts():
    llm = make_llm()
    judge_candidate(ME, OTHER, llm)
    assert "trainable photocurrent" in llm.prompts[0]
    assert "synaptic memory" in llm.prompts[0]
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/rubric.py
from dataclasses import dataclass

from gps_engine.corpus import Talk
from gps_engine.llm import LLMClient

RUBRIC_PROMPT = """You judge whether a conference talk is method-relevant to a
researcher, via these lines of inquiry (score each 0-5):
1. shared_methods: do they USE the same or equivalent methods, even under
   different names? (Judge the mathematics/apparatus, not the vocabulary.)
2. transferability: could the candidate's techniques plausibly transfer to the
   researcher's problem?
3. analogous_phenomena: do they study analogous phenomena in different systems?
Then decide match: true only if a physicist would thank you for the pointer.
Be strict; most candidates are not matches.

RESEARCHER'S ABSTRACT:
{mine}

CANDIDATE TALK:
Title: {title}
Abstract: {abstract}"""


@dataclass(frozen=True)
class Judgment:
    candidate_id: int
    shared_methods: int
    transferability: int
    analogous_phenomena: int
    match: bool
    cross_domain: bool
    why: str

    @property
    def score(self) -> int:
        return self.shared_methods + self.transferability + self.analogous_phenomena


def judge_candidate(mine: Talk, cand: Talk, llm: LLMClient) -> Judgment:
    out = llm.complete_json(
        RUBRIC_PROMPT.format(
            mine=f"{mine.title}\n{mine.abstract}",
            title=cand.title, abstract=cand.abstract),
        schema_hint='{"shared_methods": 0, "transferability": 0, '
                    '"analogous_phenomena": 0, "match": true, "why": "string"}',
    )
    return Judgment(
        candidate_id=cand.id,
        shared_methods=int(out["shared_methods"]),
        transferability=int(out["transferability"]),
        analogous_phenomena=int(out["analogous_phenomena"]),
        match=bool(out["match"]),
        cross_domain=not (set(mine.units) & set(cand.units)),
        why=str(out["why"]),
    )
```

- [ ] **Step 4: Verify PASS**
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): interrogation rubric judgment"`

---

### Task 10: Pick assembly (`recommend.py`)

**Files:** Create: `pipeline/src/gps_engine/recommend.py`, `pipeline/tests/test_recommend.py`

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/test_recommend.py
from gps_engine.recommend import assemble
from gps_engine.rubric import Judgment

def J(cid, score, match=True, cross=False):
    s = score // 3
    return Judgment(candidate_id=cid, shared_methods=s, transferability=s,
                    analogous_phenomena=score - 2 * s, match=match,
                    cross_domain=cross, why="w")

def test_caps_1_2_core_and_2_3_unexpected():
    js = [J(1, 12), J(2, 11), J(3, 10),                     # core
          J(4, 12, cross=True), J(5, 11, cross=True),
          J(6, 10, cross=True), J(7, 9, cross=True)]        # unexpected
    picks = assemble(js)
    assert [j.candidate_id for j in picks.core] == [1, 2]
    assert [j.candidate_id for j in picks.unexpected] == [4, 5, 6]

def test_non_matches_never_picked():
    picks = assemble([J(1, 15, match=False), J(2, 15, match=False, cross=True)])
    assert picks.core == [] and picks.unexpected == []

def test_empty_input_is_valid():
    picks = assemble([])
    assert picks.core == [] and picks.unexpected == []

def test_min_score_threshold_applies():
    picks = assemble([J(1, 5), J(2, 5, cross=True)], min_score=8)
    assert picks.core == [] and picks.unexpected == []
```

- [ ] **Step 2: Run to verify FAIL**
- [ ] **Step 3: Implement**

```python
# pipeline/src/gps_engine/recommend.py
from dataclasses import dataclass

from gps_engine.rubric import Judgment


@dataclass(frozen=True)
class Picks:
    core: list[Judgment]
    unexpected: list[Judgment]


def assemble(judgments: list[Judgment], min_score: int = 8,
             max_core: int = 2, max_unexpected: int = 3) -> Picks:
    ok = sorted((j for j in judgments if j.match and j.score >= min_score),
                key=lambda j: -j.score)
    return Picks(
        core=[j for j in ok if not j.cross_domain][:max_core],
        unexpected=[j for j in ok if j.cross_domain][:max_unexpected],
    )
```

- [ ] **Step 4: Verify PASS** (whole suite: `uv run pytest -v`)
- [ ] **Step 5: Commit** — `git commit -am "feat(pipeline): threshold-gated pick assembly"`

---

### Task 11: Negative-set proposal script

**Files:** Create: `pipeline/scripts/select_negatives.py`

No LLM, no network — reads the local archive, so runnable without a go. Output is a *proposal* for Rupert's review; `datasets/micro-corpus.json` is updated only after approval.

- [ ] **Step 1: Write the script**

```python
# pipeline/scripts/select_negatives.py
"""Propose ~50 negatives for the micro-corpus: 40 seeded-random unrelated talks
+ a shortlist of same-domain (organic-electronics-adjacent) talks from which
~10 different-method negatives will be hand-picked. Prints for review."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engine.corpus import load_talks  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
POSITIVES = {p["id"] for p in json.loads(
    (ROOT / "datasets" / "micro-corpus.json").read_text())["positives"]}
ANCHOR_METHOD_WORDS = ("self-assembl", "photoconduct", "photocurrent", "memrist",
                       "neuromorphic", "synaptic", "resistive switching",
                       "nanowire", "nanorod", "charge transport")

talks = load_talks(ROOT / "data" / "gps2026")
eligible = [t for t in talks.values()
            if t.id not in POSITIVES
            and not any(w in (t.title + " " + t.abstract).lower()
                        for w in ANCHOR_METHOD_WORDS)]

rng = random.Random(2026)
print("== 40 random unrelated (auto-approved unless struck) ==")
for t in rng.sample(eligible, 40):
    print(f"{t.id}\t[{','.join(t.units)}]\t{t.title[:100]}")

print("\n== same-domain shortlist (pick ~10 with NONE of the anchor's methods) ==")
same_domain = [t for t in eligible
               if "organic electronic" in t.session_title.lower()
               or "molecular electronic" in t.session_title.lower()
               or ("DPOLY" in t.units and "electro" in t.session_title.lower())]
for t in same_domain[:25]:
    print(f"{t.id}\t[{','.join(t.units)}]\t{t.title[:80]}  <<{t.session_title[:50]}>>")
```

- [ ] **Step 2: Run it** — `cd pipeline && uv run python scripts/select_negatives.py` — verify it prints 40 + a shortlist (sanity: no positive IDs appear).
- [ ] **Step 3: STOP — present output to Rupert for approval.** After approval, add a `"negatives": {"ids": [...]}` entry (chosen IDs) to `datasets/micro-corpus.json` alongside the existing plan text.
- [ ] **Step 4: Commit** — `git add pipeline/scripts/select_negatives.py datasets/micro-corpus.json && git commit -m "feat(pipeline): negative-set selection for micro-corpus"`

---

### Task 12: Stage-0 end-to-end runner (gated)

**Files:** Create: `pipeline/scripts/run_stage0.py`

**GATE: this script spends live LLM tokens. Do not run without Rupert's explicit go.** It must checkpoint per talk/pair (JSON files in `pipeline/out/stage0/`, skip-if-exists) and write probeable `pipeline/out/stage0/status.json` progress, per CLAUDE.md.

- [ ] **Step 1: Write the runner** (structure below; checkpoint helpers mirror `data/crawl_gps2026.py`; extraction is Task 5's `extract_methods` with the live `AnthropicLLM`)

```python
# pipeline/scripts/run_stage0.py
"""End-to-end Stage-0 eval on the micro-corpus. GATED: live LLM spend.
Checkpoints every artifact; rerun resumes. Progress: out/stage0/status.json."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_engine.corpus import load_talks
from gps_engine.extraction import extract_methods
from gps_engine.funnel import candidates
from gps_engine.graph import MethodGraph
from gps_engine.llm import AnthropicLLM
from gps_engine.recommend import assemble
from gps_engine.rubric import judge_candidate
from gps_engine.similarity import apply_verdicts, judge_pair, propose_pairs, sbert_embedder

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out" / "stage0"
OUT.mkdir(parents=True, exist_ok=True)
t0 = time.time()


def status(msg):
    (OUT / "status.json").write_text(json.dumps(
        {"phase": msg, "elapsed_s": round(time.time() - t0)}))
    print(f"[{round(time.time()-t0)}s] {msg}", flush=True)


def checkpointed(path: Path, fn):
    if path.exists():
        return json.loads(path.read_text())
    result = fn()
    path.write_text(json.dumps(result))
    return result


mc = json.loads((ROOT / "datasets" / "micro-corpus.json").read_text())
ids = ({p["id"] for p in mc["positives"]}
       | set(mc.get("negatives", {}).get("ids", [])))
talks = load_talks(ROOT / "data" / "gps2026", only_ids=ids)

# The anchor is an external paper: represent it as a pseudo-talk.
from gps_engine.corpus import Talk
anchor = Talk(id=0, title=mc["anchor"]["title"],
              abstract="Self-assembled porphyrin nanorods; photoconductivity with "
                       "fast on/off transients and slow growth/decay; bias-training "
                       "produces reversed short-circuit photocurrent (memory); "
                       "conduction through coupled LUMOs of stacked molecules.",
              topics=(), units=("DPOLY",), session_title="", start=None, end=None)
talks[0] = anchor

extract_llm = AnthropicLLM("claude-haiku-4-5-20251001")
judge_llm = AnthropicLLM("claude-sonnet-5")

status("extraction")
g = MethodGraph()
(OUT / "methods").mkdir(exist_ok=True)
for i, t in enumerate(talks.values()):
    ms = checkpointed(OUT / "methods" / f"{t.id}.json",
                      lambda t=t: extract_methods(t, extract_llm))
    for m in ms:
        g.link_talk(t.id, m)
    if i % 5 == 0:
        status(f"extraction {i+1}/{len(talks)}")

status("similarity")
names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
pairs = propose_pairs(names, embed=sbert_embedder())
(OUT / "verdicts").mkdir(exist_ok=True)
verdicts = []
for i, (a, b) in enumerate(pairs):
    v = checkpointed(OUT / "verdicts" / f"{i}.json",
                     lambda a=a, b=b: judge_pair(a, b, judge_llm))
    verdicts.append((a, b, v))
apply_verdicts(g, verdicts)
g.save(OUT / "graph.json")

status("funnel+rubric")
cands = candidates(g, talk_id=0)
(OUT / "judgments").mkdir(exist_ok=True)
judgments = []
for cid in sorted(cands):
    j = checkpointed(OUT / "judgments" / f"{cid}.json",
                     lambda cid=cid: judge_candidate(anchor, talks[cid], judge_llm).__dict__)
    from gps_engine.rubric import Judgment
    judgments.append(Judgment(**j))

picks = assemble(judgments)
report = {
    "funnel_candidates": sorted(cands),
    "matches": [j.__dict__ for j in judgments if j.match],
    "picks": {"core": [j.__dict__ for j in picks.core],
              "unexpected": [j.__dict__ for j in picks.unexpected]},
    "expected_positives": sorted({p["id"] for p in mc["positives"]}),
    "hit_positives": sorted({j.candidate_id for j in judgments if j.match}
                            & {p["id"] for p in mc["positives"]}),
    "false_positives": sorted({j.candidate_id for j in judgments if j.match}
                              - {p["id"] for p in mc["positives"]}),
}
(OUT / "report.json").write_text(json.dumps(report, indent=1))
status("done — see out/stage0/report.json")
```

- [ ] **Step 2: STOP — get Rupert's go, then run:** `cd pipeline && ANTHROPIC_API_KEY=... uv run python scripts/run_stage0.py` (progress: `cat pipeline/out/stage0/status.json`)
- [ ] **Step 3: Review `report.json` with Rupert** — success = most positives in `hit_positives` with sensible `why` texts, near-empty `false_positives`. Iterate prompts (extraction/rubric strictness) as needed; checkpoints make reruns cheap — delete only the affected checkpoint dirs (`judgments/` after a rubric change).
- [ ] **Step 4: Commit** — `git add pipeline datasets && git commit -m "feat(pipeline): stage-0 end-to-end eval runner"`

---

## Deferred to Plan 2/3 (not this plan)

- Supabase project creation (Rupert), Drizzle schema, Postgres loader for graph artifacts, tRPC procedures, claim-your-talk search.
- UI pages (cards, calendar), scheduler + venue map, Vercel deploy.
- Stage-1 corpus assembly (tag-set discovery) and embedding-baseline comparison.

## Self-review notes

- Spec coverage: engine §3 fully tasked (extraction T5, similarity T6–7, storage-as-artifacts T4/T12 with Postgres explicitly deferred to Plan 2, funnel T8, rubric T9, thresholds T10); ground truth §2.1 tasked (T11–12). Product surface §4 and Postgres §5 are Plans 2–3 by design.
- Extraction path decided by Rupert 2026-08-26: our own schema-constrained prompt (Path B); LlamaIndex removed from the plan entirely.
- Type consistency: `Talk`, `LLMClient`, `MethodGraph`, `Judgment`, `Picks` signatures match across tasks.
