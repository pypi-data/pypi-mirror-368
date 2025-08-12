"""Defines the data models for the Loan Calculator."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LoanResult:
    """Represents the results of a loan calculation.

    This is an immutable data container. Each calculation function in the
    core module will return an instance of this class.

    Attributes:
        payments: A list of monthly payments for differentiated loans.
        payment: The single monthly payment for an annuity loan.
        periods: The total number of periods (months) for the loan.
        principal: The calculated loan principal.
        overpayment: The total amount paid over the loan principal.
        description: A human-readable description, e.g., for loan duration.
    """

    payments: list[int] = field(default_factory=list)
    payment: int | None = None
    periods: int | None = None
    principal: int | None = None
    overpayment: int = 0
    description: str | None = None
