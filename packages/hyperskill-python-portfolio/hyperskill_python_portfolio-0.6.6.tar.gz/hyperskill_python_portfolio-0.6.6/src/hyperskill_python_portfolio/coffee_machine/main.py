"""This module is the main entry point for the coffee machine application.

It creates a CoffeeMachine instance and runs the user interaction loop.
"""

from __future__ import annotations

from .machine import CoffeeMachine


def main() -> None:
    """Initializes the coffee machine and runs the user interaction loop."""
    # Create an instance with the project's required starting inventory
    machine = CoffeeMachine(water=400, milk=540, beans=120, cups=9, money=550)

    # The machine's state controls the loop's condition entirely.
    while machine.is_running:
        user_input = input(machine.prompt)
        machine.process_input(user_input)


if __name__ == "__main__":
    main()
