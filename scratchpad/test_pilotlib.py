"""Tests for pilotlib — checkpointed, resumable progress for an inline census pilot.

The CLAUDE.md rules this exists to satisfy:
  - live progress the user can probe at any time
  - incremental checkpointing: stopped at any point, completed work stays on disk
    and a rerun resumes rather than restarts
"""
import json

import pytest

import pilotlib


@pytest.fixture
def run(tmp_path):
    return pilotlib.Run(tmp_path / "pilot")


def test_a_fresh_run_has_every_queued_row_pending(run):
    run.enqueue([{"row": 443, "conference": "CCS National Congress"},
                 {"row": 478, "conference": "Mendeleev Congress"}])

    assert [r["row"] for r in run.pending()] == [443, 478]


def test_a_recorded_row_leaves_the_pending_queue(run):
    run.enqueue([{"row": 443, "conference": "CCS National Congress"},
                 {"row": 478, "conference": "Mendeleev Congress"}])

    run.record({"row": 443, "conference": "CCS National Congress",
                "outcome": "COUNTED", "abstracts_numeric": 3604,
                "source_url": "https://example.org/programme"})

    assert [r["row"] for r in run.pending()] == [478]


def test_a_recorded_row_is_on_disk_before_the_next_row_starts(run):
    """The checkpoint rule: one row's work survives being stopped mid-queue."""
    run.enqueue([{"row": 443, "conference": "CCS National Congress"},
                 {"row": 478, "conference": "Mendeleev Congress"}])
    run.record({"row": 443, "conference": "CCS National Congress",
                "outcome": "COUNTED", "abstracts_numeric": 3604,
                "source_url": "https://example.org/programme"})

    reopened = pilotlib.Run(run.dir)

    assert [r["row"] for r in reopened.pending()] == [478]
    assert reopened.results()[0]["abstracts_numeric"] == 3604


def test_re_enqueueing_the_same_queue_does_not_discard_recorded_work(run):
    """A rerun resumes rather than restarts."""
    queue = [{"row": 443, "conference": "CCS National Congress"},
             {"row": 478, "conference": "Mendeleev Congress"}]
    run.enqueue(queue)
    run.record({"row": 443, "conference": "CCS National Congress",
                "outcome": "COUNTED", "abstracts_numeric": 3604,
                "source_url": "https://example.org/programme"})

    pilotlib.Run(run.dir).enqueue(queue)

    assert [r["row"] for r in pilotlib.Run(run.dir).pending()] == [478]


def test_recording_the_same_row_twice_overwrites_rather_than_duplicates(run):
    run.enqueue([{"row": 443, "conference": "CCS National Congress"}])
    run.record({"row": 443, "conference": "CCS National Congress",
                "outcome": "UNKNOWN", "abstracts_numeric": None})
    run.record({"row": 443, "conference": "CCS National Congress",
                "outcome": "COUNTED", "abstracts_numeric": 3604,
                "source_url": "https://example.org/programme"})

    assert len(run.results()) == 1
    assert run.results()[0]["outcome"] == "COUNTED"


def test_status_file_is_probeable_and_names_the_row_in_flight(run):
    run.enqueue([{"row": 443, "conference": "CCS National Congress"},
                 {"row": 478, "conference": "Mendeleev Congress"}])
    run.start(443)

    status = json.loads((run.dir / "STATUS.json").read_text())

    assert status["done"] == 0
    assert status["total"] == 2
    assert status["in_flight"] == "CCS National Congress"


def test_status_counts_searches_spent_so_the_budget_stays_visible(run):
    run.enqueue([{"row": 443, "conference": "CCS National Congress"},
                 {"row": 478, "conference": "Mendeleev Congress"}])
    run.record({"row": 443, "conference": "CCS", "outcome": "COUNTED",
                "searches_used": 2})
    run.record({"row": 478, "conference": "Mendeleev", "outcome": "UNKNOWN",
                "searches_used": 3})

    status = json.loads((run.dir / "STATUS.json").read_text())

    assert status["done"] == 2
    assert status["searches_used"] == 5


def test_a_rung_9_figure_without_the_not_counted_label_is_refused(run):
    """The NON-NEGOTIABLE rule: an inferred figure must say it is inferred."""
    run.enqueue([{"row": 543, "conference": "ARABLAB"}])

    with pytest.raises(ValueError, match="NOT COUNTED"):
        run.record({"row": 543, "conference": "ARABLAB", "outcome": "INFERRED",
                    "rung": 9, "abstracts": "~1,200", "abstracts_numeric": 1200})


def test_a_labelled_rung_9_figure_is_accepted(run):
    run.enqueue([{"row": 543, "conference": "ARABLAB"}])

    run.record({"row": 543, "conference": "ARABLAB", "outcome": "INFERRED",
                "rung": 9, "abstracts_numeric": 1200,
                "abstracts": "~1,200 INFERRED FROM ATTENDANCE, NOT COUNTED",
                "source_url": "https://example.org/post-show-report"})

    assert run.results()[0]["abstracts_numeric"] == 1200


def test_a_figure_without_a_source_url_is_refused(run):
    """Rule 2: every number needs an exact-page clickable URL."""
    run.enqueue([{"row": 443, "conference": "CCS National Congress"}])

    with pytest.raises(ValueError, match="source_url"):
        run.record({"row": 443, "conference": "CCS National Congress",
                    "outcome": "COUNTED", "abstracts_numeric": 3604, "rung": 3})


def test_an_unknown_outcome_needs_no_source_url(run):
    run.enqueue([{"row": 443, "conference": "CCS National Congress"}])

    run.record({"row": 443, "conference": "CCS National Congress",
                "outcome": "UNKNOWN", "abstracts_numeric": None})

    assert run.results()[0]["outcome"] == "UNKNOWN"
