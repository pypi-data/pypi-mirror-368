import ast
from pathlib import Path

def parse_decorators(path: Path):
    """
    Return decorators in path like
    [
        {"name": "say_hello", "title": "Say Hello"},
        ...
    ]
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    commands = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for deco in node.decorator_list:
                if not isinstance(deco, ast.Call):
                    continue

                func = deco.func
                is_ext_command = False
                if isinstance(func, ast.Attribute):
                    if func.attr == "command":
                        is_ext_command = True
                elif isinstance(func, ast.Name):
                    if func.id == "command":
                        is_ext_command = True

                if not is_ext_command:
                    continue

                cmd_name = None
                title = None

                if deco.args:
                    first = deco.args[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        cmd_name = first.value
                    if len(deco.args) > 1:
                        second = deco.args[1]
                        if isinstance(second, ast.Constant) and isinstance(second.value, str):
                            title = second.value

                for kw in deco.keywords:
                    if kw.arg == "title":
                        if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            title = kw.value.value

                if cmd_name:
                    commands.append({
                        "name": cmd_name,
                        "title": title or cmd_name.replace("_", " ").title(),
                        "handler": node.name
                    })

    return commands