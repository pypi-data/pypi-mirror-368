import fnmatch
import logging
import os

from python_code_changed.cli import (
    has_real_logic_change,
    load_change_detection_config,
    only_imports_reordered,
    setup_logging,
)

# 1. Whitespace-only changes
WHITESPACE_BEFORE = "x = 1"
WHITESPACE_AFTER = "x     =     1"


def test_whitespace_only():
    assert not has_real_logic_change(WHITESPACE_BEFORE, WHITESPACE_AFTER)


# 2. Reordering imports
IMPORTS_BEFORE = "import os\nimport sys"
IMPORTS_AFTER = "import sys\nimport os"


def test_import_reordering():
    assert only_imports_reordered(IMPORTS_BEFORE, IMPORTS_AFTER)
    assert not has_real_logic_change(IMPORTS_BEFORE, IMPORTS_AFTER)


# 3. Change in variable name in unused code
DEAD_CODE_BEFORE = "if False:\n    a = 5"
DEAD_CODE_AFTER = "if False:\n    b = 5"


def test_dead_code_change():
    assert not has_real_logic_change(DEAD_CODE_BEFORE, DEAD_CODE_AFTER)


# 4. Change in formatting / string quotes
QUOTES_BEFORE = 'print("hello")'
QUOTES_AFTER = "print('hello')"


def test_string_quote_change():
    assert not has_real_logic_change(QUOTES_BEFORE, QUOTES_AFTER)


# 5. Commented out logic
COMMENTED_BEFORE = '# print("hello")'
COMMENTED_AFTER = 'print("hello")'


def test_commented_out_logic():
    assert has_real_logic_change(COMMENTED_BEFORE, COMMENTED_AFTER)


# 6. Change in docstring format
DOCSTRING_BEFORE = 'def f():\n    """This function does something."""\n    pass'
DOCSTRING_AFTER = 'def f():\n    """This function does something important."""\n    pass'


def test_docstring_change():
    assert not has_real_logic_change(DOCSTRING_BEFORE, DOCSTRING_AFTER)


# 7. Changes in __doc__, __version__, or __author__
META_BEFORE = '__version__ = "1.0"'
META_AFTER = '__version__ = "1.1"'


def test_meta_change():
    # This is configurable; for now, treat as not logic change
    assert not has_real_logic_change(META_BEFORE, META_AFTER)


# 8. Function reorderings (same body)
FUNC_ORDER_BEFORE = "def a(): pass\ndef b(): pass"
FUNC_ORDER_AFTER = "def b(): pass\ndef a(): pass"


def test_function_reordering():
    assert not has_real_logic_change(FUNC_ORDER_BEFORE, FUNC_ORDER_AFTER)


# 9. Literal value changes
LITERAL_BEFORE = 'print("foo")'
LITERAL_AFTER = 'print("bar")'


def test_literal_change():
    assert has_real_logic_change(LITERAL_BEFORE, LITERAL_AFTER)


# 10. Adding unreachable code
UNREACHABLE_BEFORE = "x = 1"
UNREACHABLE_AFTER = "x = 1\nif False:\n    y = 2"


def test_add_unreachable_code():
    assert not has_real_logic_change(UNREACHABLE_BEFORE, UNREACHABLE_AFTER)


# 11. Changing order of class definitions
CLASS_ORDER_BEFORE = "class A: pass\nclass B: pass"
CLASS_ORDER_AFTER = "class B: pass\nclass A: pass"


def test_class_order_change():
    assert not has_real_logic_change(CLASS_ORDER_BEFORE, CLASS_ORDER_AFTER)


# 12. Changing function signature
FUNC_SIG_BEFORE = "def f(x): return x"
FUNC_SIG_AFTER = "def f(x, y=2): return x + y"


def test_function_signature_change():
    assert has_real_logic_change(FUNC_SIG_BEFORE, FUNC_SIG_AFTER)


