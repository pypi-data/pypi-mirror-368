# src/talkcode/analyzer/embeddings.py

import hashlib
from pathlib import Path
from talkcode.core.utils import find_python_files
from talkcode.core.cache import load_embeddings, save_embeddings


class ChunkEmbedder:
    def __init__(self, root: Path):
        self.root = root
        self.chunks = load_embeddings() or []

    def chunk_code(self, lines_per_chunk: int = 20):
        if self.chunks:  # already loaded from cache
            return
        files = find_python_files(self.root)
        for f in files:
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
                for i in range(0, len(lines), lines_per_chunk):
                    chunk = "\n".join(lines[i:i + lines_per_chunk]).strip()
                    if chunk:
                        self.chunks.append({
                            "file": str(f),
                            "start": i + 1,
                            "text": chunk,
                            "hash": hashlib.md5(chunk.encode()).hexdigest()
                        })
            except Exception as e:
                print(f"Error chunking {f}: {e}")
        save_embeddings(self.chunks)
        
    def search(self, keyword: str):
        keyword = keyword.lower()
        results = []
        for c in self.chunks:
            if keyword in c["text"].lower():
                results.append((c["file"], c["start"], c["text"]))
        return results
