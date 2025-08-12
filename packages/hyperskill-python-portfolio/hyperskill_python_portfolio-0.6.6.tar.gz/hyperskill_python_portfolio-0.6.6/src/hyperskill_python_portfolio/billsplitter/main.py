"""This module contains the main entry point for the Bill Splitter application."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Final

PROMPT_N_FRIENDS: Final[str] = "Enter the number of friends joining (including you):"
PROMPT_BILL_VALUE: Final[str] = "Enter the total bill value:"
PROMPT_LUCKY_FEATURE: Final[str] = 'Do you want to use the "Who is lucky?" feature? Write Yes/No:'


def get_non_negative_number[T: (int, float)](
    prompt: str,
    converter: Callable[[str], T],
) -> T:
    """Prompts for a non-negative number (int or float) and handles validation."""
    while True:
        try:
            value = converter(input(prompt))
            if value >= 0:
                return value
            print("Number cannot be negative.")
        except ValueError:
            print(f"Please enter a valid {converter.__name__}.")


def get_friend_names(count: int) -> list[str]:
    """Gets a list of names from user input."""
    print("Enter the name of every friend (including you), each on a new line:")
    return [input() for _ in range(count)]


def wants_feature(prompt: str) -> bool:
    """Asks a Yes/No question and returns a boolean."""
    return input(prompt).lower() == "yes"


def main() -> None:
    """Main function to run the bill splitter."""
    n_friends = get_non_negative_number(PROMPT_N_FRIENDS, int)

    if n_friends <= 0:
        print("No one is joining for the party")
        return

    names = get_friend_names(n_friends)
    bill_value = get_non_negative_number(PROMPT_BILL_VALUE, float)
    is_lucky_feature_enabled = wants_feature(PROMPT_LUCKY_FEATURE)

    lucky_friend: str | None = None
    if is_lucky_feature_enabled:
        lucky_friend = random.choice(names)  # noqa: S311
        print(f"{lucky_friend} is the lucky one!")
    else:
        print("No one is going to be lucky")

    num_payers = len(names) - (1 if lucky_friend else 0)
    split_value = round(bill_value / num_payers, 2) if num_payers > 0 else 0

    final_bill = {name: (0 if name == lucky_friend else split_value) for name in names}

    print(f"\n{final_bill}")


if __name__ == "__main__":
    main()
