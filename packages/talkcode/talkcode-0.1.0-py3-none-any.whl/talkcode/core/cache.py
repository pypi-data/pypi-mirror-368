import json
import pickle
from pathlib import Path

CACHE_DIR = Path(".talkcode_cache")
CACHE_DIR.mkdir(exist_ok=True)

def save_index(index_data, name="index.json"):
    with open(CACHE_DIR / name, "w") as f:
        json.dump(index_data, f)

def load_index(name="index.json"):
    path = CACHE_DIR / name
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None

def save_embeddings(embeddings, name="embeddings.pkl"):
    with open(CACHE_DIR / name, "wb") as f:
        pickle.dump(embeddings, f)

def load_embeddings(name="embeddings.pkl"):
    path = CACHE_DIR / name
    if path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    return None
