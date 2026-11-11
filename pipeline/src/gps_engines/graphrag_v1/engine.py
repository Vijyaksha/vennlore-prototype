"""graphrag_v1: Vennlore's GraphRAG as a pluggable engine.

index():     LLM method extraction per talk -> knowledge graph (talk, topic,
             method, unit) -> Louvain research themes -> LLM theme names
             -> index.json
recommend(): anchor methods -> local graph search (1 hop: shared concepts and
             wording; 3 hops: strong talk -> shared method -> other division)
             -> LLM explains ONLY the retrieved picks -> contract rows

Free by default (provider='local': LM Studio / Ollama), and still works with
provider='none' or when the LLM fails: template reasons, topic-only graph.
Reads only Talk.id/title/abstract/units/topics."""
import json
from dataclasses import replace
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from gps_core.checkpoint import content_key
from gps_core.filters import default_cross_domain
from gps_core.llm import AnthropicLLM, DeepSeekLLM, LLMClient, LocalLLM
from gps_core.progress import Status, parallel
from gps_core.protocol import IndexArtifact
from gps_core.records import Recommendation
from gps_data.talk import Talk, external_anchor
from gps_engines.graphrag_v1.graph import (
    build_graph,
    clean_methods,
    detect_themes,
    fallback_theme_text,
    merge_methods,
    theme_of,
)
from gps_engines.graphrag_v1.retrieve import (
    TextIndex,
    path,
    score_all,
    select,
    template_why,
    walk_deep,
    walk_three_hops,
)

ENGINE_ID = "graphrag_v1"

PROVIDERS = {
    "local": (LocalLLM, "local"),                         # free: LM Studio / Ollama
    "deepseek": (DeepSeekLLM, "deepseek-chat"),
    "anthropic": (AnthropicLLM, "claude-haiku-4-5-20251001"),
    "none": (None, None),                                 # no LLM: templates only
}

EXTRACT_PROMPT = """List the research methods and techniques this conference talk USES
(experimental techniques, instruments, simulations, algorithms, analysis methods).
Short names, 1-5 words each, at most 8. No topics, no findings.

Title: {title}
Abstract: {abstract}"""

THEME_PROMPT = """Name the research theme these conference talks share. They are linked
by the concepts: {concepts}.
Talks:
{talks}
Give a short title (at most 7 words) and a 2-sentence summary of what links them."""

ASK_PROMPT = """Answer the question using ONLY these research themes from the conference.
Name the themes and talks you rely on. 3 to 5 sentences. If the themes do not answer it, say so.

Themes:
{themes}

Question: {question}"""

EXPLAIN_PROMPT = """Explain each recommendation to the author of this talk.
Their talk: "{title}"

Talks our knowledge graph found for them (id | title | kind | graph link):
{lines}

For EACH id write ONE short sentence on why it is worth attending, based only on its
graph link. "unexpected" talks come from another research division."""


def _as_row(t: Talk) -> dict:
    """The only Talk fields an engine may read."""
    return {"id": t.id, "title": t.title, "abstract": t.abstract,
            "units": list(t.units), "topics": list(t.topics)}


