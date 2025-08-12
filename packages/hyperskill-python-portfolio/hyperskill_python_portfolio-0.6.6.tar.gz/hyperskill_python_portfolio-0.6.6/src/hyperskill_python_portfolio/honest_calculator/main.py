"""This module contains the main entry point for the Honest Calculator application."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum


class Msg(Enum):
    """Enumeration for all user-facing messages."""

    # --- Prompts ---
    ENTER_EQUATION = "Enter an equation"
    STORE_RESULT = "Do you want to store the result? (y / n):"
    CONTINUE = "Do you want to continue calculations? (y / n):"
    ONE_DIGIT_SURE = "Are you sure? It is only one digit! (y / n):"
    ONE_DIGIT_SILLY = "Don't be silly! It's just one number! Add to the memory? (y / n):"
    ONE_DIGIT_EMBARRASS = "Last chance! Do you really want to embarrass yourself? (y / n):"

    # --- Errors & Warnings ---
    INVALID_NUMBER = "Do you even know what numbers are? Stay focused!"
    INVALID_OPERATOR = (
        "Yes ... an interesting math operation. You've slept through all classes, haven't you?"
    )
    DIV_BY_ZERO = "Yeah... division by zero. Smart move..."

    # --- Laziness Messages ---
    LAZY_PREFIX = "You are"
    IS_LAZY = " ... lazy"
    IS_VERY_LAZY = " ... very lazy"
    IS_VERY_VERY_LAZY = " ... very, very lazy"


class HonestCalculator:
    """Encapsulates the state and logic for the Honest Calculator."""

    def __init__(self) -> None:
        """Initializes the calculator with zero memory."""
        self.memory: float = 0.0

    def _get_user_confirmation(self, message: Msg) -> bool:
        """A helper to get a 'y' or 'n' answer from the user."""
        while (answer := input(f"{message.value} ").lower()) not in ("y", "n"):
            continue
        return answer == "y"

    def _is_one_digit(self, number: float) -> bool:
        """Checks if a number is a single-digit integer (-9 to 9)."""
        return number.is_integer() and -10 < number < 10

    def _store_result(self, result: float) -> None:
        """Handles the logic for storing a result in memory, with honesty checks."""
        if not self._get_user_confirmation(Msg.STORE_RESULT):
            return

        should_store = True
        if self._is_one_digit(result):
            # For one-digit numbers, we require a chain of confirmations.
            should_store = (
                self._get_user_confirmation(Msg.ONE_DIGIT_SURE)
                and self._get_user_confirmation(Msg.ONE_DIGIT_SILLY)
                and self._get_user_confirmation(Msg.ONE_DIGIT_EMBARRASS)
            )

        if should_store:
            self.memory = result

    def _check_laziness(self, x: float, y: float, oper: str) -> None:
        """Checks for and prints messages related to 'lazy' operations."""
        laziness_rules: list[tuple[Callable[[], bool], Msg]] = [
            (lambda: self._is_one_digit(x) and self._is_one_digit(y), Msg.IS_LAZY),
            (lambda: (x == 1 or y == 1) and oper == "*", Msg.IS_VERY_LAZY),
            (lambda: (x == 0 or y == 0) and oper in "+-*", Msg.IS_VERY_VERY_LAZY),
        ]

        messages_to_print = [msg.value for condition, msg in laziness_rules if condition()]

        if messages_to_print:
            full_message = Msg.LAZY_PREFIX.value + "".join(messages_to_print)
            print(full_message)

    def run(self) -> None:
        """The main application loop to run the calculator."""
        while True:
            print(Msg.ENTER_EQUATION.value)
            try:
                x_str, oper, y_str = input().split()
                x = self.memory if x_str == "M" else float(x_str)
                y = self.memory if y_str == "M" else float(y_str)
            except ValueError:
                print(Msg.INVALID_NUMBER.value)
                continue

            self._check_laziness(x, y, oper)

            match oper:
                case "+":
                    result = x + y
                case "-":
                    result = x - y
                case "*":
                    result = x * y
                case "/" if y != 0:
                    result = x / y
                case "/" if y == 0:
                    print(Msg.DIV_BY_ZERO.value)
                    continue
                case _:
                    print(Msg.INVALID_OPERATOR.value)
                    continue

            print(result)
            self._store_result(result)

            if not self._get_user_confirmation(Msg.CONTINUE):
                break


if __name__ == "__main__":
    calculator = HonestCalculator()
    calculator.run()
