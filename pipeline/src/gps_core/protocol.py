"""The engine contract: two functions. Everything else is the engine's own."""
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from gps_core.records import Recommendation
from gps_data.talk import Talk


@dataclass(frozen=True)
class IndexArtifact:
    """Opaque, engine-owned. Core only records its path in the manifest."""
    path: Path
    engine_id: str


@runtime_checkable
class Engine(Protocol):
    id: str
    models: dict            # stage -> model name, recorded in the manifest

    def index(self, corpus: list[Talk], out: Path) -> IndexArtifact: ...

    def recommend(self, anchor: Talk, index: IndexArtifact) -> list[Recommendation]: ...
