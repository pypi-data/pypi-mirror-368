from src.talkcode.analyzer.embeddings import ChunkEmbedder
from pathlib import Path

def test_chunk_search():
    ce = ChunkEmbedder(Path("examples/legacy_app"))
    ce.chunk_code()
    results = ce.search("import")
    assert isinstance(results, list)
