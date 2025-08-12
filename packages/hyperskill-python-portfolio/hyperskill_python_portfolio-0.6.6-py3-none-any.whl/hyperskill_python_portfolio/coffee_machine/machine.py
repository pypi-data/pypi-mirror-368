"""This module defines the core CoffeeMachine class.

It contains the state machine logic, resource management, and all the
operations the coffee machine can perform.
"""

from __future__ import annotations

from types import MappingProxyType

from .models import RECIPES, CoffeeRecipe, State


class CoffeeMachine:
    """Manages the state and operations of a virtual coffee machine."""

    _PROMPTS = MappingProxyType(
        {
            State.MAIN_MENU: "Write action (buy, fill, take, remaining, exit): ",
            State.CHOOSING_COFFEE: "What do you want to buy? "
            "1 - espresso, 2 - latte, 3 - cappuccino, back - to main menu: ",
            State.FILLING_WATER: "Write how many ml of water you want to add:",
            State.FILLING_MILK: "Write how many ml of milk you want to add:",
            State.FILLING_BEANS: "Write how many grams of coffee beans you want to add:",
            State.FILLING_CUPS: "Write how many disposable cups you want to add:",
        }
    )

    def __init__(self, water: int, milk: int, beans: int, cups: int, money: int) -> None:
        """Initializes the coffee machine with the given resources."""
        self.water = water
        self.milk = milk
        self.beans = beans
        self.cups = cups
        self.money = money
        self.state = State.MAIN_MENU

    @property
    def is_running(self) -> bool:
        """Reports if the machine is in an active, operational state."""
        return self.state != State.SHUTDOWN

    @property
    def prompt(self) -> str:
        """Returns the appropriate user prompt for the current state."""
        return self._PROMPTS.get(self.state, "")

    def process_input(self, user_input: str) -> None:
        """Routes user input to the correct handler based on the current state."""
        # A mapping of states to the methods that handle them.
        # This is a clean alternative to a large if/elif/else block.
        state_handlers = {
            State.MAIN_MENU: self._handle_main_menu,
            State.CHOOSING_COFFEE: self._handle_buy,
            State.FILLING_WATER: self._handle_fill_water,
            State.FILLING_MILK: self._handle_fill_milk,
            State.FILLING_BEANS: self._handle_fill_beans,
            State.FILLING_CUPS: self._handle_fill_cups,
        }
        handler = state_handlers.get(self.state)
        if handler:
            handler(user_input)

    # --- State Handler Methods ---

    def _handle_main_menu(self, action: str) -> None:
        """Handles user actions from the main menu."""
        if action == "buy":
            self.state = State.CHOOSING_COFFEE
        elif action == "fill":
            self.state = State.FILLING_WATER
        elif action == "take":
            self._take_money()
        elif action == "remaining":
            self._print_remaining()
        elif action == "exit":
            self.state = State.SHUTDOWN

    def _handle_buy(self, choice: str) -> None:
        """Handles the user's coffee selection."""
        if choice == "back":
            self.state = State.MAIN_MENU
            return

        recipe = RECIPES.get(choice)
        if recipe:
            self._make_coffee(recipe)
        else:
            print("Invalid selection. Please try again.")

        # Always return to the main menu after a buy action
        self.state = State.MAIN_MENU

    def _handle_fill_water(self, amount_str: str) -> None:
        self.water += int(amount_str)
        self.state = State.FILLING_MILK

    def _handle_fill_milk(self, amount_str: str) -> None:
        self.milk += int(amount_str)
        self.state = State.FILLING_BEANS

    def _handle_fill_beans(self, amount_str: str) -> None:
        self.beans += int(amount_str)
        self.state = State.FILLING_CUPS

    def _handle_fill_cups(self, amount_str: str) -> None:
        self.cups += int(amount_str)
        self.state = State.MAIN_MENU  # Return to main menu after the last fill step

    # --- Private Action Methods ---

    def _print_remaining(self) -> None:
        """Prints the current inventory of the coffee machine."""
        print("\nThe coffee machine has:")
        print(f"{self.water} ml of water")
        print(f"{self.milk} ml of milk")
        print(f"{self.beans} g of coffee beans")
        print(f"{self.cups} disposable cups")
        print(f"${self.money} of money\n")

    def _take_money(self) -> None:
        """Dispenses all the money from the machine."""
        print(f"\nI gave you ${self.money}\n")
        self.money = 0

    def _check_resources(self, recipe: CoffeeRecipe) -> tuple[bool, str | None]:
        """Checks if there are enough resources to make a coffee."""
        if self.water < recipe.water_ml:
            return False, "water"
        if self.milk < recipe.milk_ml:
            return False, "milk"
        if self.beans < recipe.beans_g:
            return False, "coffee beans"
        if self.cups < recipe.cups:
            return False, "disposable cups"
        return True, None

    def _make_coffee(self, recipe: CoffeeRecipe) -> None:
        """Makes a coffee if resources are sufficient."""
        can_make, missing_resource = self._check_resources(recipe)

        if can_make:
            print("I have enough resources, making you a coffee!")
            self.water -= recipe.water_ml
            self.milk -= recipe.milk_ml
            self.beans -= recipe.beans_g
            self.cups -= recipe.cups
            self.money += recipe.price_usd
        else:
            print(f"Sorry, not enough {missing_resource}!")
