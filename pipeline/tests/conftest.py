import json
import pytest


@pytest.fixture
def archive(tmp_path):
    """Mimics data/gps2026 layout: events/*.json + presentations/*.json."""
    (tmp_path / "events").mkdir()
    (tmp_path / "presentations").mkdir()
    (tmp_path / "events" / "1.json").write_text(json.dumps({
        "id": 1, "title": "Session A", "sponsor_units": ["DCMP"],
        "presentation_ids": [10, 11],
        "periods": [{"start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T16:24:00.000Z"}],
    }))
    for pid, title in [(10, "Talk ten"), (11, "Talk eleven")]:
        (tmp_path / "presentations" / f"{pid}.json").write_text(json.dumps({
            "id": pid, "title": title, "abstract": f"Abstract of {title}.",
            "is_withdrawn": False, "topics": ["Condensed Matter"],
            "start": "2026-03-16T14:00:00.000Z", "end": "2026-03-16T14:12:00.000Z",
        }))
    return tmp_path
