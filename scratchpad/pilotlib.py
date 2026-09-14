"""Checkpointed, resumable progress for an inline census pilot.

One directory per run:
    QUEUE.json    the rows to work, in order
    RESULTS.json  one record per finished row, rewritten after every row
    STATUS.json   probeable progress — done / total / in_flight / searches_used

Stopping at any point leaves every finished row on disk; re-running with the same
queue resumes from the first row that has no record.
"""
import json
from pathlib import Path


class Run:
    def __init__(self, directory):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    # --- paths -------------------------------------------------------------
    @property
    def _queue_path(self):
        return self.dir / "QUEUE.json"

    @property
    def _results_path(self):
        return self.dir / "RESULTS.json"

    @property
    def _status_path(self):
        return self.dir / "STATUS.json"

    # --- state -------------------------------------------------------------
    def _read(self, path):
        return json.loads(path.read_text()) if path.exists() else []

    def _write(self, path, data):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def queue(self):
        return self._read(self._queue_path)

    def results(self):
        return self._read(self._results_path)

    def enqueue(self, rows):
        """Set the queue. Safe to re-run with the same queue — results survive."""
        self._write(self._queue_path, list(rows))
        self._refresh_status()

    def pending(self):
        done = {r["row"] for r in self.results()}
        return [q for q in self.queue() if q["row"] not in done]

    def start(self, row):
        """Mark a row as in flight, so a probe of STATUS.json names it."""
        self._refresh_status(in_flight=row)

    def record(self, record):
        self._validate(record)
        results = [r for r in self.results() if r["row"] != record["row"]]
        results.append(record)
        results.sort(key=lambda r: r["row"])
        self._write(self._results_path, results)
        self._refresh_status()

    # --- rules -------------------------------------------------------------
    def _validate(self, record):
        """Refuse records the census method forbids, at intake rather than later."""
        if record.get("rung") == 9 and record.get("abstracts_numeric") is not None:
            if "NOT COUNTED" not in (record.get("abstracts") or ""):
                raise ValueError(
                    "a rung-9 figure must carry the NOT COUNTED label: "
                    f"{record.get('conference')}"
                )
        if record.get("abstracts_numeric") is not None and not record.get("source_url"):
            raise ValueError(
                f"a figure needs a source_url: {record.get('conference')}"
            )

    # --- progress ----------------------------------------------------------
    def _refresh_status(self, in_flight=None):
        queue, results = self.queue(), self.results()
        name = None
        if in_flight is not None:
            name = next((q["conference"] for q in queue if q["row"] == in_flight), None)
        self._write(self._status_path, {
            "done": len(results),
            "total": len(queue),
            "in_flight": name,
            "searches_used": sum(r.get("searches_used") or 0 for r in results),
            "remaining": [q["conference"] for q in self.pending()],
        })
