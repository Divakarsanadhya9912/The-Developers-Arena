from typing import List, Dict
from collections import defaultdict
from src.expense import Expense
from datetime import datetime

class Reports:
    @staticmethod
    def total_expenses(expenses: List[Expense]) -> float:
        return sum(exp.amount for exp in expenses)
    
    @staticmethod
    def category_summary(expenses: List[Expense]) -> Dict[str, float]:
        summary = defaultdict(float)
        for exp in expenses:
            summary[exp.category] += exp.amount
        return dict(summary)
    
    @staticmethod
    def monthly_report(expenses: List[Expense], year_month: str) -> Dict:
        monthly = []
        for exp in expenses:
            if exp.date.startswith(year_month):
                monthly.append(exp)
        
        return {
            'total': Reports.total_expenses(monthly),
            'categories': Reports.category_summary(monthly),
            'count': len(monthly)
        }
    
    @staticmethod
    def print_category_summary(summary: Dict[str, float]):
        print("\n📊 CATEGORY-WISE SUMMARY:")
        print("-" * 50)
        for category, amount in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{category:20} ₹{amount:>10,.2f}")
