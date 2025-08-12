"""Main entry point for the chatbot application."""

from __future__ import annotations

from .bot import ChatBot


def main() -> None:
    """Initializes and runs the chatbot."""
    # Create an instance of the bot with its configuration
    simple_bot = ChatBot(bot_name="Aid", birth_year=2020)
    # Start the conversation
    simple_bot.run()


if __name__ == "__main__":
    main()
