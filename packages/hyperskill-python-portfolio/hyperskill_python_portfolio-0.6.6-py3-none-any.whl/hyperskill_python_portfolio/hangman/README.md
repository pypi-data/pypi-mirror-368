# Project: Hangman

This project is a solution for the [Hangman](https://hyperskill.org/projects/69) project on Hyperskill. It's a classic command-line word-guessing game where the player tries to uncover a hidden word before running out of attempts.

This project began as an exercise in Python fundamentals but was elevated into a complete, modern application. The focus was on creating a clean, testable architecture, ensuring code quality with a full suite of development tools, and automating checks with a professional CI/CD pipeline.

## Core Features

* **Interactive Menu:** Players can choose to play a new game, view their win/loss record, or exit gracefully.
* **Classic Hangman Gameplay:** Guess letters to reveal a hidden word chosen randomly from a predefined list (`python`, `java`, `swift`, `javascript`).
* **Limited Attempts:** Players have a fixed number of 8 lives, creating a challenging and engaging experience.
* **Robust Input Handling:** The game gracefully handles invalid inputs, such as non-lowercase letters, multi-character inputs, or repeated guesses, without penalizing the player's lives.
* **Persistent Statistics:** The game tracks wins and losses for the entire session.

## Technical Implementation

This solution is engineered to reflect modern Python best practices, going far beyond a simple script.

* **Modular Architecture:** The application is logically divided into distinct modules for data structures (`models.py`), user interaction (`io_utils.py`), core application logic (`game.py`), and the entry point (`main.py`), following the principle of Separation of Concerns.
* **Data-Driven Design:** The project heavily utilizes `Enums` (`Status`, `MenuOption`) and `Dataclasses` (`HangmanSession`, `GameStatistics`) to cleanly and safely model the application's state and logic.
* **Performance Optimization:** The `HangmanSession` class uses `__post_init__` to pre-calculate and cache the set of unique letters in the word, making win-condition checks highly efficient.
* **Robust Tooling & CI/CD:** The project is configured for a professional development workflow, validated by an automated pipeline:
    * Linting and formatting with **Ruff**.
    * Strict static type checking with **MyPy**.
    * Unit testing of core logic with **Pytest**.
    * A full **GitHub Actions** CI pipeline that automatically validates the code on every push and pull request against multiple Python versions (3.11, 3.12, 3.13).

## How to Run

From the root of the `hyperskill-python-portfolio` directory, execute the following command:

```bash
python -m hangman.hangman.main
````

The application will then start and display the main menu.
