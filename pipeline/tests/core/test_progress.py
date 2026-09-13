import json

from gps_core.progress import Status, parallel


def test_status_writes_probeable_file(tmp_path, capsys):
    s = Status(tmp_path)
    s.set("extraction 3/10")
    d = json.loads((tmp_path / "status.json").read_text())
    assert d["phase"] == "extraction 3/10" and isinstance(d["elapsed_s"], int)
    assert "extraction 3/10" in capsys.readouterr().out


def test_parallel_preserves_order_and_reports(tmp_path):
    s = Status(tmp_path)
    out = parallel("sq", [3, 1, 2], lambda x: x * x, workers=2, status=s)
    assert out == [9, 1, 4]
    assert json.loads((tmp_path / "status.json").read_text())["phase"] == "sq 3/3"


def test_status_set_leaves_no_tmp_litter_and_file_parses(tmp_path):
    s = Status(tmp_path)
    s.set("phase 1")
    assert not (tmp_path / "status.json.tmp").exists()
    assert json.loads((tmp_path / "status.json").read_text())["phase"] == "phase 1"
