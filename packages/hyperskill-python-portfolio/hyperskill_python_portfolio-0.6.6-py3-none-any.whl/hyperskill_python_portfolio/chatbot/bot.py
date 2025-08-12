"""This module defines the ChatBot class and its conversational logic."""

from __future__ import annotations

import textwrap


class ChatBot:
    """A simple, rule-based chatbot that interacts with the user."""

    _QUIZ_PROMPT = textwrap.dedent("""
        Why do we use methods?
        1. To repeat a statement multiple times.
        2. To decompose a program into several small subroutines.
        3. To determine the execution time of a program.
        4. To interrupt the execution of a program.
    """)
    _QUIZ_CORRECT_ANSWER = 2

    def __init__(self, bot_name: str, birth_year: int) -> None:
        """Initializes the ChatBot.

        Args:
            bot_name: The name of the bot.
            birth_year: The year the bot was created.
        """
        self.bot_name = bot_name
        self.birth_year = birth_year

    def run(self) -> None:
        """Runs the main conversational flow of the chatbot."""
        self._show_bot_info()
        self._ask_for_name()
        self._guess_age()
        self._count_to_number()
        self._run_quiz()
        self._show_congratulations_message()

    def _show_bot_info(self) -> None:
        """Prints the bot's introductory message."""
        intro_message = textwrap.dedent(f"""
            Hello! My name is {self.bot_name}.
            I was created in {self.birth_year}.
        """)
        print(intro_message)

    def _ask_for_name(self) -> None:
        """Asks for the user's name and responds."""
        name = input("Please, remind me your name.\n> ")
        print(f"What a great name you have, {name}!")

    def _guess_age(self) -> None:
        """Guesses the user's age based on remainders."""
        print("\nLet me guess your age.")
        print("Enter remainders of dividing your age by 3, 5, and 7.")
        rem3 = self._get_integer_input("> ")
        rem5 = self._get_integer_input("> ")
        rem7 = self._get_integer_input("> ")
        age = (rem3 * 70 + rem5 * 21 + rem7 * 15) % 105
        print(f"Your age is {age}; that's a good time to start programming!")

    def _count_to_number(self) -> None:
        """Counts from 0 to a number provided by the user."""
        print("\nNow I will prove to you that I can count to any number you want.")
        target_number = self._get_integer_input("> ")
        for current_count in range(target_number + 1):
            print(current_count, "!")

    def _run_quiz(self) -> None:
        """Tests the user's programming knowledge."""
        print("\nLet's test your programming knowledge.")
        print(self._QUIZ_PROMPT)
        while True:
            answer = self._get_integer_input("Enter your choice: ")
            if answer == self._QUIZ_CORRECT_ANSWER:
                break
            print("Please, try again.")

    def _show_congratulations_message(self) -> None:
        """Prints a final congratulatory message."""
        print("\nCongratulations, have a nice day!")

    def _get_integer_input(self, prompt: str) -> int:
        """Gets and validates integer input from the user."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("That's not a valid integer. Please try again.")
