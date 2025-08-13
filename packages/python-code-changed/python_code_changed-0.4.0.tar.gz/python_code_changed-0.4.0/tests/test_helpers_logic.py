from python_code_changed.helpers_logic import (
    _remove_unreachable_code,
    import_addition_or_removal,
)


def test_import_addition_or_removal():
    before = "import os"
    after = "import os\nimport sys"
    assert import_addition_or_removal(before, after)
    assert not import_addition_or_removal(before, before)


def test_remove_unreachable_code():
    code = "x = 1\nif False:\n    y = 2\nz = 3"
    result = _remove_unreachable_code(code)
    assert "y = 2" not in result
    assert "x = 1" in result
    assert "z = 3" in result
