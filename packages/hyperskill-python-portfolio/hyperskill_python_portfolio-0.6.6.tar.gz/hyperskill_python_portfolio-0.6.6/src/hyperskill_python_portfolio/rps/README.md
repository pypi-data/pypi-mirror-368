# Project: Rock-Paper-Scissors

This project is a solution for the [Rock-Paper-Scissors](https://hyperskill.org/projects/78) project on Hyperskill. It's a command-line game that allows a user to play against the computer with classic or user-defined rules.

This project was an opportunity to practice core Python concepts in a fun, interactive context, focusing on clean architecture, robust logic, and modern development tooling.

## Core Features

  * **Classic & Extended Gameplay:** Play the standard "rock, paper, scissors" or provide a custom, comma-separated list of options (e.g., Rock-Paper-Scissors-Lizard-Spock) for a more complex game.
  * **Player vs. Computer:** The computer opponent makes its choice randomly, providing a fair challenge.
  * **Persistent Scoring:** The game reads from and updates a `rating.txt` file to keep track of the player's score across multiple sessions.
  * **Interactive Commands:** In addition to game moves, players can use special commands like `!rating` to check their score and `!exit` to quit the game gracefully.

## Technical Implementation

This solution goes beyond a simple script and is structured as a modern Python application:

  * **Modular Architecture:** The code is organized into distinct modules for game logic (`game_logic.py`), file handling (`file_handler.py`), and user interaction (`main.py`), following the principle of Separation of Concerns.
  * **Object-Oriented Design:** A `GameRules` dataclass encapsulates the core logic, pre-calculating winning conditions for efficiency and readability.
  * **Robust Tooling:** The project is configured for professional development workflows, including:
      * Static analysis with **mypy**.
      * Linting and formatting with **ruff**.
      * Automated checks on every commit with **pre-commit**.
      * Unit testing with **pytest**.

## How to Run

From the root of the `hyperskill-python-portfolio` directory, execute the following command:

```bash
python -m src.rps.main
```

The application will then prompt for your name and game options.
