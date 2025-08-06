import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import cbatch


def test_export_all_suffix(tmp_path, capsys, monkeypatch):
    script = tmp_path / "job.sh"
    script.write_text("#!/bin/bash\n")
    monkeypatch.setattr(sys, "argv", [
        "cbatch",
        "--cluster",
        "foo",
        "--dry-run",
        "--export",
        "VAR=1,ALL",
        str(script),
    ])
    cbatch.main()
    out = capsys.readouterr().out
    assert "--export=VAR=1,ALL" in out
    assert "--export=ALL,VAR=1,ALL" not in out