# 13. Adding a function
ADD_FUNC_BEFORE = "def a(): pass"
ADD_FUNC_AFTER = "def a(): pass\ndef b(): pass"


def test_add_function():
    assert has_real_logic_change(ADD_FUNC_BEFORE, ADD_FUNC_AFTER)


# 14. Changing boolean literal
BOOL_BEFORE = "x = True"
BOOL_AFTER = "x = False"


def test_boolean_literal_change():
    assert has_real_logic_change(BOOL_BEFORE, BOOL_AFTER)


# 15. Changing numeric literal
NUM_BEFORE = "x = 1"
NUM_AFTER = "x = 2"


def test_numeric_literal_change():
    assert has_real_logic_change(NUM_BEFORE, NUM_AFTER)


# 16. Adding an import statement
IMPORT_ADD_BEFORE = "import os"
IMPORT_ADD_AFTER = "import os\nimport sys"


def test_import_addition():
    assert has_real_logic_change(IMPORT_ADD_BEFORE, IMPORT_ADD_AFTER)


# 17. Changing function body
FUNC_BODY_BEFORE = "def f():\n    return 1"
FUNC_BODY_AFTER = "def f():\n    return 2"


def test_function_body_change():
    assert has_real_logic_change(FUNC_BODY_BEFORE, FUNC_BODY_AFTER)


# 18. Changing comment inside function
COMMENT_IN_FUNC_BEFORE = "def f():\n    # comment\n    return 1"
COMMENT_IN_FUNC_AFTER = "def f():\n    # new comment\n    return 1"


def test_comment_inside_function():
    assert not has_real_logic_change(COMMENT_IN_FUNC_BEFORE, COMMENT_IN_FUNC_AFTER)


# 19. Changing multiline string (not docstring)
MULTILINE_BEFORE = 'x = """foo"""'
MULTILINE_AFTER = 'x = """bar"""'


def test_multiline_string_change():
    assert has_real_logic_change(MULTILINE_BEFORE, MULTILINE_AFTER)


# 20. Changing variable name in used code
VAR_USED_BEFORE = "x = 1\nprint(x)"
VAR_USED_AFTER = "y = 1\nprint(y)"


def test_variable_name_used_change():
    assert has_real_logic_change(VAR_USED_BEFORE, VAR_USED_AFTER)


# 21. Adding a decorator
DECORATOR_BEFORE = "def f():\n    return 1"
DECORATOR_AFTER = "@staticmethod\ndef f():\n    return 1"


def test_add_decorator():
    assert has_real_logic_change(DECORATOR_BEFORE, DECORATOR_AFTER)


# 22. Exclusion logic test


def test_exclusion_logic():
    # Simulate CLI args and config
    files = ["foo.py", "bar.py", "test.py", "helpers_trivial.py"]

    # Exclude test.py and helpers_trivial.py
    class Args:
        exclude_files = ["test.py", "helpers_trivial.py"]

    config = load_change_detection_config(config_path="", cli_args=Args())

    filtered = [
        f
        for f in files
        if not any(fnmatch.fnmatch(f, pat) or os.path.basename(f) == pat for pat in config.get("exclude_files", []))
    ]
    assert filtered == ["foo.py", "bar.py"]


# 23. Logging level configuration


def test_logging_level_config(monkeypatch):
    # Simulate config with log_level DEBUG
    class Args:
        log_level = "DEBUG"
        log_format = "%(levelname)s %(message)s"

    config = load_change_detection_config(config_path="", cli_args=Args())
    logger = setup_logging(config.get("log_level"), config.get("log_format"))
    # Should be DEBUG level
    assert logger.level == logging.DEBUG

    # Simulate config with log_level ERROR
    class Args2:
        log_level = "ERROR"
        log_format = "%(levelname)s %(message)s"

    config2 = load_change_detection_config(config_path="", cli_args=Args2())
    logger2 = setup_logging(config2.get("log_level"), config2.get("log_format"))
    assert logger2.level == logging.ERROR
