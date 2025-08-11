"""UI components for Mind Terminal."""
from collections.abc import Generator

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel


class CommandCompleter(Completer):
    """Custom completer that only works at the beginning of the line."""

    def __init__(self) -> None:
        self.commands = ["\\chat", "\\bye"]

    def get_completions(
        self, document: Document, complete_event: object
    ) -> Generator[Completion, None, None]:
        """Generate completions only at the beginning of the line."""
        # Only provide completions at the beginning of the line
        if document.text.startswith("\\") and document.cursor_position == len(
            document.text
        ):
            for command in self.commands:
                if command.startswith(document.text):
                    yield Completion(command, start_position=-len(document.text))


class TerminalUI:
    """Terminal UI for Mind Terminal."""

    def __init__(self) -> None:
        """Initialize the terminal UI."""
        self.completer = CommandCompleter()
        self.session: PromptSession[str] = PromptSession(completer=self.completer)
        self.console = Console()

    def display_welcome(self) -> None:
        """Display welcome message."""
        self.console.print(Panel("Welcome to Mind Terminal!", style="bold blue"))

    def display_response(self, response: str | None) -> None:
        """Display the LLM response."""
        if response:
            self.console.print(
                Panel(Markdown(response), title="Assistant", style="green")
            )
        else:
            self.console.print(Panel("No response received.", style="red"))

    def display_streamed_response(
        self, content_generator: Generator[str, None, None]
    ) -> None:
        """Display streamed response from the LLM."""
        # Initialize with a waiting message
        markdown_text = ""
        with Live("", refresh_per_second=4) as live:
            try:
                for chunk in content_generator:
                    if chunk is not None:
                        markdown_text += chunk
                        # Update live display with rendered markdown in a panel
                        live.update(
                            Panel(
                                Markdown(markdown_text),
                                title="Assistant",
                                style="green",
                            )
                        )
                    else:
                        markdown_text += "\nError occurred during streaming."
                        live.update(
                            Panel(
                                Markdown(markdown_text), title="Assistant", style="red"
                            )
                        )
                        return
            except Exception as e:
                markdown_text += f"\nError displaying streamed response: {e}"
                live.update(
                    Panel(Markdown(markdown_text), title="Assistant", style="red")
                )

    def get_user_input(self) -> str:
        """Get input from the user."""
        # Only enable completer at the beginning of the line
        return str(self.session.prompt("> ", completer=self.completer))

    def display_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print(Panel("Goodbye!", style="bold blue"))
