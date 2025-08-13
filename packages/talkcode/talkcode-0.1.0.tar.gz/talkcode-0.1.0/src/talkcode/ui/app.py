# src/talkcode/ui/app.py

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, LoadingIndicator
from textual.widgets import Log as TextLog
from textual.reactive import reactive
from textual.css.errors import StylesheetError

from talkcode.analyzer.indexer import CodeIndex
from talkcode.analyzer.flow import CallGraphBuilder
from talkcode.chat.ai import MultiProviderAI
from talkcode.chat.prompts import format_user_prompt


class TalkCodeUI(App):
    CSS_PATH = str(Path(__file__).parent / "styles.css")

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "show_help", "Help"),
        ("r", "refresh", "Refresh Index"),
    ]

    index = reactive[CodeIndex | None](None)
    ai_enabled = reactive(False)

    def __init__(self, config: dict):
        super().__init__()
        self.ai_enabled = config.get("ai_enabled", False)
        self.index_data = config.get("index", [])
        self.loading: LoadingIndicator | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static("Call Flow", classes="title"),
                Input(placeholder="Enter function name...", id="flow_input"),
                TextLog(id="flow_log", highlight=True),
            ),
            Vertical(
                Static("Ask a Question", classes="title"),
                Input(placeholder="Type your question here...", id="question_input"),
                TextLog(id="answer_log", highlight=True),
            )
        )
        yield LoadingIndicator(id="loading", classes="spinner")
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.stylesheet.read(self.CSS_PATH)
        except StylesheetError as e:
            print(f"Warning: Could not load stylesheet: {e}")

        self.index = CodeIndex(Path("."))
        self.index.index = self.index_data

        self.loading = self.query_one("#loading", LoadingIndicator)
        self.loading.display = False

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "question_input":
            self.handle_question(event.value.strip())
        elif event.input.id == "flow_input":
            self.handle_flow(event.value.strip())

    def handle_question(self, question: str) -> None:
        answer_log = self.query_one("#answer_log", TextLog)

        if not question:
            return

        answer_log.write(f"[bold cyan]>> {question}[/bold cyan]")

        if question.lower() == "help":
            self.action_show_help()
            return

        if self.ai_enabled:
            if self.loading:
                self.loading.display = True
            self.call_later(self._ask_ai, question, answer_log)
        else:
            answer_log.write("[italic]AI is disabled. Enable with '--ai' flag.[/italic]")

    def _ask_ai(self, question: str, answer_log: TextLog) -> None:
        try:
            ai = MultiProviderAI()
            context = "\n".join(
                f"{entry['file']}:\n" +
                "\n".join(
                    f"Function {f['name']} (line {f['line']}):\n{f['body']}\n"
                    for f in entry.get("functions", [])
                )
                for entry in self.index.index
            )
            prompt = format_user_prompt(question, context)
            response = ai.ask(prompt)
            answer_log.write(f"[green]{response}[/green]")
        except Exception as e:
            answer_log.write(f"[red]AI error: {e}[/red]")
        finally:
            if self.loading:
                self.loading.display = False

    def handle_flow(self, function_name: str) -> None:
        flow_log = self.query_one("#flow_log", TextLog)

        flow_log.clear()
        if not function_name:
            flow_log.write("[italic]Please enter a function name.[/italic]")
            return

        if self.loading:
            self.loading.display = True

        self.call_later(self._generate_flow, function_name, flow_log)

    def _generate_flow(self, function_name: str, flow_log: TextLog) -> None:
        try:
            flow_log.write(f"[yellow]Generating call flow for '{function_name}'...[/yellow]")
            cg = CallGraphBuilder(Path("."))
            cg.build()
            path = cg.trace(function_name)
            flow_log.write(f"[bold]Call flow for {function_name}:[/bold]")
            for f in path:
                flow_log.write(f" - {f}")
        except Exception as e:
            flow_log.write(f"[red]Error generating flow: {e}[/red]")
        finally:
            if self.loading:
                self.loading.display = False

    def action_show_help(self) -> None:
        answer_log = self.query_one("#answer_log", TextLog)
        answer_log.clear()
        answer_log.write("[bold]Available Commands:[/bold]")
        answer_log.write("• [cyan]flow_input[/cyan] — Type a function name to trace its call flow")
        answer_log.write("• [cyan]question_input[/cyan] — Ask AI about the codebase (if enabled)")

    def action_refresh(self) -> None:
        if self.index:
            self.index.index_codebase()


def launch_ui(config: dict = None) -> None:
    config = config or {}
    TalkCodeUI(config).run()
