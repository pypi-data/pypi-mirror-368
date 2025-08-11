"""Main module for Mind Terminal."""
from loguru import logger

from mindterm.client import LLMClient
from mindterm.config import config
from mindterm.ui import TerminalUI


def run() -> None:
    """Run the Mind Terminal application."""
    # Validate configuration
    if not config.validate():
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return

    # Initialize components
    try:
        client = LLMClient()
    except ValueError as e:
        print(f"Error initializing client: {e}")
        return

    ui = TerminalUI()
    ui.display_welcome()
    logger.info("Mind Terminal started!")

    # Main loop
    while True:
        try:
            text = ui.get_user_input()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            # Handle built-in commands
            if text == "\\bye":
                break
            elif text == "\\help":
                print("Available commands: \\chat, \\bye, \\help")
                continue

            # Get and display response
            response = client.get_completion(text)
            ui.display_response(response)

    ui.display_goodbye()


def main() -> None:
    """Main entry point."""
    run()


if __name__ == "__main__":
    main()
