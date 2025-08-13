# src/talkcode/analyzer/parser.py

import ast
from pathlib import Path

class CodeParser:
    def __init__(self, path: Path):
        self.path = path
        self.source = path.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)
        self.functions = []
        self.classes = []
        self.imports = []

    def analyze(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno
                end = getattr(node, 'end_lineno', start)
                body = "\n".join(self.source.splitlines()[start - 1:end])
                docstring = ast.get_docstring(node) or ""
                decorators = [
                    d.id if isinstance(d, ast.Name) else ast.unparse(d)
                    for d in node.decorator_list
                ]
                self.functions.append({
                    "name": node.name,
                    "line": start,
                    "body": body,
                    "docstring": docstring,
                    "decorators": decorators
                })

            elif isinstance(node, ast.ClassDef):
                start = node.lineno
                end = getattr(node, 'end_lineno', start)
                body = "\n".join(self.source.splitlines()[start - 1:end])
                docstring = ast.get_docstring(node) or ""
                decorators = [
                    d.id if isinstance(d, ast.Name) else ast.unparse(d)
                    for d in node.decorator_list
                ]
                self.classes.append({
                    "name": node.name,
                    "line": start,
                    "body": body,
                    "docstring": docstring,
                    "decorators": decorators
                })

            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self.imports.append({
                    "type": type(node).__name__,
                    "line": node.lineno
                })

    def summary(self):
        return {
            "file": str(self.path),
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports
        }
