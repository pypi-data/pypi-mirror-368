import ast


def parse_function_definitions(python_file):
    with open(python_file, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)
    function_definitions = [
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    fun_array = []
    for func_def in function_definitions:
        func_define = {
            "name": func_def.name,
            "arguments": list(arg.arg for arg in func_def.args.args),
        }
        fun_array.append(func_define)
    return fun_array
