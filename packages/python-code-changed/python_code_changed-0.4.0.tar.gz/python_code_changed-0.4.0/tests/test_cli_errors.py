import stat

from typer.testing import CliRunner

from python_code_changed.cli import app

runner = CliRunner()


def test_cli_invalid_config(tmp_path):
    # Create an invalid config file
    config_path = tmp_path / "bad_config.ini"
    config_path.write_text("[bad_section\ninvalid]")
    result = runner.invoke(app, ["detect", "--config", str(config_path), __file__])
    # Now, CLI should return exit code 1 for error cases
    assert result.exit_code == 1 or "Error" in result.output or "exception" in result.output.lower()


def test_cli_unreadable_file(tmp_path):
    # Create a file and remove read permissions
    file_path = tmp_path / "unreadable.py"
    file_path.write_text("x = 1\n")
    file_path.chmod(0)
    try:
        result = runner.invoke(app, ["detect", str(file_path)])
        # The CLI now returns exit code 1 for unreadable files
        assert result.exit_code == 1
    finally:
        # Restore permissions so the file can be deleted
        file_path.chmod(stat.S_IWUSR | stat.S_IRUSR)


def test_cli_nonexistent_file():
    result = runner.invoke(app, ["detect", "this_file_does_not_exist.py"])
    # The CLI now returns exit code 1 for nonexistent files
    assert result.exit_code == 1
