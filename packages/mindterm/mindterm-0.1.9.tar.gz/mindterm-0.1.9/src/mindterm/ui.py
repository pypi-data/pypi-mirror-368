"""UI components for Mind Terminal."""
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


class TerminalUI:
    """Terminal UI for Mind Terminal."""

    def __init__(self) -> None:
        """Initialize the terminal UI."""
        self.completer = WordCompleter(["\\chat", "\\bye"], ignore_case=True)
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

    def get_user_input(self) -> str:
        """Get input from the user."""
        return str(self.session.prompt("> "))

    def display_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print(Panel("Goodbye!", style="bold blue"))
