# -*- coding: utf-8 -*-
"""
A simple banking system simulation that allows users to create credit card accounts,
log in, manage balances, and perform transfers.

This script demonstrates:
- Separation of concerns (data layer, domain logic, UI).
- Secure password (PIN) hashing with bcrypt.
- Atomic database transactions for transfers.
- Use of modern Python features like dataclasses, enums, and type hints.
"""
import secrets
import sqlite3
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# You must install the bcrypt library for this script to work.
# Run: pip install bcrypt
import bcrypt

# ---------- Configuration ----------
DB_PATH = "card.s3db"
IIN = "400000"  # Issuer Identification Number


# ---------- Data Structures ----------
@dataclass
class Account:
    """A data class to hold account information."""
    id: int
    number: str
    pin_hash: bytes
    balance: int


class MainMenu(Enum):
    """Enumeration for the main menu options."""
    CREATE = "1"
    LOGIN = "2"
    EXIT = "0"


class AccountMenu(Enum):
    """Enumeration for the logged-in account menu options."""
    BALANCE = "1"
    ADD_INCOME = "2"
    DO_TRANSFER = "3"
    CLOSE_ACCOUNT = "4"
    LOG_OUT = "5"
    EXIT = "0"


# ---------- Luhn Algorithm ----------
def _luhn_transform(digits: list[int]) -> list[int]:
    """
    Helper function to apply the Luhn doubling algorithm to a list of digits.
    This logic is shared between checksum calculation and validation.
    """
    transformed = list(digits)  # Create a copy
    for i in range(len(transformed) - 2, -1, -2):
        doubled = transformed[i] * 2
        transformed[i] = doubled - 9 if doubled > 9 else doubled
    return transformed


def calc_check_digit(partial_15: str) -> int:
    """Calculates the Luhn check digit for a 15-digit number string."""
    digits = [int(d) for d in partial_15]
    # Add a placeholder for the checksum calculation
    transformed_digits = _luhn_transform(digits + [0])
    checksum = sum(transformed_digits) % 10
    return (10 - checksum) % 10


def valid_luhn(number: str) -> bool:
    """Validates a number string using the Luhn algorithm."""
    if not number.isdigit():
        return False
    digits = [int(d) for d in number]
    transformed_digits = _luhn_transform(digits)
    return sum(transformed_digits) % 10 == 0


# ---------- Data Layer (Repository) ----------
class AccountRepo:
    """
    Repository class for all database operations.
    Acts as a context manager to ensure the connection is handled safely.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        """Opens the database connection and creates schema if it doesn't exist."""
        self.conn = sqlite3.connect(self.db_path)
        self._create_schema()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def _create_schema(self) -> None:
        """Creates the 'card' table if it doesn't already exist."""
        assert self.conn is not None
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY,
                number TEXT UNIQUE NOT NULL,
                pin BLOB NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()

    def create(self, number: str, pin: str) -> None:
        """Hashes a PIN and saves a new account to the database."""
        assert self.conn is not None
        hashed_pin = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())
        self.conn.execute(
            "INSERT INTO card (number, pin, balance) VALUES (?, ?, 0)",
            (number, hashed_pin),
        )
        self.conn.commit()

    def get(self, number: str) -> Optional[Account]:
        """Retrieves an account by its number."""
        assert self.conn is not None
        cursor = self.conn.execute(
            "SELECT id, number, pin, balance FROM card WHERE number = ?",
            (number,),
        )
        row = cursor.fetchone()
        return Account(*row) if row else None

    def exists(self, number: str) -> bool:
        """Checks if an account with the given number exists."""
        assert self.conn is not None
        row = self.conn.execute(
            "SELECT 1 FROM card WHERE number = ?",
            (number,),
        ).fetchone()
        return row is not None

    def get_balance(self, number: str) -> int:
        """Retrieves the balance for a given account number."""
        assert self.conn is not None
        row = self.conn.execute(
            "SELECT balance FROM card WHERE number = ?",
            (number,),
        ).fetchone()
        return row[0] if row else 0

    def add_income(self, number: str, income: int) -> None:
        """Adds income to an account's balance."""
        assert self.conn is not None
        self.conn.execute(
            "UPDATE card SET balance = balance + ? WHERE number = ?",
            (income, number),
        )
        self.conn.commit()

    def transfer(self, from_number: str, to_number: str, amount: int) -> bool:
        """Performs an atomic transfer between two accounts."""
        assert self.conn is not None
        try:
            with self.conn:  # Begins a transaction
                # 1. Check if sender has enough money
                sender_balance = self.get_balance(from_number)
                if sender_balance < amount:
                    return False
                # 2. Debit the sender
                self.conn.execute(
                    "UPDATE card SET balance = balance - ? WHERE number = ?",
                    (amount, from_number),
                )
                # 3. Credit the receiver
                self.conn.execute(
                    "UPDATE card SET balance = balance + ? WHERE number = ?",
                    (amount, to_number),
                )
        except sqlite3.Error:
            # Transaction will be automatically rolled back on error
            return False
        return True

    def delete(self, number: str) -> None:
        """Deletes an account from the database."""
        assert self.conn is not None
        self.conn.execute("DELETE FROM card WHERE number = ?", (number,))
        self.conn.commit()


