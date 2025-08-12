# Hyperskill Python Portfolio

A collection of classic command-line applications and games, developed as a portfolio of
Python projects from the Hyperskill platform. Each application is a self-contained,
runnable program built with modern Python 3.12+.

This package allows you to instantly install and run a variety of small, fun programs
directly from your terminal.

## Quick Start: Installation & Usage

Install the package using `pip` (or any modern installer like `uv` or `pipx`):

```
pip install hyperskill-python-portfolio
```

Once installed, you can immediately run any of the included applications.

### Try a Game: Hangman

```
hangman
```

### Try a Simulator: Coffee Machine

```
coffeemachine
```

### Try a Utility: Loan Calculator

The loan calculator can compute annuity payments, principals, and more.

```
# Calculate the monthly payment for a loan
loancalc annuity --principal 500000 --interest 5.5 --periods 360

# Calculate the total principal for a given payment
loancalc annuity --payment 2800 --interest 5.5 --periods 360
```

## Available Applications

This portfolio includes the following command-line applications:

| **Command**     | **Description**                                              |
|-----------------|--------------------------------------------------------------|
| `billsplitter`  | A simple utility to split a bill among friends.              |
| `chatbot`       | A basic, friendly chatbot with scripted dialogue.            |
| `coffeemachine` | An interactive, stateful coffee machine simulator.           |
| `hangman`       | The classic word-guessing game.                              |
| `honestcalc`    | An interactive calculator with memory and 'honest' feedback. |
| `loancalc`      | A powerful command-line loan calculator.                     |
| `rps`           | Rock-Paper-Scissors with score tracking.                     |
| `zookeeper`     | A fun script that displays ASCII art of animals.             |

Each application is a standalone project, refactored for quality and built with modern
tooling.

## About This Project

This project serves two purposes:

1. **For Users:** To provide a simple, installable package of classic command-line tools
   and games.

2. **For Developers:** To serve as a practical portfolio demonstrating modern Python
   development practices.

The source code is heavily documented, tested with `pytest`, type-checked with `mypy`,
and formatted with `ruff`. It is intended to be a clear and readable example of a
well-structured Python application suite.

## For Contributors

This project is managed with a modern Python toolchain. If you are interested in the
development process or wish to contribute, please visit the
project's [GitHub repository](https://github.com/rabestro/hyperskill-python-portfolio "null").

The repository contains detailed information on the development setup, tooling (`uv`,
`ruff`, `mypy`), and how to run the quality checks.

## License

This project is licensed under the MIT License.
