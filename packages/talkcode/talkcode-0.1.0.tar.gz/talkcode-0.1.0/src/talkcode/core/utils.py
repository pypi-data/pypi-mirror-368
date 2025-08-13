from pathlib import Path

def find_python_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]
