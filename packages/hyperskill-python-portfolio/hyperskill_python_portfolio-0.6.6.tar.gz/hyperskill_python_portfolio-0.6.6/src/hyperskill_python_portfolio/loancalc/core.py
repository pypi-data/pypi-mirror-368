"""Core functionality for the loan calculator."""

from __future__ import annotations

from math import ceil, log, pow

from .models import LoanResult

MONTHS_IN_YEAR = 12


def calculate_annuity_payment(interest: float, periods: int, principal: int) -> LoanResult:
    """Calculates the fixed monthly annuity payment."""
    compound = pow(1 + interest, periods)
    payment = ceil(principal * (interest * compound) / (compound - 1))
    overpayment = payment * periods - principal
    return LoanResult(payment=payment, overpayment=overpayment)


def calculate_annuity_principal(interest: float, periods: int, payment: int) -> LoanResult:
    """Calculates the loan principal based on an annuity payment."""
    compound = pow(1 + interest, periods)
    principal = payment / ((interest * compound) / (compound - 1))
    overpayment = payment * periods - principal
    return LoanResult(principal=int(principal), overpayment=ceil(overpayment))


def calculate_annuity_periods(interest: float, principal: int, payment: int) -> LoanResult:
    """Calculates the number of periods to repay an annuity loan."""
    periods = ceil(log(payment / (payment - interest * principal), 1 + interest))
    years, months = divmod(periods, MONTHS_IN_YEAR)

    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")

    description = " and ".join(parts)
    overpayment = payment * periods - principal
    return LoanResult(periods=periods, overpayment=overpayment, description=description)


def calculate_diff(interest: float, periods: int, principal: int) -> LoanResult:
    """Calculates all monthly payments for a differentiated loan."""
    payments_generator = (
        ceil((principal / periods) + (interest * (principal - (principal * (m - 1) / periods))))
        for m in range(1, periods + 1)
    )

    payments = list(payments_generator)
    overpayment = sum(payments) - principal

    return LoanResult(payments=payments, overpayment=overpayment)
