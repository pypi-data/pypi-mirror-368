# Typer CLI command definition (must be above __main__ block)

import ast
import configparser
import logging
import os

import typer

from .ast_utils import normalize_ast, remove_dead_code
from .helpers_logic import (
    decorator_change,
    get_code_literals,
    import_addition_or_removal,
    logic_change_ignoring_unreachable,
    uncommented_code_detected,
    variable_name_change_in_used_code,
)
from .helpers_trivial import (
    is_minor_deletion,
    only_comments_changed,
    only_docstring_changed,
    only_function_order_changed,
    only_imports_reordered,
    only_meta_vars_changed,
)

# Global config for type-safe access in get_changed_files
_GLOBAL_CONFIG: dict = {}

# Typer app definition must be above all Typer CLI command decorators

app = typer.Typer(
    help="""
Detect real code changes in Python files.

Examples:
  python -m python_code_changed.cli --help
  python -m python_code_changed.cli file1.py file2.py
  python -m python_code_changed.cli --base-branch origin/main --debug
  python -m python_code_changed.cli --file-extensions .py .pyi --exclude-files test_*.py
  python -m python_code_changed.cli --config-path real_code_checks.ini

By default (no arguments), analyzes all staged files for real code changes compared to the base branch.
"""
)


# Typer CLI command definition must be immediately after app definition
@app.command()
def detect(
    files: list[str] | None = typer.Argument(None, help="Files to analyze (default: changed files)"),
    staged: bool = typer.Option(False, "--staged", help="Analyze all staged files (git diff --name-only --cached)"),
    base_branch: str = typer.Option("origin/main", help="Base branch to compare against"),
    config_path: str = typer.Option("real_code_checks.ini", help="Path to config file for code change checks"),
    log_level: str = typer.Option("CRITICAL", help="Logging level (e.g. INFO, DEBUG)"),
    log_format: str = typer.Option("%(asctime)s %(levelname)s %(message)s", help="Logging format string"),
    debug: bool = typer.Option(False, help="Show detailed debug info for all files"),
    file_extensions: list[str] | None = typer.Option(None, help="List of file extensions to include (e.g. .py .pyi)"),
    diff_command: str | None = typer.Option(
        None, help="Git diff command to use for changed files (default: git diff --name-only --cached)"
    ),
    exclude_files: list[str] | None = typer.Option(
        None, help="List of file patterns or filenames to exclude from analysis"
    ),
    uncommented_code: bool | None = typer.Option(None, help="Enable uncommented code check"),
    code_literals: bool | None = typer.Option(None, help="Enable code literals check"),
    import_addition: bool | None = typer.Option(None, help="Enable import addition check"),
    variable_name_change: bool | None = typer.Option(None, help="Enable variable name change check"),
    decorator_change: bool | None = typer.Option(None, help="Enable decorator change check"),
    minor_deletion: bool | None = typer.Option(None, help="Enable minor deletion check"),
    comments: bool | None = typer.Option(None, help="Enable comments check"),
    imports_reordered: bool | None = typer.Option(None, help="Enable imports reordered check"),
    function_order: bool | None = typer.Option(None, help="Enable function order check"),
    docstring: bool | None = typer.Option(None, help="Enable docstring check"),
    meta_vars: bool | None = typer.Option(None, help="Enable meta vars check"),
    unreachable_code: bool | None = typer.Option(None, help="Enable unreachable code check"),
    output_changed_files: str | None = typer.Option(
        None,
        help=(
            "Optional path to write changed files (one per line). "
            "Writes an empty file when no real code changes are found."
        ),
    ),
):
    """
    Detect real code changes in Python files.
    By default, analyzes all staged files for real code changes compared to the base branch.
    """
    global logger
    logger = setup_logging(log_level, log_format)
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Build config dict using a dataclass for type safety
    from dataclasses import dataclass

    @dataclass
    class Args:
        base_branch: str
        config: str
        log_level: str
        log_format: str
        file_extensions: list[str] | None
        diff_command: str | None
        exclude_files: list[str] | None
        uncommented_code: bool | None
        code_literals: bool | None
        import_addition: bool | None
        variable_name_change: bool | None
        decorator_change: bool | None
        minor_deletion: bool | None
        comments: bool | None
        imports_reordered: bool | None
        function_order: bool | None
        docstring: bool | None
        meta_vars: bool | None
        unreachable_code: bool | None

    args = Args(
        base_branch=base_branch,
        config=config_path,
        log_level=log_level,
        log_format=log_format,
        file_extensions=file_extensions,
        diff_command=diff_command,
        exclude_files=exclude_files,
        uncommented_code=uncommented_code,
        code_literals=code_literals,
        import_addition=import_addition,
        variable_name_change=variable_name_change,
        decorator_change=decorator_change,
        minor_deletion=minor_deletion,
        comments=comments,
        imports_reordered=imports_reordered,
        function_order=function_order,
        docstring=docstring,
        meta_vars=meta_vars,
        unreachable_code=unreachable_code,
    )

    config = load_change_detection_config(config_path, cli_args=args)
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = config
    if staged or (files is None or len(files) == 0):
        files_to_analyze = get_changed_files(base_branch)
    else:
        files_to_analyze = files

    # Exclude files by pattern
    excluded_files = []
    original_files = files_to_analyze[:]
    if config.get("exclude_files"):
        import fnmatch

        files_to_analyze = [
            f
            for f in files_to_analyze
            if not any(fnmatch.fnmatch(f, pat) or os.path.basename(f) == pat for pat in config["exclude_files"])
        ]
    excluded_files = [f for f in original_files if f not in files_to_analyze]
    if not files_to_analyze:
        # Modern, Typer-style summary output for excluded/all filtered
        typer.secho("\n═════════════════════════════════════════════════════", fg=typer.colors.CYAN, bold=True)
        typer.secho("   Real Code Change Detection Summary", fg=typer.colors.CYAN, bold=True)
        typer.secho("═════════════════════════════════════════════════════\n", fg=typer.colors.CYAN, bold=True)
        typer.secho("Files analyzed:           0", fg=typer.colors.BRIGHT_WHITE)
        typer.secho("Files with real changes:  0", fg=typer.colors.BRIGHT_BLACK)
        typer.secho("Files with no changes:    0", fg=typer.colors.BRIGHT_BLACK)
        typer.secho("Files with errors:        0", fg=typer.colors.BRIGHT_BLACK)
        if excluded_files:
            typer.secho("\nFiles excluded from analysis:", fg=typer.colors.YELLOW, bold=True)
            for f in excluded_files:
                typer.secho(f"  • {f}", fg=typer.colors.YELLOW)
        typer.secho("\nFinal outcome: Was real code changed? NO", fg=typer.colors.MAGENTA, bold=True)
        typer.secho("═════════════════════════════════════════════════════\n", fg=typer.colors.CYAN, bold=True)
        # If requested, still create an empty output file
        if output_changed_files:
            try:
                out_dir = os.path.dirname(output_changed_files)
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)
                with open(output_changed_files, "w") as f_out:
                    pass
                typer.secho(
                    f"\nChanged files written to: {output_changed_files} (no entries)",
                    fg=typer.colors.GREEN,
                )
            except Exception as e:
                typer.secho(
                    f"\nFailed to write changed files to {output_changed_files}: {e}",
                    fg=typer.colors.RED,
                )
        raise typer.Exit()

    logger.info(f"Analyzing files: {files_to_analyze}")
    logger.debug(f"Config used: {config}")
    if not files_to_analyze:
        # Modern, Typer-style summary output for no changed files
        typer.secho("\n═════════════════════════════════════════════════════", fg=typer.colors.CYAN, bold=True)
        typer.secho("   Real Code Change Detection Summary", fg=typer.colors.CYAN, bold=True)
        typer.secho("═════════════════════════════════════════════════════\n", fg=typer.colors.CYAN, bold=True)
        typer.secho("Files analyzed:           0", fg=typer.colors.BRIGHT_WHITE)
        typer.secho("Files with real changes:  0", fg=typer.colors.BRIGHT_BLACK)
        typer.secho("Files with no changes:    0", fg=typer.colors.BRIGHT_BLACK)
        typer.secho("Files with errors:        0", fg=typer.colors.BRIGHT_BLACK)
        if excluded_files:
            typer.secho("\nFiles excluded from analysis:", fg=typer.colors.YELLOW, bold=True)
            for f in excluded_files:
                typer.secho(f"  • {f}", fg=typer.colors.YELLOW)
        typer.secho("\nFinal outcome: Was real code changed? NO", fg=typer.colors.MAGENTA, bold=True)
        typer.secho("═════════════════════════════════════════════════════\n", fg=typer.colors.CYAN, bold=True)
        # If requested, still create an empty output file
        if output_changed_files:
            try:
                out_dir = os.path.dirname(output_changed_files)
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)
                with open(output_changed_files, "w") as f_out:
                    pass
                typer.secho(
                    f"\nChanged files written to: {output_changed_files} (no entries)",
                    fg=typer.colors.GREEN,
                )
            except Exception as e:
                typer.secho(
                    f"\nFailed to write changed files to {output_changed_files}: {e}",
                    fg=typer.colors.RED,
                )
        raise typer.Exit()

    results: list[tuple[str, bool | None]] = []
    for file in files_to_analyze:
        logger.info(f"Processing file: {file}")
        try:
            with open(file) as f:  # type: ignore[assignment]
                after = f.read()  # type: ignore[attr-defined]
            logger.debug(f"Loaded staged file {file}")
        except Exception as e:
            logger.error(f"Could not read staged file {file}: {e}")
            results.append((file, None))
            continue

        import subprocess

        try:
            before = subprocess.check_output(
                ["git", "show", f"{base_branch}:{file}"], text=True, stderr=subprocess.DEVNULL
            )
            logger.debug(f"Loaded base branch ({base_branch}) version for {file}")
        except subprocess.CalledProcessError:
            logger.warning(f"File {file} not found in base branch {base_branch}. Treating as new file.")
            before = ""
        except Exception as e:
            logger.error(f"Error retrieving base branch version for {file}: {e}")
            before = ""

        try:
            result = has_real_logic_change(before, after, config=config)
            logger.info(f"File: {file}\n  Real logic change detected: {result}\n")
            results.append((file, result))
        except Exception as e:
            logger.error(f"Error comparing {file}: {e}")
            results.append((file, None))

    changed_files = [f for f, changed in results if changed is True]
    unchanged_files = [f for f, changed in results if changed is False]
    error_files = [f for f, changed in results if changed is None]

    # Modern, Typer-style summary output
    typer.secho("\n═════════════════════════════════════════════════════", fg=typer.colors.CYAN, bold=True)
    typer.secho("   Real Code Change Detection Summary", fg=typer.colors.CYAN, bold=True)
    typer.secho("═════════════════════════════════════════════════════\n", fg=typer.colors.CYAN, bold=True)
    typer.secho(f"Files analyzed:           {len(results)}", fg=typer.colors.BRIGHT_WHITE)
    typer.secho(
        f"Files with real changes:  {len(changed_files)}",
        fg=typer.colors.GREEN if changed_files else typer.colors.BRIGHT_BLACK,
    )
    typer.secho(
        f"Files with no changes:    {len(unchanged_files)}",
        fg=typer.colors.BLUE if unchanged_files else typer.colors.BRIGHT_BLACK,
    )
    typer.secho(
        f"Files with errors:        {len(error_files)}",
        fg=typer.colors.RED if error_files else typer.colors.BRIGHT_BLACK,
    )

    if changed_files:
        typer.secho("\nFiles with real code changes:", fg=typer.colors.GREEN, bold=True)
        for f in changed_files:
            typer.secho(f"  • {f}", fg=typer.colors.GREEN)
    if unchanged_files:
        typer.secho("\nFiles with no real code changes:", fg=typer.colors.BLUE, bold=True)
        for f in unchanged_files:
            typer.secho(f"  • {f}", fg=typer.colors.BLUE)
    if error_files:
        typer.secho("\nFiles with errors:", fg=typer.colors.RED, bold=True)
        for f in error_files:
            typer.secho(f"  • {f}", fg=typer.colors.RED)
    if config.get("exclude_files"):
        all_files = changed_files + unchanged_files + error_files
        excluded_files = [f for f in config.get("exclude_files", []) if f not in all_files]
        if excluded_files:
            typer.secho("\nFiles excluded from analysis:", fg=typer.colors.YELLOW, bold=True)
            for f in excluded_files:
                typer.secho(f"  • {f}", fg=typer.colors.YELLOW)
    overall = "YES" if len(changed_files) > 0 else "NO"
    typer.secho(f"\nFinal outcome: Was real code changed? {overall}", fg=typer.colors.MAGENTA, bold=True)
    typer.secho("═════════════════════════════════════════════════════\n", fg=typer.colors.CYAN, bold=True)
    # Optionally write changed files to a txt file (always create file if path provided)
    if output_changed_files is not None:
        try:
            out_dir = os.path.dirname(output_changed_files)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_changed_files, "w") as f_out:
                for fname in changed_files:
                    f_out.write(f"{fname}\n")
            message_suffix = "" if changed_files else " (no entries)"
            typer.secho(
                f"\nChanged files written to: {output_changed_files}{message_suffix}",
                fg=typer.colors.GREEN,
            )
        except Exception as e:
            typer.secho(
                f"\nFailed to write changed files to {output_changed_files}: {e}",
                fg=typer.colors.RED,
            )

    if error_files:
        raise typer.Exit(1)


