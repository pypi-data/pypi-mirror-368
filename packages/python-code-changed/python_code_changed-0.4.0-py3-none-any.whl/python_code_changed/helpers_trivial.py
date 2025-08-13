import re


def only_comments_changed(before: str, after: str) -> bool:
    """
    Returns True if only comments have changed between before and after code.
    """

    def strip_comments(line):
        return line.split("#", 1)[0].rstrip()

    def normalize(src):
        return "\n".join(strip_comments(line) for line in src.splitlines() if strip_comments(line).strip())

    return normalize(before).strip() == normalize(after).strip()


def only_imports_reordered(before: str, after: str) -> bool:
    """
    Returns True if only the order of import statements has changed between before and after code.
    Ignores comments and whitespace.
    """

    def get_imports(src):
        lines = src.splitlines()
        imports = [line.strip() for line in lines if re.match(r"^(import |from )", line.strip())]
        return imports

    def get_non_import_code(src):
        lines = src.splitlines()
        return "\n".join(
            [
                line
                for line in lines
                if not re.match(r"^(import |from )", line.strip()) and not line.strip().startswith("#") and line.strip()
            ]
        )

    before_imports = get_imports(before)
    after_imports = get_imports(after)
    if set(before_imports) == set(after_imports):
        if get_non_import_code(before).strip() == get_non_import_code(after).strip():
            return before_imports != after_imports
    return False


def only_function_order_changed(before, after):
    """
    Returns True if only the order of function definitions has changed between before and after code.
    Ignores comments and whitespace.
    """

    def get_functions(src):
        lines = src.splitlines()
        functions = []
        func_block = []
        in_func = False
        for line in lines:
            if line.strip().startswith("def "):
                if func_block:
                    functions.append("\n".join(func_block))
                    func_block = []
                in_func = True
            if in_func:
                func_block.append(line)
            if line.strip() == "" and in_func:
                in_func = False
        if func_block:
            functions.append("\n".join(func_block))
        return set(functions)

    return get_functions(before) == get_functions(after) and before != after


def only_docstring_changed(before, after):
    def remove_docstrings(src):
        src = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
        src = re.sub(r"'''(.*?)'''", "", src, flags=re.DOTALL)
        return src

    return remove_docstrings(before).strip() == remove_docstrings(after).strip() and before != after


def only_meta_vars_changed(before, after):
    meta = ("__version__", "__author__", "__doc__")

    def remove_meta_vars(src):
        lines = src.splitlines()
        return "\n".join([line for line in lines if not re.match(rf"^({'|'.join(meta)})\s*=.*", line.strip())])

    return remove_meta_vars(before).strip() == remove_meta_vars(after).strip() and before != after


def is_minor_deletion(before: str, after: str) -> bool:
    before_lines = [
        line.strip() for line in before.strip().splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    after_lines = [
        line.strip() for line in after.strip().splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    return before_lines == after_lines
