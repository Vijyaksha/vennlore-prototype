"""graph_v1 assembled once. index(): extraction → gleaning → claims → PhySH
filing → edge cascade → pair verdicts → graph.json. recommend(): anchor
extraction → filing → bipartite cascade → verdicts → funnel → rubric → rows.
Replaces run_stage0.py / run_stage1_index.py / run_query.py."""
import json
from dataclasses import replace
from pathlib import Path
from typing import Callable

from gps_core.checkpoint import checkpointed, content_key
from gps_core.filters import default_cross_domain
from gps_core.llm import AnthropicLLM, DeepSeekLLM, LLMClient, LLMRefusal, LLMUnusable
from gps_core.progress import Status, parallel
from gps_core.protocol import IndexArtifact
from gps_core.records import Recommendation
from gps_data.talk import Talk
from gps_engines.graph_v1.cascade import Decision, decide_pairs_bulk, decide_pairs_cross
from gps_engines.graph_v1.claims import claims_digest, extract_claims
from gps_engines.graph_v1.filing import candidate_shortlist, embed_targets, file_method
from gps_engines.graph_v1.funnel import candidates
from gps_engines.graph_v1.graph import MethodGraph
from gps_engines.graph_v1.li_extraction import extract_methods_json, glean_and_describe
from gps_engines.graph_v1.physh import PhySH, load_physh
from gps_engines.graph_v1.rubric import judge_candidate
from gps_engines.graph_v1.similarity import apply_verdicts, judge_pair, sbert_embedder

ENGINE_ID = "graph_v1"
MATCH_MIN_SCORE = 5       # calibrated on the 10+47 ground truth (2026-08-30)
RUBRIC_MAX = 15
# The anchor is linked into the graph under this talk id; for this task the
# anchor is ALWAYS external (Talk.id == 0), so it cannot collide with a
# corpus talk. An in-corpus anchor would; that is a later plan's problem.
ANCHOR_KEY = 0

PROVIDERS = {
    "deepseek": {"extract": "deepseek-chat", "pair_judge": "deepseek-chat",
                 "rubric": "deepseek-reasoner", "client": DeepSeekLLM},
    "anthropic": {"extract": "claude-haiku-4-5-20251001", "pair_judge": "claude-sonnet-5",
                  "rubric": "claude-sonnet-5", "client": AnthropicLLM},
}


def _norm(name: str) -> str:
    return " ".join(str(name).casefold().split())


