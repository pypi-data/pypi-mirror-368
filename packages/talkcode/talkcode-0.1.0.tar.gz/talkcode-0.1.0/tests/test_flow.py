from src.talkcode.analyzer.flow import CallGraphBuilder
from pathlib import Path

def test_trace_function():
    cg = CallGraphBuilder(Path("examples/legacy_app"))
    cg.build()
    path = cg.trace("examples")
    assert isinstance(path, list)
