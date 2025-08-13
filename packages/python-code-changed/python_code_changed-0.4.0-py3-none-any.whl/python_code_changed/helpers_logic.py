import ast
import re


# Add missing import_addition_or_removal function for CLI compatibility
def import_addition_or_removal(before, after):
    """
    Returns True if there is an addition or removal of import statements between before and after code.
    """

    def get_imports(src):
        lines = src.splitlines()
        return set(line.strip() for line in lines if re.match(r"^(import |from )", line.strip()))

    before_imports = get_imports(before)
    after_imports = get_imports(after)
    return before_imports != after_imports


def _remove_unreachable_code(src):
    """
    Removes unreachable code blocks (e.g., if False) from the source code string using AST transformation.
    Returns the modified source code as a string.
    """
    try:
        tree = ast.parse(src)
    except Exception:
        return src

    class DeadCodeRemover(ast.NodeTransformer):
        def visit_If(self, node):
            if (isinstance(node.test, ast.Constant) and node.test.value is False) or (
                isinstance(node.test, ast.NameConstant) and node.test.value is False
            ):
                node.body = []
            return self.generic_visit(node)

    tree = DeadCodeRemover().visit(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return src


def logic_change_ignoring_unreachable(before, after):
    """
    Returns True if there is a real logic change, ignoring changes inside unreachable code (e.g., if False blocks).
    """
    """
    Returns True if there is a real logic change, ignoring changes inside unreachable code (e.g., if False blocks).
    """
    before_no_dead = _remove_unreachable_code(before)
    after_no_dead = _remove_unreachable_code(after)
    return before_no_dead.strip() != after_no_dead.strip()


def variable_name_change_in_used_code(before, after):
    """
    Returns True if variable names have changed in used (reachable) code between before and after.
    Ignores unreachable code.
    """
    before = _remove_unreachable_code(before)
    after = _remove_unreachable_code(after)
    try:
        before_ast = ast.parse(before)
        after_ast = ast.parse(after)
    except Exception:
        return False

    def get_names(tree):
        names = set()

        class NameVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                names.add(node.id)

        NameVisitor().visit(tree)
        return names

    return get_names(before_ast) != get_names(after_ast)


def decorator_change(before, after):
    before = _remove_unreachable_code(before)
    after = _remove_unreachable_code(after)
    try:
        before_ast = ast.parse(before)
        after_ast = ast.parse(after)
    except Exception:
        return False

    def get_decorators(tree):
        decorators = set()

        class DecoratorVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                for d in node.decorator_list:
                    decorators.add(ast.dump(d))

        DecoratorVisitor().visit(tree)
        return decorators

    return get_decorators(before_ast) != get_decorators(after_ast)


def uncommented_code_detected(before, after):
    before = _remove_unreachable_code(before)
    after = _remove_unreachable_code(after)
    before_lines = before.splitlines()
    after_lines = set(line.strip() for line in after.splitlines() if line.strip() and not line.strip().startswith("#"))
    for _ in before_lines:
        if _.strip().startswith("#"):
            uncommented = _.lstrip("#").strip()
            if uncommented and uncommented in after_lines:
                return True
    return False


def get_code_literals(src):
    src = _remove_unreachable_code(src)
    try:
        tree = ast.parse(src)
    except Exception:
        return set()
    literals = set()
    meta_names = {"__version__", "__author__", "__doc__"}

    class LiteralVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.targets[0], ast.Name) and node.targets[0].id in meta_names:
                return
            self.generic_visit(node)

        def visit_Expr(self, node):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return
            self.generic_visit(node)

        def visit_Constant(self, node):
            literals.add(repr(node.value))

        def visit_Str(self, node):
            literals.add(repr(node.s))

        def visit_Num(self, node):
            literals.add(repr(node.n))

        def visit_NameConstant(self, node):
            literals.add(repr(node.value))

    LiteralVisitor().visit(tree)
    return literals
