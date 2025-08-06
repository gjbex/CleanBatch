import sys
import subprocess
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import cbatch


def test_file_not_found_exit_code(tmp_path, monkeypatch, capsys):
    script = tmp_path / "job.sh"
    script.write_text("#!/bin/bash\n")

    def fake_popen(*args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory")

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(sys, "argv", ["cbatch", "--cluster", "foo", str(script)])

    with pytest.raises(SystemExit) as exc_info:
        cbatch.main()

    assert exc_info.value.code == 2
    err = capsys.readouterr().err
    assert "Error:" in err