# ---------- Domain Logic ----------
def generate_card_number(repo: AccountRepo) -> str:
    """Generates a new, unique card number that passes the Luhn check."""
    while True:
        account_identifier = "".join(str(secrets.randbelow(10)) for _ in range(9))
        partial = IIN + account_identifier
        check_digit = calc_check_digit(partial)
        number = partial + str(check_digit)
        if not repo.exists(number):
            return number


def generate_pin() -> str:
    """Generates a random 4-digit PIN."""
    return f"{secrets.randbelow(10000):04d}"


def create_account(repo: AccountRepo) -> tuple[str, str]:
    """
    Creates a new account with a unique card number and PIN.
    This function will retry if a card number collision occurs (extremely rare).
    """
    while True:
        number = generate_card_number(repo)
        pin = generate_pin()
        try:
            repo.create(number, pin)
            return number, pin
        except sqlite3.IntegrityError:
            # In the unlikely event of a number collision between generation
            # and insertion, the loop will simply try again.
            continue


# ---------- Presentation (UI) Layer ----------
def _handle_transfer(repo: AccountRepo, current_user_number: str) -> None:
    """Handles the user interaction logic for transferring money."""
    print("\nTransfer")
    print("Enter card number:")
    target_number = input().strip()

    if target_number == current_user_number:
        print("You can't transfer money to the same account!")
        return

    if not valid_luhn(target_number):
        print("Probably you made a mistake in the card number. Please try again!")
        return

    if not repo.exists(target_number):
        print("Such a card does not exist.")
        return

    print("Enter how much money you want to transfer:")
    try:
        amount = int(input().strip())
        if amount <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    if repo.get_balance(current_user_number) < amount:
        print("Not enough money!")
        return

    if repo.transfer(current_user_number, target_number, amount):
        print("Success!")
    else:
        print("An error occurred during the transfer.")


def account_menu(repo: AccountRepo, account_number: str) -> None:
    """Displays the menu for a logged-in user and handles their actions."""
    print("\nYou have successfully logged in!")
    while True:
        print("\n1. Balance\n2. Add income\n3. Do transfer")
        print("4. Close account\n5. Log out\n0. Exit")
        choice = input().strip()

        if choice == AccountMenu.BALANCE.value:
            balance = repo.get_balance(account_number)
            print(f"\nBalance: {balance}")

        elif choice == AccountMenu.ADD_INCOME.value:
            print("\nEnter income:")
            try:
                income = int(input().strip())
                if income < 0:
                    print("Income must be non-negative.")
                    continue
                repo.add_income(account_number, income)
                print("Income was added!")
            except ValueError:
                print("Invalid amount.")

        elif choice == AccountMenu.DO_TRANSFER.value:
            _handle_transfer(repo, account_number)

        elif choice == AccountMenu.CLOSE_ACCOUNT.value:
            repo.delete(account_number)
            print("\nThe account has been closed!")
            return  # Exit account menu

        elif choice == AccountMenu.LOG_OUT.value:
            print("\nYou have successfully logged out!")
            return  # Exit account menu

        elif choice == AccountMenu.EXIT.value:
            print("\nBye!")
            sys.exit(0)


def login(repo: AccountRepo) -> None:
    """Handles the user login process."""
    print("\nEnter your card number:")
    card_number = input().strip()
    print("Enter your PIN:")
    pin = input().strip()

    account = repo.get(card_number)
    if account and bcrypt.checkpw(pin.encode(), account.pin_hash):
        account_menu(repo, account.number)
    else:
        print("\nWrong card number or PIN!")


def main() -> None:
    """Main function to run the banking system application."""
    # The 'with' statement ensures the database connection is managed safely.
    with AccountRepo() as repo:
        while True:
            print("\n1. Create an account\n2. Log into account\n0. Exit")
            choice = input().strip()

            if choice == MainMenu.CREATE.value:
                number, pin = create_account(repo)
                print("\nYour card has been created")
                print(f"Your card number:\n{number}")
                print(f"Your card PIN:\n{pin}")

            elif choice == MainMenu.LOGIN.value:
                login(repo)

            elif choice == MainMenu.EXIT.value:
                print("\nBye!")
                break


if __name__ == "__main__":
    main()