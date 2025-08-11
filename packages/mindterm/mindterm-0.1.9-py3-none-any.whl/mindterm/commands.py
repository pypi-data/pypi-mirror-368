"""Command handling for Mind Terminal."""
from collections.abc import Callable
from typing import Any


class CommandHandler:
    """Handles commands for Mind Terminal."""

    def __init__(self) -> None:
        """Initialize command handler."""
        self.commands: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]) -> None:
        """Register a command."""
        self.commands[name] = func

    def execute(self, command: str, *args: Any, **kwargs: Any) -> bool:
        """Execute a command. Returns True if the command was handled."""
        if command in self.commands:
            self.commands[command](*args, **kwargs)
            return True
        return False

    def get_commands(self) -> dict[str, Callable[..., Any]]:
        """Get all registered commands."""
        return self.commands
