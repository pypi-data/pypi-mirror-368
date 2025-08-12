"""Configures the command-line interface for the loan calculator."""

from __future__ import annotations

import argparse

from .handlers import handle_annuity, handle_diff


def non_negative_int(value: str) -> int:
    """Custom argparse type for a non-negative integer."""
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise ValueError
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Value must be a non-negative integer: '{value}'"
        ) from None


def non_negative_float(value: str) -> float:
    """Custom argparse type for a non-negative float."""
    try:
        fvalue = float(value)
        if fvalue < 0:
            raise ValueError
        return fvalue
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Value must be a non-negative float: '{value}'"
        ) from None


def build_parser() -> argparse.ArgumentParser:
    """Builds and configures the argument parser for the application."""
    parser = argparse.ArgumentParser(
        description="💸 Loan Calculator: Compute annuity or differentiated payments."
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Select a loan calculation mode.",
    )

    # --- 'diff' command parser ---
    parser_diff = subparsers.add_parser(
        name="diff",
        help="Calculate monthly differentiated payments",
    )
    parser_diff.add_argument(
        "--principal",
        type=non_negative_int,
        required=True,
        help="Loan principal",
    )
    parser_diff.add_argument(
        "--periods",
        type=non_negative_int,
        required=True,
        help="Number of months",
    )
    parser_diff.add_argument(
        "--interest",
        type=non_negative_float,
        required=True,
        help="Annual interest rate (%%)",
    )
    parser_diff.set_defaults(func=handle_diff)

    # --- 'annuity' command parser ---
    parser_annuity = subparsers.add_parser(
        "annuity",
        help="Calculate annuity payment, principal, or periods",
    )
    parser_annuity.add_argument(
        "--principal",
        type=non_negative_int,
        help="Loan principal",
    )
    parser_annuity.add_argument(
        "--payment",
        type=non_negative_int,
        help="Monthly payment",
    )
    parser_annuity.add_argument(
        "--periods",
        type=non_negative_int,
        help="Number of months",
    )
    parser_annuity.add_argument(
        "--interest",
        type=non_negative_float,
        required=True,
        help="Annual interest rate (%%)",
    )
    parser_annuity.set_defaults(func=handle_annuity)

    return parser
