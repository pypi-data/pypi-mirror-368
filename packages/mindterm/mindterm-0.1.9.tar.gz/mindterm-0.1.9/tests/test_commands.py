"""Tests for the commands module."""
from mindterm.commands import CommandHandler


def test_command_registration() -> None:
    """Test command registration."""
    handler = CommandHandler()

    def test_command() -> None:
        pass

    handler.register("test", test_command)
    assert "test" in handler.get_commands()


def test_command_execution() -> None:
    """Test command execution."""
    handler = CommandHandler()
    executed = []

    def test_command() -> None:
        executed.append(True)

    handler.register("test", test_command)
    result = handler.execute("test")
    assert result is True
    assert len(executed) == 1

    # Test non-existent command
    result = handler.execute("nonexistent")
    assert result is False
