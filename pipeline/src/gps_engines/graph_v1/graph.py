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
        # frozenset({a,b}) -> {"strength": int 1-10, "why": str}
        self._edge_attrs: dict[frozenset, dict] = {}
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
        moved = self._names.pop(absorb)
        for name in moved:
            self._canon[name] = keep
        self._names[keep] |= moved
        for other in self._related.pop(absorb, set()):
            self._related[other].discard(absorb)
            attrs = self._edge_attrs.pop(frozenset((absorb, other)), None)
            if other != keep:
                self._related[other].add(keep)
                self._related[keep].add(other)
                if attrs is not None:
                    prev = self._edge_attrs.get(frozenset((keep, other)))
                    if prev is None or attrs["strength"] > prev["strength"]:
                        self._edge_attrs[frozenset((keep, other))] = attrs

    def add_related(self, a: int, b: int, strength: int = 0, why: str = "") -> None:
        if a == b:
            return
        self._related[a].add(b); self._related[b].add(a)
        key = frozenset((a, b))
        prev = self._edge_attrs.get(key)
        # Strongest-wins: aggregation point for edges that collide (directly
        # or via merges of their endpoints).
        if prev is None or strength > prev["strength"]:
            self._edge_attrs[key] = {"strength": int(strength), "why": str(why)}

    def edge_info(self, a: int, b: int) -> dict | None:
        return self._edge_attrs.get(frozenset((a, b)))

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
            "edges": [[min(k), max(k), v["strength"], v["why"]]
                      for k, v in self._edge_attrs.items()],
            "next": self._next,
        }))

    @classmethod
    def load(cls, path: Path) -> "MethodGraph":
        d = json.loads(path.read_text())
        g = cls()
        g._canon = {k: int(v) for k, v in d["canon"].items()}
        g._talks = {int(k): set(v) for k, v in d["talks"].items()}
        g._related = {int(k): set(v) for k, v in d["related"].items()}
        g._edge_attrs = {frozenset((a, b)): {"strength": st, "why": w}
                         for a, b, st, w in d.get("edges", [])}
        g._names = {}
        for name, nid in g._canon.items():
            g._names.setdefault(nid, set()).add(name)
        g._next = d["next"]
        return g
