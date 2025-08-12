"""This module contains the main Game class that orchestrates the application."""

from __future__ import annotations

import random
from typing import Final

from .io_utils import get_letter_from_user, get_menu_command
from .models import GameStatistics, HangmanSession, MenuOption, Status


class Game:
    """Manages the application flow, game state, and user statistics."""

    WORD_BANK: Final[tuple[str, ...]] = ("python", "java", "swift", "javascript")
    MAX_ATTEMPTS: Final[int] = 8

    def __init__(self) -> None:
        """Initializes the game with a new set of statistics."""
        self.statistics = GameStatistics()

    def run(self) -> None:
        """Starts the main game loop and handles menu navigation."""
        print("H A N G M A N")
        while True:
            match get_menu_command():
                case MenuOption.EXIT:
                    break
                case MenuOption.PLAY:
                    self._play_one_game()
                case MenuOption.RESULTS:
                    self._show_results()

    def _play_one_game(self) -> None:
        """Manages the logic for a single round of Hangman."""
        random_word = random.choice(self.WORD_BANK)  # noqa: S311
        session = HangmanSession(random_word)
        remaining_attempts = self.MAX_ATTEMPTS

        while remaining_attempts > 0 and not session.is_word_solved():
            print()
            print(session.get_current_progress())

            letter = get_letter_from_user()
            if not letter:
                continue

            status = session.make_guess(letter)

            if status == Status.MISS:
                print(status.value)
                remaining_attempts -= 1
            elif status == Status.SAME:
                print(status.value)

        print()
        if session.is_word_solved():
            print(session.word)  # The word is fully revealed
            print(f"You guessed the word {session.word}!")
            print("You survived!")
            self.statistics.wins += 1
        else:
            print("You lost!")
            self.statistics.losses += 1

    def _show_results(self) -> None:
        """Prints the current game statistics."""
        print(f"You won: {self.statistics.wins} times.")
        print(f"You lost: {self.statistics.losses} times.")
