# src/talkcode/analyzer/chunk_search.py

from talkcode.analyzer.embeddings import ChunkEmbedder
from pathlib import Path

class ChunkSearcher:
    def __init__(self, root: Path):
        self.root = root
        self.embedder = ChunkEmbedder(root)
        self.embedder.chunk_code()

    def search(self, query: str, top_k: int = 5):
        results = self.embedder.search(query)
        return results[:top_k]
