"""Live progress the user can probe at any time: out/status.json plus a
printed line. parallel() runs fn over items on a thread pool, preserves
input order, and reports every few completions."""
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class Status:
    def __init__(self, out: Path):
        self.out = out
        self.t0 = time.time()
        out.mkdir(parents=True, exist_ok=True)

    def set(self, msg: str) -> None:
        elapsed = round(time.time() - self.t0)
        status_path = self.out / "status.json"
        tmp = status_path.with_name(status_path.name + ".tmp")
        tmp.write_text(json.dumps({"phase": msg, "elapsed_s": elapsed}))
        os.replace(tmp, status_path)
        print(f"[{elapsed}s] {msg}", flush=True)


def parallel(label: str, items: Iterable[T], fn: Callable[[T], R],
             workers: int = 8, status: Status | None = None,
             every: int = 10) -> list[R]:
    items = list(items)
    done = 0
    lock = threading.Lock()

    def wrapped(item: T) -> R:
        nonlocal done
        r = fn(item)
        with lock:
            done += 1
            if status and (done % every == 0 or done == len(items)):
                status.set(f"{label} {done}/{len(items)}")
        return r

    if not items:
        return []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(wrapped, items))
