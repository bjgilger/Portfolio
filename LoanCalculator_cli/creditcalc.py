import argparse
import sys
from math import ceil, log


def validate_args(args):
    # Ensure valid type
    if args.type not in ['annuity', 'diff']:
        return False

    # Interest is required for all operations
    if args.interest is None:
        return False

    # Ensure no negative values
    for val in [args.principal, args.payment, args.periods, args.interest]:
        if val is not None and val < 0:
            return False

    # For diff payment, payment must NOT be provided
    if args.type == 'diff':
        if args.payment is not None:
            return False
        if args.principal is None or args.periods is None:
            return False

    # For annuity, at least 2 of principal, payment, and periods must be present
    if args.type == 'annuity':
        filled = [args.principal, args.payment, args.periods]
        if sum(x is not None for x in filled) < 2:
            return False

    return True



# Setup parser
parser = argparse.ArgumentParser(description='Loan Calculator')
parser.add_argument('--principal', type=float, help='Loan principal')
parser.add_argument('--payment', type=float, help='Monthly payment')
parser.add_argument('--periods', type=int, help='Number of months')
parser.add_argument('--interest', type=float, help='Annual interest rate as a percentage')
parser.add_argument('--type', help='Calculation type: "annuity" or "diff"')


args = parser.parse_args()

if not validate_args(args):
    print("Incorrect parameters")
    sys.exit(1)


# Extract arguments
principal = args.principal
payment = args.payment
periods = args.periods
interest = args.interest
type = args.type

# Basic validation
if args.type not in ['annuity', 'diff']:
    print("Incorrect parameters")
    sys.exit(1)


if any(x is not None and x < 0 for x in [principal, payment, periods, interest]):
    print("Incorrect parameters")
    sys.exit(1)

if len([arg for arg in [principal, payment, periods] if arg is not None]) < 2:
    print("Incorrect parameters")
    sys.exit(1)

monthly_interest = interest / 100 / 12

# Annuity logic
if type == 'annuity':
    if payment is None and principal is not None and periods is not None:
        payment = (principal * monthly_interest * (1 + monthly_interest) ** periods) / \
                  (((1 + monthly_interest) ** periods) - 1)
        payment = ceil(payment)
        print(f"Your monthly payment = {payment}")
        print(f"Overpayment = {payment * periods - int(principal)}")


    elif principal is None and payment is not None and periods is not None:
        principal = payment / ((monthly_interest * (1 + monthly_interest) ** periods) /
                               ((1 + monthly_interest) ** periods - 1))
        print(f"Your loan principal = {ceil(principal)}")
        print(f"Overpayment = {ceil(payment * periods - principal)}")

    elif periods is None and principal is not None and payment is not None:
        try:
            periods = log(payment / (payment - monthly_interest * principal), 1 + monthly_interest)
            periods = ceil(periods)
            years = periods // 12
            months = periods % 12
            time_str = f"{years} years" if years else ""
            if months:
                time_str += f" and {months} months" if time_str else f"{months} months"
            print(f"It will take {time_str} to repay this loan!")
            print(f"Overpayment = {ceil(payment * periods - principal)}")
        except ValueError:
            print("Error: payment must be greater than interest portion")
            sys.exit(1)

    else:
        print("Incorrect parameters")
        sys.exit(1)

# Differentiated payment logic
elif type == 'diff':
    if principal is not None and periods is not None:
        total_payment = 0
        for m in range(1, periods + 1):
            diff_payment = ceil(principal / periods + monthly_interest * (principal - (principal * (m - 1) / periods)))
            total_payment += diff_payment
            print(f"Month {m}: payment is {diff_payment}")
        print(f"Overpayment = {ceil(total_payment - principal)}")
    else:
        print("Incorrect parameters")
        sys.exit(1)
