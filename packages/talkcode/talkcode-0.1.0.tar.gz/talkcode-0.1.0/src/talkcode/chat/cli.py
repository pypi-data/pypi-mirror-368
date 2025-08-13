# src/talkcode/chat/cli.py

from pathlib import Path
from prompt_toolkit import prompt
from rich import print
from talkcode.analyzer.indexer import CodeIndex
from talkcode.analyzer.flow import CallGraphBuilder
from talkcode.analyzer.embeddings import ChunkEmbedder
from talkcode.chat.ai import MultiProviderAI

def start_chat(config):
    ai_enabled = config.get("ai_enabled", False)
    ai_client = None
    if ai_enabled:
        try:
            ai_client = MultiProviderAI()
        except Exception as e:
            print(f"[red]AI disabled: {e}[/red]")

    path_index = Path.home() / ".talkcode" / "index.json"
    if not path_index.exists():
        print("[red]No index found. Run 'talkcode index' first.[/red]")
        return

    import json
    index_data = json.loads(path_index.read_text())
    index = CodeIndex(Path("."))
    index.index = index_data

    print("[bold cyan]talkcode chat started. Type 'exit' to quit.[/bold cyan]")
    while True:
        q = prompt(">> ").strip()
        if q.lower() in ("exit", "quit"):
            break

        if q.lower().startswith("function "):
            name = q.split("function", 1)[-1].strip()
            results = index.search_function(name)
            for file, fname, lineno in results:
                print(f"[yellow]{fname}[/yellow] in [blue]{file}[/blue] at line {lineno}")

        elif q.lower().startswith("class "):
            name = q.split("class", 1)[-1].strip()
            results = index.search_class(name)
            for file, cname, lineno in results:
                print(f"[magenta]{cname}[/magenta] in [blue]{file}[/blue] at line {lineno}")

        elif q.lower().startswith("decorator "):
            name = q.split("decorator", 1)[-1].strip()
            results = index.search_decorator(name)
            for file, symbol, lineno in results:
                print(f"[green]{symbol}[/green] with @{name} in [blue]{file}[/blue] at line {lineno}")

        elif q.lower().startswith("flow "):
            target = q.split("flow", 1)[-1].strip()
            cg = CallGraphBuilder(Path("."))
            cg.build()
            path = cg.trace(target)
            print(f"[bold]Call flow for {target}:[/bold]")
            for f in path:
                print(f" - {f}")

        elif q.lower().startswith("search "):
            keyword = q.split("search", 1)[-1].strip()
            ce = ChunkEmbedder(Path("."))
            ce.chunk_code()
            results = ce.search(keyword)
            for file, start, text in results[:3]:
                print(f"[blue]{file}[/blue] line {start}:\n{text}\n")

        else:
            if ai_client:
                context = "\n".join(
                    f"{entry['file']}:\n"
                    + "\n".join(
                        f"Function {f['name']} (line {f['line']}):\n"
                        + (f"Docstring: {f['docstring']}\n" if f.get("docstring") else "")
                        + (f"Decorators: {', '.join(f['decorators'])}\n" if f.get("decorators") else "")
                        + f"{f['body']}\n"
                        for f in entry.get("functions", [])
                    )
                    + "\n"
                    + "\n".join(
                        f"Class {c['name']} (line {c['line']}):\n"
                        + (f"Docstring: {c['docstring']}\n" if c.get("docstring") else "")
                        + (f"Decorators: {', '.join(c['decorators'])}\n" if c.get("decorators") else "")
                        + f"{c['body']}\n"
                        for c in entry.get("classes", [])
                    )
                    for entry in index.index
                )
                try:
                    answer = ai_client.ask(q, context=context)
                    print(f"[green]{answer}[/green]")
                except Exception as e:
                    print(f"[red]AI error: {e}[/red]")
            else:
                print("[italic]AI is disabled or not initialized.[/italic]")
