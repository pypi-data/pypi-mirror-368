"""The main entry point for the Rock-Paper-Scissors game application.

This module is responsible for the user-facing interactions, including:
- Setting up the player's name and score.
- Establishing the game rules (default or custom).
- Running the main interactive game loop.
"""

from __future__ import annotations

import logging
import random

from .file_handler import DEFAULT_RATING_FILE, get_user_score
from .game_logic import GameRules, create_rules_from_input

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def handle_game_turn(user_input: str, current_score: int, rules: GameRules) -> int:
    """Handles a single user move, compares it, and updates the score.

    Args:
        user_input: The move entered by the user (e.g., "rock").
        current_score: The user's current score.
        rules: The rules for the current game.

    Returns:
        The updated score after the turn.
    """
    computer_choice = random.choice(rules.options)  # noqa: S311
    result = rules.compare(user_input, computer_choice)

    match result:
        case 1:
            print(f"Well done. The computer chose {computer_choice} and failed")
            return current_score + 100
        case 0:
            print(f"There is a draw ({user_input})")
            return current_score + 50
        case -1:
            print(f"Sorry, but the computer chose {computer_choice}")
            return current_score
    return current_score  # Should be unreachable, but good for type safety


def game_loop(initial_score: int, rules: GameRules) -> None:
    """Runs the main interactive game loop.

    Args:
        initial_score: The player's starting score.
        rules: The rules for the current game.
    """
    score = initial_score
    while True:
        user_input = input().strip().lower()
        if user_input == "!exit":
            break
        if user_input == "!rating":
            print(f"Your rating: {score}")
        elif user_input in rules.options:
            score = handle_game_turn(user_input, score, rules)
        else:
            print("Invalid input")

    print("Bye!")


def setup_player_and_score() -> tuple[str, int]:
    """Gets the player's name and loads their score from the rating file.

    Returns:
        A tuple containing the player's name and their initial score.
    """
    user_name = input("Enter your name: ").strip()
    print(f"Hello, {user_name}")

    try:
        return user_name, get_user_score(user_name, file_path=DEFAULT_RATING_FILE)
    except FileNotFoundError:
        logging.info(f"{DEFAULT_RATING_FILE} not found. Starting with a score of 0.")
    except ValueError as e:
        logging.warning(f"Could not retrieve score for {user_name}: {e}. Starting with 0.")
    return user_name, 0


def setup_rules() -> GameRules:
    """Prompts the user for custom game rules or uses the default."""
    options_str = input(
        "Enter game options (e.g., rock,paper,scissors) or leave empty for default:\n"
    )
    return create_rules_from_input(options_str)


def main() -> None:
    """Sets up the game and runs the main loop."""
    user_name, initial_score = setup_player_and_score()
    rules = setup_rules()

    print("Okay, let's start")
    game_loop(initial_score, rules)


if __name__ == "__main__":
    main()
