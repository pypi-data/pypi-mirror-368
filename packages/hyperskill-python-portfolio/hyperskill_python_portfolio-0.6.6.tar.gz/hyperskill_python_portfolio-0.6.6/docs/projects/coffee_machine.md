---
title: Coffee Machine
subtitle: From a simple script to a robust state machine
icon: material/coffee-outline
tags:
  - Object-Oriented Programming
  - State Machine
  - Enums
  - Dataclasses
  - Refactoring
---

# Project: Coffee Machine

## Overview

The Coffee Machine is an interactive, stateful command-line application that simulates the experience of using a real coffee machine. It manages resources like water, milk, and coffee beans, handles purchases, and allows for restocking.

This project serves as an excellent case study in refactoring a simple procedural script into a robust, object-oriented application using a state machine pattern.

!!! info "Official Project on Hyperskill"

    This project is based on the **[Coffee Machine](https://hyperskill.org/projects/68)** project from the Hyperskill platform. It's a fantastic exercise for practicing functions, loops, and conditional logic in Python.

    > **About the project from Hyperskill:**
    > What can be better than a cup of coffee during a break? A coffee that you don’t have to make yourself. It’s enough to press a couple of buttons on the machine and you get a cup of energy; but first, we should teach the machine how to do it. In this project, you will work on programming a coffee machine simulator. The machine works with typical products: coffee, milk, sugar, and plastic cups; if it runs out of something, it shows a notification. You can get three types of coffee: espresso, cappuccino, and latte. Since nothing’s for free, it also collects the money.


## Usage

To run the coffee machine simulator, use the following command in your terminal after installation:

```
coffeemachine
```

The application will then guide you through the available actions, such as buying coffee, filling supplies, or taking the money from the machine.

## The Refactoring Journey

The most valuable aspect of this project was the process of refactoring it from a simple script into a well-designed application.

!!! note "The Starting Point: A Procedural Script"

    Initially, the program was a set of functions operating on a single, global dictionary that held the machine's resources. This approach, while functional for a simple task, had several significant drawbacks:

    * **Hard to Test:** Functions with `input()` calls scattered throughout the logic are very difficult to test automatically.
    * **Poor Encapsulation:** Any function could directly modify the global state, creating a high risk of bugs and making the code hard to reason about.
    * **Unclear Logic:** The program flow was controlled by a series of `if/else` statements, which could easily become a tangled mess as new features were added.

### The Solution: A State Machine

To address these issues, we refactored the code around a central `CoffeeMachine` class designed as a **State Machine**.

!!! info "What is a State Machine?"

    A state machine is a design pattern where an object's behavior changes depending on its internal state. Our `CoffeeMachine` can be in several states, such as `MAIN_MENU`, `CHOOSING_COFFEE`, or `FILLING_WATER`. The current state dictates how user input is processed and what the next state will be. This completely eliminated the complex `if/else` chains.

### Better Data with Dataclasses and Enums

A key part of the refactoring was improving how we modeled our data. This is where Python's modern features shine.

#### States as Enums

Instead of using simple strings like `"main_menu"` for states (which can lead to typos), we used Python's built-in `Enum` type. This makes the code safer and more self-documenting.

```python
# From: src/hyperskill_python_portfolio/coffee_machine/models.py
from enum import Enum, auto

class State(Enum):
    """Represents the operational states of the CoffeeMachine."""
    MAIN_MENU = auto()
    CHOOSING_COFFEE = auto()
    FILLING_WATER = auto()
    # ... and so on
```

#### Recipes as Dataclasses

Similarly, all the data for a coffee recipe (water, milk, beans, price) was consolidated from multiple dictionaries into a single, clean `dataclass`. This creates an immutable, single source of truth for each coffee type.

```python
# From: src/hyperskill_python_portfolio/coffee_machine/models.py
from dataclasses import dataclass

@dataclass(frozen=True)
class CoffeeRecipe:
    """A data blueprint for a coffee type. Immutable by design."""
    name: str
    water_ml: int
    milk_ml: int
    beans_g: int
    price_usd: int
```

This approach makes the code safer, easier to read, and much simpler to maintain or extend.

## Key Python Concepts Illustrated

- **Object-Oriented Programming (OOP):** Encapsulating logic and data in the `CoffeeMachine` class.

- **Design Patterns:** Implementing a clean State Machine.

- **`enum.Enum`:** Creating safe and explicit enumerations for states.

- **`dataclasses`:** Building robust and immutable data models.

- **`@property`:** Creating clean, read-only attributes like `is_running` and `prompt`.

- **Type Hinting:** Ensuring code correctness and clarity for static analysis with `mypy`.

- **Testable Code:** Designing a class that can be tested in isolation by removing direct `input()` dependencies.
