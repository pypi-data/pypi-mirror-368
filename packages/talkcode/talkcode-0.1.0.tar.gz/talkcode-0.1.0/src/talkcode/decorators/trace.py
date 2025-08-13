# src/talkcode/analyzer/decorator_trace.py

from talkcode.analyzer.indexer import CodeIndex
from talkcode.analyzer.flow import CallGraphBuilder
from pathlib import Path

class DecoratorTracer:
    def __init__(self, root: Path):
        self.root = root
        self.index = CodeIndex(root)
        self.index.index_codebase()
        self.call_graph = CallGraphBuilder(root)
        self.call_graph.build()

    def find_decorated(self, decorator_name: str):
        results = []
        for entry in self.index.index:
            for func in entry.get("functions", []):
                if decorator_name in func.get("decorators", []):
                    results.append((entry["file"], func["name"], func["line"]))
            for cls in entry.get("classes", []):
                if decorator_name in cls.get("decorators", []):
                    results.append((entry["file"], cls["name"], cls["line"]))
        return results

    def trace_usage(self, decorator_name: str):
        decorated = self.find_decorated(decorator_name)
        usage = {}
        for file, name, line in decorated:
            trace = self.call_graph.trace(name)
            usage[name] = {
                "file": file,
                "line": line,
                "calls": trace
            }
        return usage