# Setup logging (configurable)
def setup_logging(level="INFO", fmt="%(asctime)s %(levelname)s %(message)s"):
    """
    Sets up and returns a logger for the real_code_change module with the specified level and format.
    """
    logger = logging.getLogger("real_code_change")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger


logger = setup_logging()


def get_changed_files(base_branch: str = "origin/main") -> list[str]:
    """
    Returns a list of changed files (filtered by extension) compared to the base branch.
    Uses git diff and configuration options.
    """
    import subprocess
    from shlex import split

    # Get config for file extensions and diff command
    global _GLOBAL_CONFIG
    config = _GLOBAL_CONFIG if "_GLOBAL_CONFIG" in globals() else None
    file_extensions = config.get("file_extensions", [".py"]) if config else [".py"]
    diff_command = (
        config.get("diff_command", "git diff --name-only --cached") if config else "git diff --name-only --cached"
    )
    logger.debug(f"Running diff command: {diff_command}")
    try:
        result = subprocess.check_output(split(diff_command), text=True)
        logger.info(f"Changed files detected: {result.splitlines()}")
        filtered_files = [f for f in result.splitlines() if any(f.endswith(ext) for ext in file_extensions)]
        logger.debug(f"Filtered files by extension {file_extensions}: {filtered_files}")
        return filtered_files
    except Exception as e:
        logger.error(f"Error getting changed files: {e}")
        return []


