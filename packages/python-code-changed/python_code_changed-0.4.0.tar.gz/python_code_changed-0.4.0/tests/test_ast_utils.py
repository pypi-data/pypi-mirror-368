import ast

from python_code_changed.ast_utils import normalize_ast


def test_normalize_ast_removes_lineno():
    code = """def f():\n    pass\n"""
    tree = ast.parse(code)
    norm = normalize_ast(tree)
    assert hasattr(norm, "body")
    for node in ast.walk(norm):
        assert not getattr(node, "lineno", None)


def test_normalize_ast_docstring():
    code = 'def f():\n    """Docstring"""\n    pass\n'
    tree = ast.parse(code)
    norm = normalize_ast(tree)
    # The first statement in the function should be ast.Pass (docstring replaced)
    func = norm.body[0]
    assert isinstance(func.body[0], ast.Pass)
