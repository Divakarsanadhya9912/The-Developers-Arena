import re
from datetime import datetime
from typing import Optional

def validate_amount(amount_str: str) -> Optional[float]:
    try:
        amount = float(amount_str)
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None

def validate_date(date_str: str) -> Optional[str]:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        return None

def get_valid_input(prompt: str, validator=None) -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            print("❌ Input cannot be empty!")
            continue
        if validator and not validator(value):
            print("❌ Invalid input! Please try again.")
            continue
        return value

def clear_screen():
    print("\n" * 50)
