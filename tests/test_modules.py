import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import cbatch


def test_missing_modules_file(tmp_path, capsys, monkeypatch):
    script = tmp_path / "job.sh"
    script.write_text("#!/bin/bash\n")
    missing = tmp_path / "missing.txt"
    monkeypatch.setattr(sys, "argv", [
        "cbatch",
        "--cluster",
        "foo",
        "--modules",
        str(missing),
        str(script),
    ])
    with pytest.raises(SystemExit) as excinfo:
        cbatch.main()
    assert excinfo.value.code == 1
    err = capsys.readouterr().err
    assert "modules file" in err
    assert str(missing) in err