def load_change_detection_config(config_path="real_code_checks.ini", cli_args=None):
    """
    Loads change detection configuration from an INI file and CLI arguments.
    Returns a dictionary of settings for checks and logging.
    """
    parser = configparser.ConfigParser()
    parser.read(config_path)
    # Logging config
    log_level = parser.get("logging", "level", fallback=None)
    try:
        log_format = parser.get("logging", "format", raw=True, fallback=None)
    except TypeError:
        # For older Python/configparser versions
        log_format = parser.get("logging", "format", fallback=None)
    checks = {
        "uncommented_code": parser.getboolean("checks", "uncommented_code", fallback=True),
        "code_literals": parser.getboolean("checks", "code_literals", fallback=True),
        "import_addition": parser.getboolean("checks", "import_addition", fallback=True),
        "variable_name_change": parser.getboolean("checks", "variable_name_change", fallback=True),
        "decorator_change": parser.getboolean("checks", "decorator_change", fallback=True),
        "minor_deletion": parser.getboolean("checks", "minor_deletion", fallback=True),
        "comments": parser.getboolean("checks", "comments", fallback=True),
        "imports_reordered": parser.getboolean("checks", "imports_reordered", fallback=True),
        "function_order": parser.getboolean("checks", "function_order", fallback=True),
        "docstring": parser.getboolean("checks", "docstring", fallback=True),
        "meta_vars": parser.getboolean("checks", "meta_vars", fallback=True),
        "unreachable_code": parser.getboolean("checks", "unreachable_code", fallback=True),
    }
    if cli_args and hasattr(cli_args, "log_level") and cli_args.log_level:
        log_level = cli_args.log_level
    if cli_args and hasattr(cli_args, "log_format") and cli_args.log_format:
        log_format = cli_args.log_format
    checks["log_level"] = log_level if log_level else "INFO"
    checks["log_format"] = log_format if log_format else "%(asctime)s %(levelname)s %(message)s"
    logger.info(f"Loading config from {config_path}")
    # File extensions config
    file_extensions = []
    if parser.has_section("analysis") and parser.has_option("analysis", "file_extensions"):
        ext_cfg = parser.get("analysis", "file_extensions", fallback=None)
        if ext_cfg:
            file_extensions += [e.strip() for e in ext_cfg.split(",") if e.strip()]
    if cli_args and hasattr(cli_args, "file_extensions") and cli_args.file_extensions:
        file_extensions += cli_args.file_extensions
    checks["file_extensions"] = file_extensions if file_extensions else [".py"]

    # Git diff command config
    diff_command = parser.get("git", "diff_command", fallback=None)
    if cli_args and hasattr(cli_args, "diff_command") and cli_args.diff_command:
        diff_command = cli_args.diff_command
    checks["diff_command"] = diff_command if diff_command else "git diff --name-only --cached"
    # Git base branch config
    base_branch = parser.get("git", "base_branch", fallback=None)
    if cli_args and hasattr(cli_args, "base_branch") and cli_args.base_branch:
        base_branch = cli_args.base_branch
    checks["base_branch"] = base_branch if base_branch else "origin/main"
    # Exclude files support
    exclude_files = []
    if parser.has_section("analysis") and parser.has_option("analysis", "exclude_files"):
        exclude_files_cfg = parser.get("analysis", "exclude_files", fallback=None)
        if exclude_files_cfg:
            exclude_files += [f.strip() for f in exclude_files_cfg.split(",") if f.strip()]
    if cli_args and hasattr(cli_args, "exclude_files") and cli_args.exclude_files:
        exclude_files += cli_args.exclude_files
    checks["exclude_files"] = exclude_files
    # Override with CLI args if provided
    if cli_args:
        for key in checks:
            arg_val = getattr(cli_args, key, None)
            if arg_val is not None:
                checks[key] = arg_val
    return checks


