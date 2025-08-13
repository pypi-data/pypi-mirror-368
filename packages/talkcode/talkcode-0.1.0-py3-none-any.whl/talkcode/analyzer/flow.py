# src/talkcode/analyzer/flow.py

import ast
from pathlib import Path
from talkcode.core.utils import find_python_files

class CallGraphBuilder:
    def __init__(self, root: Path):
        self.root = root
        self.graph = {}

    def build(self):
        files = find_python_files(self.root)
        for f in files:
            try:
                source = f.read_text(encoding="utf-8")
                tree = ast.parse(source)
                current_func = None

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        current_func = node.name
                        self.graph.setdefault(current_func, [])

                    elif isinstance(node, ast.Call):
                        callee = self._get_callee_name(node)
                        if current_func and callee:
                            self.graph[current_func].append(callee)

            except Exception as e:
                print(f"Error building flow for {f}: {e}")

    def _get_callee_name(self, node):
        # Handles calls like func(), obj.method(), decorator()
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

    def trace(self, func_name: str):
        visited = set()
        path = []

        def dfs(f):
            if f in visited:
                return
            visited.add(f)
            path.append(f)
            for callee in self.graph.get(f, []):
                dfs(callee)

        dfs(func_name)
        return path
