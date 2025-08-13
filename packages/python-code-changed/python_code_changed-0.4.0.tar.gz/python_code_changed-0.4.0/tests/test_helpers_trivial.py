from python_code_changed.helpers_trivial import (
    only_comments_changed,
    only_imports_reordered,
)


def test_only_comments_changed():
    before = "x = 1  # comment"
    after = "x = 1  # another comment"
    assert only_comments_changed(before, after)
    assert only_comments_changed("# just a comment", "# just a comment")
    assert not only_comments_changed("x = 1", "x = 2")


def test_only_imports_reordered():
    before = "import os\nimport sys\nx = 1"
    after = "import sys\nimport os\nx = 1"
    assert only_imports_reordered(before, after)
    assert not only_imports_reordered("import os\nx = 1", "import sys\nx = 2")
