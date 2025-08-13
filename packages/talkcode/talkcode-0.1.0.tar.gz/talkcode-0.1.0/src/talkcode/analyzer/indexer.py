from pathlib import Path
from talkcode.core.utils import find_python_files
import ast
from talkcode.core.cache import load_index, save_index


# src/talkcode/analyzer/indexer.py

from pathlib import Path
from talkcode.core.utils import find_python_files
from talkcode.analyzer.parser import CodeParser

class CodeIndex:
    def __init__(self, root: Path):
        self.root = root
        self.index = load_index() or []

    def build(self):
        if self.index:  # already loaded from cache
            return
        
        files = find_python_files(self.root)
        for f in files:
            try:
                parser = CodeParser(f)
                parser.analyze()
                self.index.append(parser.summary())
            except Exception as e:
                print(f"Error indexing {f}: {e}")
        save_index(self.index)

    def search_function(self, name: str):
        results = []
        for entry in self.index:
            for f in entry.get("functions", []):
                if name.lower() in f["name"].lower():
                    results.append((entry["file"], f["name"], f["line"]))
        return results

    def search_class(self, name: str):
        results = []
        for entry in self.index:
            for c in entry.get("classes", []):
                if name.lower() in c["name"].lower():
                    results.append((entry["file"], c["name"], c["line"]))
        return results

    def search_imports(self, keyword: str):
        results = []
        for entry in self.index:
            for imp in entry.get("imports", []):
                if keyword.lower() in imp["type"].lower():
                    results.append((entry["file"], imp["type"], imp["line"]))
        return results

    def search_decorator(self, decorator_name: str):
        results = []
        for entry in self.index:
            for f in entry.get("functions", []):
                if decorator_name in f.get("decorators", []):
                    results.append((entry["file"], f["name"], f["line"]))
            for c in entry.get("classes", []):
                if decorator_name in c.get("decorators", []):
                    results.append((entry["file"], c["name"], c["line"]))
        return results

def extract_definitions(file_path: Path):
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = getattr(node, 'end_lineno', start)
            body = "\n".join(source.splitlines()[start - 1:end])
            functions.append({
                "name": node.name,
                "line": start,
                "body": body,
                "docstring": ast.get_docstring(node),
                "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
            })


        elif isinstance(node, ast.ClassDef):
            start = node.lineno
            end = getattr(node, 'end_lineno', start)
            body = "\n".join(source.splitlines()[start - 1:end])
            classes.append({
                "name": node.name,
                "line": start,
                "body": body,
                "docstring": ast.get_docstring(node),
                "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
            })
          
    return functions, classes
