from src.talkcode.analyzer.indexer import CodeIndex
from pathlib import Path

def test_index_build():
    index = CodeIndex(Path("examples/legacy_app"))
    index.build()
    assert len(index.index) > 0

def test_search_function():
    index = CodeIndex(Path("examples/legacy_app"))
    index.build()
    results = index.search_function("examples")
    assert isinstance(results, list)