class GraphRAGEngine:
    id = ENGINE_ID

    def __init__(self, llm: LLMClient | None, models: dict, workers: int = 4):
        self.llm, self.models, self.workers = llm, models, workers
        self._warned = False

    # ---- LLM boundary: every call may fail; failures fall back, loudly -----

    def _ask(self, prompt: str, hint: str) -> dict | None:
        if self.llm is None:
            return None
        try:
            out = self.llm.complete_json(prompt, schema_hint=hint)
            return out if isinstance(out, dict) else None
        except Exception as e:   # unreachable server, refusal, unusable JSON...
            if not self._warned:
                print(f"[{self.id}] LLM call failed ({type(e).__name__}: {str(e)[:120]}); "
                      "using graph-only fallbacks", flush=True)
                self._warned = True
            return None

    def _cached(self, path: Path, fn):
        """Checkpoint successes only, so a rerun retries what failed and resumes
        everything that did not."""
        if path.exists():
            return json.loads(path.read_text())
        result = fn()
        if result is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(path.name + ".tmp")
            tmp.write_text(json.dumps(result))
            tmp.replace(path)
        return result

    def _ck(self, root: Path, stage: str, *inputs) -> Path:
        model = self.models.get({"methods": "extract"}.get(stage, stage), "none")
        return root / stage / f"{content_key(self.id, stage, model, *inputs)}.json"

    def _methods(self, root: Path, t: dict) -> list[str]:
        if self.llm is None:
            return []
        out = self._cached(
            self._ck(root, "methods", t["title"], t["abstract"]),
            lambda: self._ask(EXTRACT_PROMPT.format(**t), '{"methods": ["method name", ...]}'))
        return clean_methods((out or {}).get("methods"))

    # ---- the contract ------------------------------------------------------

    def index(self, corpus: list[Talk], out: Path) -> IndexArtifact:
        ids = [t.id for t in corpus]
        assert len(ids) == len(set(ids)), "duplicate talk ids in corpus"
        status = Status(out)
        talks = [_as_row(t) for t in corpus]
        status.set(f"extracting methods from {len(talks)} talks")
        methods = parallel("methods", talks, lambda t: self._methods(out, t),
                           workers=self.workers, status=status)
        for t, ms in zip(talks, methods, strict=True):
            t["methods"] = ms
        merge_methods(talks)

        status.set("building knowledge graph and themes")
        g = build_graph(talks)
        themes = detect_themes(g)
        by_id = {t["id"]: t for t in talks}

        def name(theme: dict) -> dict:
            text = None
            if len(theme["talk_ids"]) >= 2:
                listing = "\n".join(f"- {by_id[i]['title']}" for i in theme["talk_ids"][:8])
                text = self._cached(
                    self._ck(out, "themes", theme["concepts"], theme["talk_ids"]),
                    lambda: self._ask(THEME_PROMPT.format(
                        concepts=", ".join(theme["concepts"][:6]), talks=listing),
                        '{"title": "short name", "summary": "two sentences"}'))
            ok = text and str(text.get("title", "")).strip() and str(text.get("summary", "")).strip()
            text = ({"title": " ".join(str(text["title"]).strip(" \"'.").split()[:7]),
                     "summary": str(text["summary"])[:600]} if ok else fallback_theme_text(theme))
            return {**theme, **text}

        themes = parallel("themes", themes, name, workers=self.workers, status=status)
        (out / "index.json").write_text(json.dumps(
            {"engine_id": self.id, "talks": talks, "themes": themes}, indent=1))
        status.set(f"indexed {len(talks)} talks, {len(themes)} themes")
        return IndexArtifact(path=out, engine_id=self.id)

    def _load(self, index: IndexArtifact):
        """index.json, its graph and its text index, built once and reused by every
        search until the index file changes."""
        f = index.path / "index.json"
        key = (str(f), f.stat().st_mtime_ns)
        if getattr(self, "_loaded", (None,))[0] != key:
            data = json.loads(f.read_text())
            self._loaded = (key, data, build_graph(data["talks"]), TextIndex(data["talks"]))
        return self._loaded[1:]

    def recommend(self, anchor: Talk, index: IndexArtifact) -> list[Recommendation]:
        data, g, text = self._load(index)
        talks, themes = data["talks"], data["themes"]
        a = _as_row(anchor)
        a["methods"] = self._methods(index.path / "anchors", a)
        text_sim = text.sims(a)
        units = {t["id"]: t["units"] for t in talks}

        home = anchor
        if not anchor.units:
            # A free-text query has no division: borrow the units of its closest
            # talks, so talks from other divisions can still be "unexpected".
            ranked = sorted(score_all(a, talks, g, lambda t: False, text_sim).values(),
                            key=lambda s: (-s.score, s.talk["id"]))
            votes: dict[str, float] = {}
            for s in [s for s in ranked if s.talk["units"]][:5]:   # score-weighted vote
                for u in s.talk["units"]:
                    votes[u] = votes.get(u, 0.0) + s.score
            borrowed = sorted(votes, key=lambda u: -votes[u])[:1]
            home = replace(anchor, units=tuple(borrowed))

        def cross(t: dict) -> bool:
            return default_cross_domain(home, _unit_only(t["id"], units[t["id"]]))

        scored = score_all(a, talks, g, cross, text_sim)
        walk_three_hops(scored, g, len(talks))
        walk_deep(a, scored, g, len(talks))
        chosen = select(scored)
        reasons = self._explain(index.path, a, [s for s in chosen if s.match])

        rows = []
        for s in chosen:
            why = reasons.get(str(s.talk["id"]))
            rows.append(Recommendation(
                for_talk_id=anchor.id, candidate_id=s.talk["id"], score=round(s.score, 4),
                rank=0, match=s.match, cross_domain=s.cross_domain,
                why=why or template_why(s),
                strongest_parallel=" → ".join(path(s)),
                shared_methods=tuple(dict.fromkeys(([s.bridge] if s.bridge else []) + s.shared))[:5],
                evidence={"hops": s.hops, "path": path(s), "bridge": s.bridge,
                          "via_talk_id": s.via["id"] if s.via else None,
                          "theme": theme_of(s.talk, themes),
                          "text_similarity": round(s.text, 4),
                          "concept_similarity": round(s.concept, 4),
                          "explained_by": "llm" if why else "template"},
                engine_id=self.id, run_id=""))
        return rows

    # ---- extras beyond the Engine protocol: themes and global questions ------

    def themes(self, index: IndexArtifact) -> list[dict]:
        """Every research theme: id, title, summary, concepts, talk_ids."""
        data = json.loads((index.path / "index.json").read_text())
        return [{**{k: t[k] for k in ("id", "title", "summary", "talk_ids")},
                 "concepts": list(dict.fromkeys(t["concepts"]))}   # older indexes may repeat labels
                for t in data["themes"]]

    def ask(self, index: IndexArtifact, question: str, top_k: int = 3) -> dict:
        """GraphRAG global search: rank themes against the question, then let the LLM
        answer from those theme summaries only. answer is None without an LLM."""
        data = json.loads((index.path / "index.json").read_text())
        themes = data["themes"]
        if not themes:
            return {"answer": None, "theme_ids": []}
        titles = {t["id"]: t["title"] for t in data["talks"]}
        docs = [f"{t['title']}. {t['summary']} " + " ".join(t["concepts"]) for t in themes]
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        mat = vec.fit_transform(docs + [question])
        sims = cosine_similarity(mat[-1], mat[:-1])[0]
        ranked = [themes[i] for i in sorted(range(len(themes)), key=lambda i: (-sims[i], i))][:top_k]
        listing = "\n".join(
            f"- {t['title']}: {t['summary'][:300]} Talks: "
            + "; ".join(titles[i] for i in t["talk_ids"][:5] if i in titles) for t in ranked)
        out = None
        if self.llm is not None:
            out = self._cached(self._ck(index.path / "asks", "ask", question, listing),
                               lambda: self._ask(ASK_PROMPT.format(themes=listing, question=question),
                                                 '{"answer": "3 to 5 sentences"}'))
        answer = str((out or {}).get("answer") or "").strip() or None
        return {"answer": answer, "theme_ids": [t["id"] for t in ranked]}

    def _explain(self, root: Path, a: dict, picks: list) -> dict[str, str]:
        """GraphRAG generation: the LLM sees only the retrieved picks and their
        graph paths, so its reasons stay grounded."""
        if self.llm is None or not picks:
            return {}
        lines = "\n".join(
            f"{s.talk['id']} | {s.talk['title']} | {'unexpected' if s.cross_domain else 'core'}"
            f" | {' -> '.join(path(s))}" for s in picks)
        out = self._cached(
            self._ck(root / "anchors", "explain", a["title"], a["abstract"], lines),
            lambda: self._ask(EXPLAIN_PROMPT.format(title=a["title"], lines=lines),
                              '{"reasons": {"<talk id>": "one sentence"}}'))
        reasons = (out or {}).get("reasons") or {}
        ids = {str(s.talk["id"]) for s in picks}
        return {str(k): str(v).strip() for k, v in reasons.items()
                if str(k) in ids and 10 <= len(str(v).strip()) <= 400}


def _unit_only(talk_id: int, units: list[str]) -> Talk:
    """A Talk carrying just id and units, for core's default_cross_domain."""
    return replace(external_anchor("", "", units), id=talk_id)


def build(provider: str = "local", model: str | None = None, workers: int = 4,
          llm_factory=None) -> GraphRAGEngine:
    """Registry factory. provider='local' (default) is free: whatever model LM
    Studio, or Ollama via LOCAL_LLM_URL, has loaded. Tests inject llm_factory."""
    if provider not in PROVIDERS:
        raise KeyError(f"unknown provider {provider!r}; known: {sorted(PROVIDERS)}")
    client, default_model = PROVIDERS[provider]
    if client is None:
        return GraphRAGEngine(llm=None, models={}, workers=workers)
    name = model or default_model
    llm = (llm_factory or client)(name)
    return GraphRAGEngine(llm=llm, workers=workers,
                          models={"extract": name, "themes": name, "explain": name})