class GraphV1Engine:
    id = ENGINE_ID

    def __init__(self, extract_llm: LLMClient, pair_llm: LLMClient, rubric_llm: LLMClient,
                 embed: Callable, physh: PhySH, models: dict, workers: int = 8):
        self.extract_llm, self.pair_llm, self.rubric_llm = extract_llm, pair_llm, rubric_llm
        self.embed, self.physh, self.models, self.workers = embed, physh, models, workers
        self._targets = None

    # ---- shared stages -------------------------------------------------

    def _targets_vecs(self):
        if self._targets is None:
            self._targets = embed_targets(self.physh, self.embed)
        return self._targets

    # Each stage's checkpoint is keyed by the model that PRODUCES it, so
    # changing the pair judge never invalidates extraction, and vice versa.
    _STAGE_MODEL = {"methods": "extract", "enrich": "extract", "claims": "extract",
                    "filings": "extract", "verdicts": "pair_judge", "judgments": "rubric"}

    def _ck(self, out: Path, stage: str, *inputs) -> Path:
        model = self.models[self._STAGE_MODEL[stage]]
        return out / stage / f"{content_key(self.id, stage, model, *inputs)}.json"

    def _extract(self, out: Path, t: Talk) -> tuple[list[str], dict, list]:
        key = (t.id, t.title, t.abstract)
        ms = checkpointed(self._ck(out, "methods", key),
                          lambda: extract_methods_json(t, self.extract_llm))
        enriched = checkpointed(self._ck(out, "enrich", key, ms),
                                lambda: list(glean_and_describe(t, ms, self.extract_llm)))
        claims = checkpointed(self._ck(out, "claims", key),
                              lambda: extract_claims(t, self.extract_llm))
        return enriched[0], enriched[1], claims

    def _file(self, out: Path, name: str, ctx: str) -> list[dict]:
        return checkpointed(
            self._ck(out, "filings", name, ctx),
            lambda: file_method(name, ctx, candidate_shortlist(
                name, ctx, self.physh, self.embed, self._targets_vecs()), self.physh, self.extract_llm))

    def _judge_pair(self, out: Path, d: Decision, name_context: dict,
                    status: Status) -> dict:
        def judge():
            try:
                return judge_pair(d.a, d.b, self.pair_llm,
                                  context_a=name_context.get(_norm(d.a), ""),
                                  context_b=name_context.get(_norm(d.b), ""),
                                  evidence=d.evidence)
            except (LLMRefusal, LLMUnusable) as err:
                kind = "REFUSAL" if isinstance(err, LLMRefusal) else "UNUSABLE RESPONSE"
                status.set(f"{kind} (pair, defaulting to no-edge): {d.a!r} vs {d.b!r}")
                return {"verdict": "unrelated",
                        "why": f"API {kind}; defaulted to no-edge, not a real judgment"}
        return checkpointed(self._ck(out, "verdicts", d.a, d.b, d.evidence), judge)

    @staticmethod
    def _n_refused(results) -> int:
        """Refusals counted from the results themselves, so a resumed run
        reports the same number as the run that first hit them."""
        return sum(1 for r in results
                   if any(m in (r.get("why") or "") for m in ("API REFUSAL", "API UNUSABLE")))

    @staticmethod
    def _verdicts(decisions: list[Decision], judged: dict) -> list[tuple[str, str, dict]]:
        vs = []
        for d in decisions:
            if d.action == "judge":
                vs.append((d.a, d.b, judged[(d.a, d.b)]))
            elif d.action in ("auto-same", "auto-related"):
                vs.append((d.a, d.b, {"verdict": "same" if d.action == "auto-same" else "related",
                                      "strength": d.strength, "why": d.why,
                                      "provenance": d.provenance}))
        return vs

    # ---- contract operations -------------------------------------------

    def index(self, corpus: list[Talk], out: Path) -> IndexArtifact:
        assert len({t.id for t in corpus}) == len(corpus), "duplicate talk ids in corpus"
        status = Status(out)
        status.set("extraction")
        ordered = sorted(corpus, key=lambda t: t.id)
        extracted = parallel("extraction", ordered, lambda t: (t, *self._extract(out, t)),
                             workers=self.workers, status=status)
        g = MethodGraph()
        name_context: dict[str, str] = {}
        for t, ms, descs, _claims in extracted:
            for m in ms:
                g.link_talk(t.id, m)
                key = _norm(m)
                if key not in name_context:
                    d = descs.get(m) or descs.get(key) or ""
                    name_context[key] = (f'in "{t.title[:70]}": {d}' if d
                                         else f'used in "{t.title[:70]}"')
        status.set("filing")
        names = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
        self._targets_vecs()          # embed PhySH once, on this thread
        filed = parallel("filing", names,
                         lambda n: self._file(out, n, name_context.get(_norm(n), "")),
                         workers=self.workers, status=status)
        filings = dict(zip(names, filed))
        status.set("cascade")
        texts = {n: f"{n}: {name_context.get(_norm(n), '')}" for n in names}
        kept, n_dropped = decide_pairs_bulk(names, filings, self.physh, self.embed, texts)
        to_judge = [d for d in kept if d.action == "judge"]
        status.set(f"cascade: {len(kept) - len(to_judge)} auto, {len(to_judge)} to judge, {n_dropped} dropped")
        judged = dict(zip([(d.a, d.b) for d in to_judge],
                          parallel("verdicts", to_judge,
                                   lambda d: self._judge_pair(out, d, name_context, status),
                                   workers=self.workers, status=status)))
        apply_verdicts(g, self._verdicts(kept, judged))
        g.save(out / "graph.json")
        (out / "name_context.json").write_text(json.dumps(name_context))
        (out / "filings.json").write_text(json.dumps(filings))
        (out / "talks.json").write_text(json.dumps({t.id: {"title": t.title, "abstract": t.abstract,
                                                           "units": list(t.units)} for t in ordered}))
        status.set(f"done — {len(names)} methods, {len(ordered)} talks, "
                   f"{self._n_refused(judged.values())} pair refusals")
        return IndexArtifact(path=out, engine_id=self.id)

    def recommend(self, anchor: Talk, index: IndexArtifact) -> list[Recommendation]:
        idx = index.path
        # keyed by content, not by id: every external anchor is id 0, so an
        # id-keyed dir would let two queries overwrite each other's status
        out = idx / "queries" / content_key(anchor.id, anchor.title, anchor.abstract)
        status = Status(out)
        g = MethodGraph.load(idx / "graph.json")
        name_context = json.loads((idx / "name_context.json").read_text())
        filings = json.loads((idx / "filings.json").read_text())
        talks = {int(k): v for k, v in json.loads((idx / "talks.json").read_text()).items()}

        status.set("anchor extraction")
        ms, descs, anchor_claims = self._extract(idx, anchor)
        existing = sorted({n for nid in g.nodes() for n in g.names_of(nid)})
        for m in ms:
            g.link_talk(ANCHOR_KEY, m)
            key = _norm(m)
            if key not in name_context:
                d = descs.get(m) or descs.get(key) or ""
                name_context[key] = (f'in "{anchor.title[:70]}": {d}' if d
                                     else f'used in "{anchor.title[:70]}"')
        # Normalised throughout: filings, name_context and `existing` are all
        # keyed on normalised names, and the cascade compares raw strings — so
        # an anchor method already in the index must not be re-filed, nor
        # cross-judged against its own twin.
        new_names = sorted({_norm(m) for m in ms})
        self._targets_vecs()          # embed PhySH once, on this thread
        for n in new_names:
            if n not in filings:
                filings[n] = self._file(idx, n, name_context.get(n, ""))

        status.set("bipartite cascade")
        texts = {n: f"{n}: {name_context.get(n, '')}" for n in set(existing) | set(new_names)}
        ds = decide_pairs_cross(new_names, existing, filings, self.physh, self.embed, texts)
        to_judge = [d for d in ds if d.action == "judge"]
        judged = dict(zip([(d.a, d.b) for d in to_judge],
                          parallel("verdicts", to_judge,
                                   lambda d: self._judge_pair(idx, d, name_context, status),
                                   workers=self.workers, status=status)))
        apply_verdicts(g, self._verdicts(ds, judged))

        cands = sorted(candidates(g, talk_id=ANCHOR_KEY, min_strength=0))
        status.set(f"rubric: {len(cands)} candidates")
        anchor_digest = claims_digest(anchor_claims)

        def rubric_one(cid: int) -> dict:
            # only id/title/abstract/units are load-bearing here: the rubric
            # and the extraction checkpoint key read nothing else off a Talk
            cand = replace(anchor, id=cid, title=talks[cid]["title"],
                           abstract=talks[cid]["abstract"], units=tuple(talks[cid]["units"]))
            _ms, _d, cand_claims = self._extract(idx, cand)

            def judge():
                try:
                    j = judge_candidate(anchor, cand, self.rubric_llm,
                                        mine_claims=anchor_digest,
                                        cand_claims=claims_digest(cand_claims))
                    return {"same_method": j.same_method, "specificity": j.specificity,
                            "usage_parallel": j.usage_parallel, "why": j.why,
                            "strongest_parallel": j.strongest_parallel}
                except (LLMRefusal, LLMUnusable) as err:
                    kind = "REFUSAL" if isinstance(err, LLMRefusal) else "UNUSABLE RESPONSE"
                    status.set(f"{kind} (rubric, defaulting to no-match): talk {cid}")
                    return {"same_method": 0, "specificity": 0, "usage_parallel": 0,
                            "strongest_parallel": "",
                            "why": f"API {kind}; defaulted to no-match, not a real judgment"}
            return checkpointed(self._ck(idx, "judgments", anchor.id, anchor.abstract, cid,
                                         cand.abstract), judge)

        judgments = parallel("rubric", cands, rubric_one, workers=self.workers, status=status)
        rows = []
        for cid, j in zip(cands, judgments):
            total = j["same_method"] + j["specificity"] + j["usage_parallel"]
            cand_units = tuple(talks[cid]["units"])
            rows.append(Recommendation(
                for_talk_id=anchor.id, candidate_id=cid, score=total / RUBRIC_MAX, rank=0,
                match=total >= MATCH_MIN_SCORE,
                # default_cross_domain compares units only; the stand-in Talk
                # carries the candidate's units and nothing else of its own
                cross_domain=default_cross_domain(anchor, replace(anchor, units=cand_units)),
                why=j["why"], strongest_parallel=j["strongest_parallel"],
                shared_methods=tuple(self._shared_methods(g, cid)),
                evidence={"same_method": j["same_method"], "specificity": j["specificity"],
                          "usage_parallel": j["usage_parallel"], "rubric_sum": total,
                          "match_min_score": MATCH_MIN_SCORE},
                engine_id=self.id, run_id=""))
        status.set(f"done — {sum(r.match for r in rows)} matches of {len(rows)} candidates, "
                   f"{self._n_refused(judgments)} rubric refusals")
        return rows

    @staticmethod
    def _shared_methods(g: MethodGraph, cid: int) -> list[str]:
        """Node names that connect the anchor to the candidate: a shared node
        gives one name; a RELATED_TO hop gives 'anchor-name ~ candidate-name'."""
        out: set[str] = set()
        for n in g.nodes():
            if ANCHOR_KEY not in g.talks_using(n):
                continue
            n_name = sorted(g.names_of(n))[0]
            if cid in g.talks_using(n):
                out.add(n_name)
            for r in g.related_to(n):
                if cid in g.talks_using(r):
                    out.add(f"{n_name} ~ {sorted(g.names_of(r))[0]}")
        return sorted(out)


def build(provider: str = "deepseek", workers: int = 8, embed=None, physh=None,
          llm_factory=None, extract_model=None, pair_judge_model=None,
          rubric_model=None) -> GraphV1Engine:
    """Registry factory. Live clients by default; tests inject fakes.
    Per-stage model overrides exist because the stage-0 reference run judged
    PAIRS with deepseek-reasoner while PROVIDERS carries the stage-1 choice
    (deepseek-chat); models always records the EFFECTIVE choice."""
    cfg = PROVIDERS[provider]
    make = llm_factory or cfg["client"]
    models = {"extract": extract_model or cfg["extract"],
              "pair_judge": pair_judge_model or cfg["pair_judge"],
              "rubric": rubric_model or cfg["rubric"]}
    return GraphV1Engine(
        extract_llm=make(models["extract"]), pair_llm=make(models["pair_judge"]),
        rubric_llm=make(models["rubric"]), embed=embed or sbert_embedder(),
        physh=physh or load_physh(), workers=workers, models=models)
