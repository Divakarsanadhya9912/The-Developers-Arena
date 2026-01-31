from datetime import datetime
from typing import Optional

class Expense:
    def __init__(self, amount: float, category: str, date: str, description: str):
        self.amount = amount
        self.category = category.strip().title()
        self.date = date
        self.description = description.strip()
    
    def __str__(self) -> str:
        return f"{self.date} | {self.category}: ₹{self.amount:,.2f} - {self.description}"
    
    def to_list(self) -> list:
        return [self.date, self.category, self.amount, self.description]
