"""One line per engine. ENGINE=<name> selects it. Value is "module:factory";
the factory takes keyword config and returns an Engine."""
import importlib
import json
import os

from gps_core.protocol import Engine

ENGINES: dict[str, str] = {
    "graph_v1": "gps_engines.graph_v1.engine:build",
}


def get_engine(name: str, **config) -> Engine:
    try:
        target = ENGINES[name]
    except KeyError:
        raise KeyError(f"unknown engine {name!r}; known: {sorted(ENGINES)}") from None
    module, _, factory = target.partition(":")
    if not factory:
        raise ValueError(f"engine {name!r} maps to {target!r}; expected 'module:factory'")
    return getattr(importlib.import_module(module), factory)(**config)


def engine_from_env() -> Engine:
    """ENGINE names the engine (default graph_v1); ENGINE_CONFIG is an optional
    JSON object of keyword config for its factory, e.g.
    ENGINE_CONFIG='{"pair_judge_model": "deepseek-reasoner"}'."""
    name = os.environ.get("ENGINE", "graph_v1")
    config = json.loads(os.environ.get("ENGINE_CONFIG", "{}"))
    return get_engine(name, **config)
