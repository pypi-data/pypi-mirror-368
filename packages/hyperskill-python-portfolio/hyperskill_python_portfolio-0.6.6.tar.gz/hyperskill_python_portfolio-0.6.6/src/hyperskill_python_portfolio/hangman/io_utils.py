"""Provides utility functions for handling user input."""

from __future__ import annotations

from .models import MenuOption


def get_menu_command() -> MenuOption:
    """Gets a valid menu command from the user."""
    command_map = {opt.value: opt for opt in MenuOption}

    while True:
        prompt = (
            'Type "play" to play the game, "results" to show the scoreboard, and "exit" to quit:'
        )
        raw_input = input(prompt).lower()
        command = command_map.get(raw_input)
        if command:
            return command

        print("Invalid command. Please, try again.")


def get_letter_from_user() -> str | None:
    """Gets a valid single lowercase letter from the user."""
    char = input("Input a letter: ")
    if len(char) != 1:
        print("Please, input a single letter.")
        return None
    if not char.isascii() or not char.islower():
        print("Please, enter a lowercase letter from the English alphabet.")
        return None
    return char
