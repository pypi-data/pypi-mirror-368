"""This module defines the core logic for a Rock-Paper-Scissors style game."""

from __future__ import annotations

from dataclasses import dataclass

#: A tuple containing the default game options in winning order.
DEFAULT_OPTIONS = ("rock", "paper", "scissors")


@dataclass(frozen=True)
class GameRules:
    """Represents the immutable rules of a Rock-Paper-Scissors style game.

    This data-centric class holds the game options and provides a single
    method to compare choices. Other interactions can be performed directly
    on the public `options` attribute.

    Attributes:
        options: A tuple of valid game choices in winning order.
    """

    options: tuple[str, ...] = DEFAULT_OPTIONS

    def compare(self, player_1_choice: str, player_2_choice: str) -> int:
        """Compares two choices based on their circular relationship.

        The logic determines the winner by shifting the circular list of options
        so that the first player's choice is in the middle. The second player's
        choice then falls on the "losing" side or the "winning" side.

        Args:
            player_1_choice: The choice of the first player.
            player_2_choice: The choice of the second player.

        Returns:
             1 if player 1 wins, 0 for a draw, -1 if player 2 wins.
        """
        if player_1_choice == player_2_choice:
            return 0

        # The core of the algorithm: determine the winner based on position
        # in a circular list.
        length = len(self.options)
        half = length // 2

        # Find the index of the first player's choice.
        p1_index = self.options.index(player_1_choice)

        # Calculate a delta to shift the list so p1_index is at `half`.
        # This simplifies comparison by putting p1 at a known reference point.
        delta = half - p1_index
        p1_shifted_index = (p1_index + delta) % length
        p2_shifted_index = (self.options.index(player_2_choice) + delta) % length

        return 1 if p1_shifted_index > p2_shifted_index else -1


def create_rules_from_input(options_str: str) -> GameRules:
    """Creates a GameRules instance from a comma-separated string.

    If the input string is empty, default rules are returned.

    Args:
        options_str: A string of game options, e.g., "rock, paper, scissors".

    Returns:
        A new GameRules instance.
    """
    if not options_str:
        return GameRules()

    return GameRules(tuple(opt.strip() for opt in options_str.lower().split(",")))
