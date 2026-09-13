"""One line per engine. ENGINE=<name> selects it. Value is "module:factory";
the factory takes keyword config and returns an Engine."""
import importlib

from gps_core.protocol import Engine

ENGINES: dict[str, str] = {
    "graph_v1": "gps_engines.graph_v1.engine:build",
}


def get_engine(name: str, **config) -> Engine:
    try:
        target = ENGINES[name]
    except KeyError:
        raise KeyError(f"unknown engine {name!r}; known: {sorted(ENGINES)}") from None
    module, factory = target.split(":")
    return getattr(importlib.import_module(module), factory)(**config)
