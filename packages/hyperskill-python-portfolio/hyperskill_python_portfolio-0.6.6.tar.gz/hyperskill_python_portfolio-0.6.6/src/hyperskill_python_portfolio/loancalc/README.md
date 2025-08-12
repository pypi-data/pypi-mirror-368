# Loan Calculator (`loancalc`)

A powerful and flexible command-line application for calculating loan payments and terms. This tool supports both
annuity and differentiated payment schemes.

## Features

- **Calculate Annuity Payments**: Determine the fixed monthly payment amount based on the loan principal, period, and
  interest rate.

- **Calculate Loan Principal**: Find the total loan amount you can afford based on the monthly payment, period, and
  interest rate.

- **Calculate Repayment Period**: Estimate how long it will take to repay a loan based on the principal, monthly
  payment, and interest rate.

- **Calculate Differentiated Payments**: Compute the payment for each month, which varies over the life of the loan.

## Usage

The application is structured with sub-commands for different payment types.

```
loancalc [command] [options]
```

### Commands

- `annuity`: Used for calculations involving fixed monthly payments.

- `diff`: Used for calculations involving differentiated (declining) payments.

## Examples

### Annuity Payments

1. Calculate the monthly payment:

(You know the principal, number of months, and interest rate)

```
loancalc annuity --principal 500000 --periods 360 --interest 7.5
```

2. Calculate the loan principal:

(You know the monthly payment, number of months, and interest rate)

```
loancalc annuity --payment 3497 --periods 360 --interest 7.5
```

3. Calculate the number of months to repay:

(You know the principal, monthly payment, and interest rate)

```
loancalc annuity --principal 500000 --payment 3500 --interest 7.5
```

### Differentiated Payments

Calculate the monthly payments for the entire loan period:

(You know the principal, number of months, and interest rate. The --payment argument is not used here.)

```
loancalc diff --principal 1000000 --periods 12 --interest 10
```

## Arguments

### `annuity` Command Arguments

|               |                                                                        |                                                |
|---------------|------------------------------------------------------------------------|------------------------------------------------|
| **Argument**  | **Description**                                                        | **Required?**                                  |
| `--principal` | The total loan amount.                                                 | Yes, unless calculating the principal.         |
| `--payment`   | The fixed monthly payment amount.                                      | Yes, unless calculating the payment.           |
| `--periods`   | The total number of months to repay the loan.                          | Yes, unless calculating the number of periods. |
| `--interest`  | The annual interest rate (e.g., `7.5` for 7.5%). Must be non-negative. | **Always**                                     |

**Note:** For the `annuity` command, you must provide exactly three of the four arguments. The missing one will be
calculated.

### `diff` Command Arguments

|               |                                               |               |
|---------------|-----------------------------------------------|---------------|
| **Argument**  | **Description**                               | **Required?** |
| `--principal` | The total loan amount.                        | **Always**    |
| `--periods`   | The total number of months to repay the loan. | **Always**    |
