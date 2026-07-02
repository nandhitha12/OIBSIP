"""
Random Password Generator — OIBSIP Task 3 (Beginner Tier)
Author: Nandhitha Reddy

A command-line tool that generates strong, random passwords based on
user-defined length and character type criteria.

Run:
    python password_cli.py
"""

import random
import string


def get_length() -> int:
    """Ask for password length, enforcing an 8-character minimum."""
    while True:
        raw = input("Enter desired password length (minimum 8): ").strip()
        if not raw.isdigit():
            print("  Please enter a whole number.")
            continue
        length = int(raw)
        if length < 8:
            print("  Length must be at least 8 characters.")
            continue
        return length


def get_character_types() -> dict:
    """
    Ask which character types to include. Requires at least 2 types
    to be selected before returning.
    """
    while True:
        print("\nWhich character types should the password include?")
        print("  (answer y/n to each)")
        uppercase = input("  Uppercase letters (A-Z)? [y/n]: ").strip().lower() == "y"
        lowercase = input("  Lowercase letters (a-z)? [y/n]: ").strip().lower() == "y"
        numbers = input("  Numbers (0-9)? [y/n]: ").strip().lower() == "y"
        symbols = input("  Symbols (!@#$...)? [y/n]: ").strip().lower() == "y"

        selected_count = sum([uppercase, lowercase, numbers, symbols])
        if selected_count < 2:
            print("  Please select at least 2 character types.\n")
            continue

        return {
            "uppercase": uppercase,
            "lowercase": lowercase,
            "numbers": numbers,
            "symbols": symbols,
        }


def build_character_pool(types: dict) -> str:
    """Combine the selected character sets into one pool to sample from."""
    pool = ""
    if types["uppercase"]:
        pool += string.ascii_uppercase
    if types["lowercase"]:
        pool += string.ascii_lowercase
    if types["numbers"]:
        pool += string.digits
    if types["symbols"]:
        pool += "!@#$%^&*()-_=+[]{}"
    return pool


def generate_password(length: int, types: dict) -> str:
    """
    Generate a password of the given length using the selected character
    types. Guarantees at least one character from each selected type by
    seeding those first, then filling the rest randomly and shuffling.
    """
    pool = build_character_pool(types)

    guaranteed = []
    if types["uppercase"]:
        guaranteed.append(random.choice(string.ascii_uppercase))
    if types["lowercase"]:
        guaranteed.append(random.choice(string.ascii_lowercase))
    if types["numbers"]:
        guaranteed.append(random.choice(string.digits))
    if types["symbols"]:
        guaranteed.append(random.choice("!@#$%^&*()-_=+[]{}"))

    remaining_length = length - len(guaranteed)
    rest = [random.choice(pool) for _ in range(remaining_length)]

    password_chars = guaranteed + rest
    random.shuffle(password_chars)
    return "".join(password_chars)


def main() -> None:
    print("=" * 45)
    print("       Random Password Generator")
    print("=" * 45)

    while True:
        length = get_length()
        types = get_character_types()
        password = generate_password(length, types)

        print("\n" + "-" * 45)
        print(f"Generated password: {password}")
        print("-" * 45)

        again = input("\nGenerate another password? [y/n]: ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()
