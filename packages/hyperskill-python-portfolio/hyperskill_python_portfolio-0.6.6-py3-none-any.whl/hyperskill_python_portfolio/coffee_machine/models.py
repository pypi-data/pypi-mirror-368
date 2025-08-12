"""This module defines the data models for the coffee machine application."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class State(Enum):
    """Represents the operational states of the CoffeeMachine."""

    MAIN_MENU = auto()
    CHOOSING_COFFEE = auto()
    FILLING_WATER = auto()
    FILLING_MILK = auto()
    FILLING_BEANS = auto()
    FILLING_CUPS = auto()
    SHUTDOWN = auto()


@dataclass(frozen=True)
class CoffeeRecipe:
    """A data blueprint for a coffee type. Immutable by design."""

    name: str
    water_ml: int
    milk_ml: int
    beans_g: int
    price_usd: int
    cups: int = 1


# A single, unified source of truth for all recipes, keyed by user input.
RECIPES = {
    "1": CoffeeRecipe(name="espresso", water_ml=250, milk_ml=0, beans_g=16, price_usd=4),
    "2": CoffeeRecipe(name="latte", water_ml=350, milk_ml=75, beans_g=20, price_usd=7),
    "3": CoffeeRecipe(name="cappuccino", water_ml=200, milk_ml=100, beans_g=12, price_usd=6),
}