def add_check_args_to_parser(parser):
    parser.add_argument(
        "--file-extensions", nargs="+", type=str, help="List of file extensions to include (e.g. .py .pyi)"
    )
    parser.add_argument(
        "--diff-command",
        type=str,
        help="Git diff command to use for changed files (default: git diff --name-only --cached)",
    )
    parser.add_argument("--uncommented_code", action="store_true", help="Enable uncommented code check")
    parser.add_argument("--no-uncommented_code", action="store_true", help="Disable uncommented code check")
    parser.add_argument("--code_literals", action="store_true", help="Enable code literals check")
    parser.add_argument("--no-code_literals", action="store_true", help="Disable code literals check")
    parser.add_argument("--import_addition", action="store_true", help="Enable import addition check")
    parser.add_argument("--no-import_addition", action="store_true", help="Disable import addition check")
    parser.add_argument("--variable_name_change", action="store_true", help="Enable variable name change check")
    parser.add_argument("--no-variable_name_change", action="store_true", help="Disable variable name change check")
    parser.add_argument("--decorator_change", action="store_true", help="Enable decorator change check")
    parser.add_argument("--no-decorator_change", action="store_true", help="Disable decorator change check")
    parser.add_argument("--minor_deletion", action="store_true", help="Enable minor deletion check")
    parser.add_argument("--no-minor_deletion", action="store_true", help="Disable minor deletion check")
    parser.add_argument("--comments", action="store_true", help="Enable comments check")
    parser.add_argument("--no-comments", action="store_true", help="Disable comments check")
    parser.add_argument("--imports_reordered", action="store_true", help="Enable imports reordered check")
    parser.add_argument("--no-imports_reordered", action="store_true", help="Disable imports reordered check")
    parser.add_argument("--function_order", action="store_true", help="Enable function order check")
    parser.add_argument("--no-function_order", action="store_true", help="Disable function order check")
    parser.add_argument("--docstring", action="store_true", help="Enable docstring check")
    parser.add_argument("--no-docstring", action="store_true", help="Disable docstring check")
    parser.add_argument("--meta_vars", action="store_true", help="Enable meta vars check")
    parser.add_argument("--no-meta_vars", action="store_true", help="Disable meta vars check")
    parser.add_argument("--unreachable_code", action="store_true", help="Enable unreachable code check")
    parser.add_argument("--no-unreachable_code", action="store_true", help="Disable unreachable code check")
    parser.add_argument(
        "--exclude_files", nargs="+", type=str, help="List of file patterns or filenames to exclude from analysis"
    )
    return parser


