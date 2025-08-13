# src/talkcode/main.py

import typer
from talkcode.core.config import init_config, load_config
from talkcode.chat.cli import start_chat
from talkcode.ui.app import launch_ui
from talkcode.analyzer.indexer import CodeIndex
from pathlib import Path
import json

app = typer.Typer()

@app.command()
def init():
    """Initialize talkcode configuration."""
    init_config()

@app.command()
def chat(
    ai: bool = False,
    path: str = typer.Option(".", help="Path to the indexed codebase")
):
    """Start talkcode in chat mode."""
    resolved_path = Path(path).resolve()
    index_path = Path.home() / ".talkcode" / "index.json"

    if not index_path.exists():
        print("No index found. Please run 'talkcode index --path <your_path>' first.")
        raise typer.Exit()

    index_data = json.loads(index_path.read_text())
    config = load_config()
    config["ai_enabled"] = ai
    config["index"] = index_data
    config["codebase_path"] = str(resolved_path)

    start_chat(config)


@app.command()
def ui(
    ai: bool = False,
    path: str = typer.Option(".", help="Path to the indexed codebase")
):
    """Launch talkcode in UI mode."""
    resolved_path = Path(path).resolve()
    index_path = Path.home() / ".talkcode" / "index.json"

    if not index_path.exists():
        print("No index found. Please run 'talkcode index --path <your_path>' first.")
        raise typer.Exit()

    index_data = json.loads(index_path.read_text())
    config = load_config()
    config["ai_enabled"] = ai
    config["index"] = index_data
    config["codebase_path"] = str(resolved_path)

    launch_ui(config)


@app.command()
def index(path: str = typer.Option(".", help="Path to the codebase to index")):
    """Index a Python codebase."""
   
    resolved_path = Path(path).resolve()
    index = CodeIndex(resolved_path)
    index.build()

    index_path = Path.home() / ".talkcode" / "index.json"
    index_path.parent.mkdir(exist_ok=True)
    index_path.write_text(json.dumps(index.index, indent=2))

    print(f"Indexed {len(index.index)} files from {path}")

if __name__ == "__main__":
    app()
