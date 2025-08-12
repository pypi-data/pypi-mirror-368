---
title: Honest Calculator
subtitle: A case study in refactoring a script into a testable application
icon: material/calculator-variant-outline
tags:
  - Python
  - Refactoring
  - Testing
  - OOP
---

# Project: Honest Calculator

## Overview

The Honest Calculator is an interactive command-line application that performs basic arithmetic operations. What makes it "honest" is its quirky, opinionated personality. It provides funny feedback on certain inputs (like multiplying by 1 or using single-digit numbers) and includes a multi-step confirmation flow before storing "unimpressive" results.

This project is a perfect exercise in refactoring a simple script with "magic numbers" and global state into a clean, object-oriented, and testable application.

!!! info "Official Project on Hyperskill"

    This project is my implementation of the **[Honest Calculator](https://hyperskill.org/projects/208)** project from the Hyperskill platform.

    The premise is fun: I had to build a calculator for a fictional "International Union Against Idleness" competition. The goal wasn't just to calculate, but to motivate users. The calculator helps with complex math, but for simple operations—like adding small numbers or multiplying by one—it gets a bit "honest" and encourages the user to do it themselves. This quirky requirement makes it a great challenge for handling state and conditional logic.

    > For me, this project was the perfect opportunity to move beyond a simple script. The need to manage memory, a series of "laziness" checks, and a multi-step confirmation flow pushed me to refactor the initial procedural code into a much cleaner, class-based design. It became a fantastic case study in making code not just work, but be testable and readable.

## Usage

To run the calculator, use the following command in your terminal after installation:

```shell
honestcalc
```

The application will prompt you to enter equations like `2 + 2` or `5` * `M` (to use the value from memory).

## The Refactoring Journey

This project provides a classic example of how moving from a procedural script to an object-oriented design dramatically improves code quality.

!!! note "The Starting Point: A 'Quick and Dirty' Script"

    The first working version was a single script with several issues common in early drafts:

    - **Global State:** The `memory` was a global variable, making it hard to track where it was being modified.
    - **Magic Numbers:** All user-facing messages were stored in a large tuple, and accessed with numeric indices like `MESSAGE[4]` or `MESSAGE[10]`. This was unreadable and extremely brittle; adding a new message would require re-numbering all subsequent indices.
    - **Difficult to Test:** With `input()` and `print()` calls mixed directly into the main logic loop, writing automated unit tests was nearly impossible.

### The Solution: An OOP Structure with Enums

The refactoring focused on solving these core problems by introducing a class and leveraging modern Python features.

#### 1. Encapsulation with a Class

All logic and state were moved into a central `HonestCalculator` class. This immediately solved the global state problem by making `memory` an instance attribute (`self.memory`).

#### 2. Replacing Magic Numbers with Enums

This was the most impactful change for readability. The tuple of messages was replaced with a dedicated `Enum`, transforming unreadable code into self-documenting code.

**Before:**

```python
# Unclear and brittle
print(MESSAGE[3])
```

**After:**

```python
# From: src/hyperskill_python_portfolio/honest_calculator/main.py
class Msg(Enum):
    # ...
    DIV_BY_ZERO = "Yeah... division by zero. Smart move..."

# Clear, safe, and self-documenting
print(Msg.DIV_BY_ZERO.value)
```

#### 3. Data-Driven Logic

Instead of a complex chain of `if` statements for the laziness checks, we adopted a data-driven approach. A list of `(condition, message)` tuples defines the rules, making the logic cleaner and easier to extend.

```python
# From: src/hyperskill_python_portfolio/honest_calculator/main.py
laziness_rules = [
    (lambda: self._is_one_digit(x) and self._is_one_digit(y), Msg.IS_LAZY),
    (lambda: (x == 1 or y == 1) and oper == "*", Msg.IS_VERY_LAZY),
    # ... more rules
]
```

This journey turned a fragile script into a robust, readable, and maintainable application, ready for testing and extension.

## Key Python Concepts Illustrated

- **Object-Oriented Programming (OOP):** Encapsulating state and behavior in the `HonestCalculator` class.

- **`enum.Enum`:** Eliminating "magic numbers" by creating a safe, named collection of constants for all user-facing messages.

- **Modern Control Flow (`match...case`):** Using structural pattern matching for elegantly handling different arithmetic operators.

- **Data-Driven Design:** Defining logic (like the laziness checks) as data, making it more modular and extensible.

- **Unit Testing with `pytest`:** Writing comprehensive tests by using fixtures like `monkeypatch` (to mock `input()`) and `capsys` (to capture `print` output).

- **Type Hinting:** Using type annotations for all functions and variables to enable static analysis with `mypy`.
