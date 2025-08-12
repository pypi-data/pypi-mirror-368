"""A simple command-line zoo habitat viewer."""

from __future__ import annotations

from .art import ALL_ART

GREETING = f"Please enter the number of the habitat (0-{len(ALL_ART) - 1}) you would like to view:"
FAREWELL = "See you later!"
ERROR_MESSAGE = "\nInvalid habitat number. Please try again.\n"
EXIT_COMMAND = "exit"


def main() -> None:
    """Runs the main interactive loop for the habitat viewer."""
    habitats = {str(i): animal for i, animal in enumerate(ALL_ART)}

    while (channel := input(GREETING)) != EXIT_COMMAND:
        print(habitats.get(channel, ERROR_MESSAGE))

    print(FAREWELL)


if __name__ == "__main__":
    main()