# Main function: Detect real logic change
def has_real_logic_change(before: str, after: str, config=None) -> bool:
    logger.debug("has_real_logic_change called")
    logger.info("Starting logic change detection")
    if config is None:
        config = load_change_detection_config()
    logger.debug("Removing unreachable code from both versions")
    before_clean = remove_dead_code(before)
    after_clean = remove_dead_code(after)

    # Logic change checks (operate on cleaned code)
    if config.get("uncommented_code", True) and uncommented_code_detected(before_clean, after_clean):
        logger.info("Uncommented code detected as logic change")
        logger.debug("uncommented_code_detected returned True")
        return True
    if config.get("code_literals", True) and get_code_literals(before_clean) != get_code_literals(after_clean):
        logger.info("Code literals changed")
        logger.debug("get_code_literals returned True")
        return True
    if config.get("import_addition", True) and import_addition_or_removal(before_clean, after_clean):
        logger.info("Import addition or removal detected")
        logger.debug("import_addition_or_removal returned True")
        return True
    if config.get("variable_name_change", True) and variable_name_change_in_used_code(before_clean, after_clean):
        logger.info("Variable name change detected in used code")
        logger.debug("variable_name_change_in_used_code returned True")
        return True
    if config.get("decorator_change", True) and decorator_change(before_clean, after_clean):
        logger.info("Decorator change detected")
        logger.debug("decorator_change returned True")
        return True

    # Trivial change checks (operate on original code)
    if config.get("minor_deletion", True) and is_minor_deletion(before, after):
        logger.info("Minor deletion detected, not a real logic change")
        logger.debug("is_minor_deletion returned True")
        return False
    if config.get("comments", True) and only_comments_changed(before, after):
        logger.info("Only comments changed, not a real logic change")
        logger.debug("only_comments_changed returned True")
        return False
    if config.get("imports_reordered", True) and only_imports_reordered(before, after):
        logger.info("Only imports reordered, not a real logic change")
        logger.debug("only_imports_reordered returned True")
        return False
    if config.get("function_order", True) and only_function_order_changed(before, after):
        logger.info("Only function order changed, not a real logic change")
        logger.debug("only_function_order_changed returned True")
        return False
    if config.get("docstring", True) and only_docstring_changed(before, after):
        logger.info("Only docstring changed, not a real logic change")
        logger.debug("only_docstring_changed returned True")
        return False
    if config.get("meta_vars", True) and only_meta_vars_changed(before, after):
        logger.info("Only meta vars changed, not a real logic change")
        logger.debug("only_meta_vars_changed returned True")
        return False

    # Ignore changes inside unreachable code (e.g., if False blocks)
    if config.get("unreachable_code", True) and not logic_change_ignoring_unreachable(before, after):
        logger.info("No logic change detected (ignoring unreachable code)")
        logger.debug("logic_change_ignoring_unreachable returned False")
        return False

    # Otherwise, do AST normalization and compare on cleaned code
    try:
        logger.debug("Parsing and normalizing ASTs for both versions")
        before_ast = normalize_ast(ast.parse(before_clean))
        after_ast = normalize_ast(ast.parse(after_clean))
    except Exception as e:
        logger.error(f"AST parsing error: {e}")
        return True
    result = ast.dump(before_ast) != ast.dump(after_ast)
    if result:
        logger.info("AST comparison: real logic change detected")
    else:
        logger.info("AST comparison: no real logic change detected")
    logger.debug(f"AST comparison result: {result}")
    return result
    print("DEBUG: has_real_logic_change called")
    # Remove unreachable code from both versions
    before_clean = remove_dead_code(before)
    after_clean = remove_dead_code(after)

    # Logic change checks (operate on cleaned code)
    if uncommented_code_detected(before_clean, after_clean):
        print("DEBUG: uncommented_code_detected returned True")
        return True
    if get_code_literals(before_clean) != get_code_literals(after_clean):
        print("DEBUG: get_code_literals returned True")
        return True
    if import_addition_or_removal(before_clean, after_clean):
        print("DEBUG: import_addition_or_removal returned True")
        return True
    if variable_name_change_in_used_code(before_clean, after_clean):
        print("DEBUG: variable_name_change_in_used_code returned True")
        return True
    if decorator_change(before_clean, after_clean):
        print("DEBUG: decorator_change returned True")
        return True

    # Trivial change checks (operate on original code)
    if is_minor_deletion(before, after):
        return False
    if only_comments_changed(before, after):
        return False
    if only_imports_reordered(before, after):
        return False
    if only_function_order_changed(before, after):
        return False
    if only_docstring_changed(before, after):
        return False
    if only_meta_vars_changed(before, after):
        print("DEBUG: only_meta_vars_changed returned True")
        return False

    # Ignore changes inside unreachable code (e.g., if False blocks)
    if not logic_change_ignoring_unreachable(before, after):
        return False

    # Otherwise, do AST normalization and compare on cleaned code
    try:
        before_ast = normalize_ast(ast.parse(before_clean))
        after_ast = normalize_ast(ast.parse(after_clean))
    except Exception:
        return True
    return ast.dump(before_ast) != ast.dump(after_ast)

    # Short-circuit for trivial changes
    if is_minor_deletion(before, after):
        return False
    if only_comments_changed(before, after):
        return False
    if only_imports_reordered(before, after):
        return False
    if only_function_order_changed(before, after):
        return False
    if only_docstring_changed(before, after):
        return False
    if only_meta_vars_changed(before, after):
        print("DEBUG: only_meta_vars_changed returned True")
        return False

    # Otherwise, do AST normalization and compare on code with unreachable code removed
    # Ignore changes inside unreachable code (e.g., if False blocks)
    if not logic_change_ignoring_unreachable(before, after):
        return False
    before_no_dead = remove_dead_code(before)
    after_no_dead = remove_dead_code(after)
    try:
        before_ast = normalize_ast(ast.parse(before_no_dead))
        after_ast = normalize_ast(ast.parse(after_no_dead))
    except Exception:
        return True
    return ast.dump(before_ast) != ast.dump(after_ast)


# Ensure script runs when executed directly (move to end of file)
if __name__ == "__main__":
    app()
