import csv
import os
from typing import List
from src.expense import Expense

class FileManager:
    def __init__(self, filename: str = 'data/expenses.csv'):
        self.filename = filename
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    def save_expenses(self, expenses: List[Expense]) -> bool:
        try:
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Category', 'Amount', 'Description'])
                for expense in expenses:
                    writer.writerow(expense.to_list())
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
    
    def load_expenses(self) -> List[Expense]:
        expenses = []
        if not os.path.exists(self.filename):
            return expenses
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    expense = Expense(
                        float(row['Amount']),
                        row['Category'],
                        row['Date'],
                        row['Description']
                    )
                    expenses.append(expense)
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
        return expenses
    
    def backup_data(self, backup_filename: str) -> bool:
        try:
            import shutil
            shutil.copy2(self.filename, f"reports/{backup_filename}")
            return True
        except Exception:
            return False
