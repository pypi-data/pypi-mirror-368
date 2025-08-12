"""Defines handler functions that connect CLI arguments to core logic."""

from __future__ import annotations

import sys
from argparse import Namespace

from hyperskill_python_portfolio.loancalc.core import (
    MONTHS_IN_YEAR,
    calculate_annuity_payment,
    calculate_annuity_periods,
    calculate_annuity_principal,
    calculate_diff,
)


def monthly_interest(annual_interest: float) -> float:
    """Calculates the monthly interest rate from the annual interest rate."""
    return annual_interest / (MONTHS_IN_YEAR * 100)


def handle_annuity(args: Namespace) -> str:
    """Handles the 'annuity' command.

    Validates arguments, dispatches to the correct annuity calculation function,
    and formats the result for printing.
    """
    known = [args.principal, args.payment, args.periods]
    if known.count(None) != 1:
        print(
            "Error: Exactly one of --principal, --payment, or --periods must be omitted.",
            file=sys.stderr,
        )
        sys.exit(1)

    interest = monthly_interest(args.interest)
    if args.payment is None:
        result = calculate_annuity_payment(interest, args.periods, args.principal)
        main_message = f"Your monthly payment = {result.payment}!"
    elif args.principal is None:
        result = calculate_annuity_principal(interest, args.periods, args.payment)
        main_message = f"Your loan principal = {result.principal}!"
    else:  # args.periods is None
        result = calculate_annuity_periods(interest, args.principal, args.payment)
        main_message = f"It will take {result.description} to repay this loan!"

    return main_message + f"\nOverpayment = {result.overpayment}"


def handle_diff(args: Namespace) -> str:
    """Handles the 'diff' (differentiated) command.

    Validates arguments, calls the differentiated calculation function,
    and formats the result for printing.
    """
    if hasattr(args, "payment") and args.payment is not None:
        print(
            "Error: --payment is not allowed with 'diff' calculation mode.",
            file=sys.stderr,
        )
        sys.exit(1)

    interest = monthly_interest(args.interest)
    result = calculate_diff(interest, args.periods, args.principal)

    return (
        "\n".join(
            f"Month {month}: payment is {payment}"
            for month, payment in enumerate(result.payments, start=1)
        )
        + f"\n\nOverpayment = {result.overpayment}"
    )
