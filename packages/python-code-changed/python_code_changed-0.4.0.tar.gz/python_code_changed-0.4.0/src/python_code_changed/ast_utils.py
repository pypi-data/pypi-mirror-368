import ast
import copy


def normalize_ast(node):
    """
    Recursively normalizes an AST node by removing location info, sorting imports and functions,
    and replacing docstrings with pass statements. Returns a deep copy of the node.
    """
    if not isinstance(node, ast.AST):
        return node
    node = copy.deepcopy(node)
    for field in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
        if hasattr(node, field):
            try:
                setattr(node, field, None)
            except Exception:
                pass
    for child_name, child_value in ast.iter_fields(node):
        if isinstance(child_value, list):
            setattr(node, child_name, [normalize_ast(n) for n in child_value])
        elif isinstance(child_value, ast.AST):
            setattr(node, child_name, normalize_ast(child_value))
    if hasattr(node, "body") and isinstance(node.body, list) and node.body:
        doc_expr = node.body[0]
        if isinstance(doc_expr, ast.Expr):
            val = getattr(doc_expr, "value", None)
            if (isinstance(val, ast.Str)) or (isinstance(val, ast.Constant) and isinstance(val.value, str)):
                node.body[0] = ast.Pass()
        node.body = [normalize_ast(child) for child in node.body]
        imports = []
        functions = []
        others = []
        for stmt in node.body:
            if isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom):
                imports.append(stmt)
            elif isinstance(stmt, ast.FunctionDef):
                functions.append(stmt)
            else:
                others.append(stmt)
        imports_sorted = sorted(
            imports, key=lambda x: getattr(x, "module", None) or (x.names[0].name if x.names else "")
        )
        functions_sorted = sorted(functions, key=lambda x: x.name)
        node.body = imports_sorted + functions_sorted + others
    return node


def remove_dead_code(src):
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
            # Remove entire 'if False:' block
            if (isinstance(node.test, ast.Constant) and node.test.value is False) or (
                isinstance(node.test, ast.NameConstant) and node.test.value is False
            ):
                return None
            # Recursively process children
            node.body = [self.visit(stmt) for stmt in node.body if self.visit(stmt) is not None]
            node.orelse = [self.visit(stmt) for stmt in node.orelse if self.visit(stmt) is not None]
            return node

        def visit_FunctionDef(self, node):
            node.body = [self.visit(stmt) for stmt in node.body if self.visit(stmt) is not None]
            return node

        def visit_ClassDef(self, node):
            node.body = [self.visit(stmt) for stmt in node.body if self.visit(stmt) is not None]
            return node

        def visit_Module(self, node):
            node.body = [self.visit(stmt) for stmt in node.body if self.visit(stmt) is not None]
            return node

    tree = DeadCodeRemover().visit(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return src
