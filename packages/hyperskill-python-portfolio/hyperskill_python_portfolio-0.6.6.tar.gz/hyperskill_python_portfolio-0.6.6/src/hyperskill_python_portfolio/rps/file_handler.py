"""Handles reading from and writing to the player rating file."""

from __future__ import annotations

import logging
from pathlib import Path

DEFAULT_RATING_FILE = Path("rating.txt")


def get_user_score(username: str, file_path: Path = DEFAULT_RATING_FILE) -> int:
    """Reads a user's score from the rating file.

    Args:
        username: The name of the user whose score is to be retrieved.
        file_path: The path to the file containing user ratings.

    Returns:
        The user's score as an integer.

    Raises:
        FileNotFoundError: If the file at `file_path` cannot be found.
        ValueError: If the user is not found, or if a score is malformed.
    """
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 2:
                continue  # Skip malformed lines

            name, score_str = parts
            if name == username:
                return int(score_str)

    raise ValueError(f"Username '{username}' not found in {file_path}")


def save_user_score(username: str, score: int, file_path: Path = DEFAULT_RATING_FILE) -> None:
    """Saves or updates a user's score in the rating file.

    This function reads all existing scores, updates the score for the
    specified user (or adds them if new), and writes the entire file back.

    Args:
        username: The name of the user whose score is to be saved.
        score: The new score to save for the user.
        file_path: The path to the file where ratings are stored.
    """
    scores: dict[str, int] = {}
    try:
        with open(file_path, encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    name, score_str = parts
                    try:
                        scores[name] = int(score_str)
                    except ValueError:
                        logging.warning(f"Skipping malformed score for {name} in {file_path}")
    except FileNotFoundError:
        logging.info(f"Rating file {file_path} not found. A new one will be created.")

    scores[username] = score

    with open(file_path, "w", encoding="utf-8") as file:
        for name, s in scores.items():
            file.write(f"{name} {s}\n")
