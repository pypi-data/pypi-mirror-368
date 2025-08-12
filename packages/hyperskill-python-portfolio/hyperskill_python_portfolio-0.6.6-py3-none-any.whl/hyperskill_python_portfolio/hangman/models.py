"""Defines the core data models for the Hangman game."""

from __future__ import annotations

import dataclasses
import enum


class Status(enum.Enum):
    """Represents the outcome of a player's guess."""

    HIT = "You hit!"
    MISS = "That letter doesn't appear in the word."
    SAME = "You've already guessed this letter."


class MenuOption(enum.Enum):
    """Represents the main menu commands available to the player."""

    PLAY = "play"
    RESULTS = "results"
    EXIT = "exit"


@dataclasses.dataclass
class GameStatistics:
    """A simple data class to track wins and losses."""

    wins: int = 0
    losses: int = 0


@dataclasses.dataclass
class HangmanSession:
    """Represents the state of a single game session of Hangman."""

    word: str
    guesses: set[str] = dataclasses.field(default_factory=set)
    _unique_word_letters: frozenset[str] = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Cache the unique letters of the word for efficient checking."""
        self._unique_word_letters = frozenset(self.word)

    def make_guess(self, letter: str) -> Status:
        """Processes a single letter guess and updates the session state.

        Args:
            letter: The single character guessed by the user.

        Returns:
            The status of the guess (HIT, MISS, or SAME).
        """
        if letter in self.guesses:
            return Status.SAME
        self.guesses.add(letter)
        return Status.HIT if letter in self.word else Status.MISS

    def get_current_progress(self) -> str:
        """Returns a string representing the player's current progress.

        Example:
            For a word "python" with guesses {'p', 'o'}, returns "p-tho-".
        """
        return "".join(c if c in self.guesses else "-" for c in self.word)

    def is_word_solved(self) -> bool:
        """Checks if all unique letters in the word have been guessed."""
        return self._unique_word_letters.issubset(self.guesses)
