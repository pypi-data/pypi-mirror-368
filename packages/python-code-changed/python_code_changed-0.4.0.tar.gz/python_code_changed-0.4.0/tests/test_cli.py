from typer.testing import CliRunner

from python_code_changed.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Detect real code changes" in result.output


def test_cli_no_args():
    result = runner.invoke(app, [])
    # Help or error should now always return exit code 1 for error, 0 for help/success
    assert result.exit_code in (0, 1)


def test_cli_detect_option():
    # This just checks the command is recognized; for full integration, use temp files
    result = runner.invoke(app, ["detect", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
