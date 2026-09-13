"""The engine's output records. Shapes are fixed by packages/contracts."""
from dataclasses import asdict, dataclass, field

CONTRACT_VERSION = 1


@dataclass(frozen=True)
class Recommendation:
    for_talk_id: int
    candidate_id: int
    score: float                 # 0..1, higher is better
    rank: int                    # 1 is best within for_talk_id
    match: bool
    cross_domain: bool
    why: str
    strongest_parallel: str
    shared_methods: tuple[str, ...]
    evidence: dict
    engine_id: str
    run_id: str

    def to_row(self) -> dict:
        row = asdict(self)
        row["shared_methods"] = list(self.shared_methods)
        row["contract_version"] = CONTRACT_VERSION
        return row


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    engine_id: str
    kind: str                    # "index" | "recommend"
    engine_version: str
    models: dict
    corpus_hash: str
    anchor_ids: tuple[int, ...]
    started_at: str
    finished_at: str
    index_path: str | None = None
    extra: dict = field(default_factory=dict)   # not in the contract; kept out of to_row

    def to_row(self) -> dict:
        row = asdict(self)
        row.pop("extra")
        row["anchor_ids"] = list(self.anchor_ids)
        row["contract_version"] = CONTRACT_VERSION
        return row
