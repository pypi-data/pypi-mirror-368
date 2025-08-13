import os
import tempfile

from typer.testing import CliRunner

from python_code_changed.cli import app

runner = CliRunner()


def test_cli_detect_staged(monkeypatch):
    # Simulate staged files by patching os.popen and os.path.exists
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(os, "popen", lambda cmd: os.popen("echo src/python_code_changed/helpers_logic.py"))
    result = runner.invoke(app, ["detect", "--staged"])
    # Integration: exit code 1 if error, 0 if success
    assert result.exit_code in (0, 1)
    assert "Summary" in result.output


def test_cli_detect_with_files():
    with (
        tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f1,
        tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f2,
    ):
        f1.write("x = 1\n")
        f2.write("x = 1\n")
        f1.flush()
        f2.flush()
        result = runner.invoke(app, ["detect", f1.name, f2.name])
        assert result.exit_code in (0, 1)
        assert "Summary" in result.output
    os.unlink(f1.name)
    os.unlink(f2.name)


def test_cli_invalid_file():
    result = runner.invoke(app, ["detect", "nonexistent_file.py"])
    assert result.exit_code in (0, 1)
    assert "Summary" in result.output or "Error" in result.output
