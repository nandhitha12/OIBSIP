"""
BMI Calculator — OIBSIP Task 2 (Beginner Tier)
Author: Nandhitha Reddy

A command-line tool that calculates Body Mass Index (BMI) from user-entered
weight and height, then classifies the result into a standard health
category.

Formula:
    BMI = weight (kg) / height (m) ** 2

Categories:
    < 18.5        Underweight
    18.5 - 24.9   Normal
    25 - 29.9     Overweight
    >= 30         Obese

Run:
    python bmi_cli.py
"""


def get_positive_float(prompt: str) -> float:
    """
    Repeatedly ask the user for a number until they give a valid,
    positive value. Rejects non-numeric input and negative/zero values
    with a helpful message instead of crashing.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print(f"  '{raw}' isn't a valid number. Please enter digits only, "
                  f"e.g. 68.5")
            continue

        if value <= 0:
            print("  Please enter a positive number greater than zero.")
            continue

        return value


def classify_bmi(bmi: float) -> str:
    """Return the standard health category for a given BMI value."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """BMI = weight (kg) / height (m) squared."""
    return weight_kg / (height_m ** 2)


def main() -> None:
    print("=" * 40)
    print("        BMI Calculator")
    print("=" * 40)

    weight = get_positive_float("Enter your weight in kg: ")
    height = get_positive_float("Enter your height in m (e.g. 1.70): ")

    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)

    print("-" * 40)
    print(f"Your BMI is: {bmi:.2f}")
    print(f"Category:    {category}")
    print("-" * 40)


if __name__ == "__main__":
    main()
