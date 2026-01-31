from typing import List
from src.expense import Expense
from src.utils import get_valid_input, validate_amount, validate_date, clear_screen
from src.file_manager import FileManager
from src.reports import Reports

class Menu:
    def __init__(self):
        self.file_manager = FileManager()
        self.expenses: List[Expense] = self.file_manager.load_expenses()
        self.categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Other']
    
    def display_main_menu(self):
        print("\n" + "="*60)
        print("           🏦 PERSONAL FINANCE MANAGER 🏦")
        print("="*60)
        print("1.  ➕ Add New Expense")
        print("2.  📋 View All Expenses")
        print("3.  📊 Category-wise Summary")
        print("4.  📅 Monthly Report")
        print("5.  🔍 Search Expenses")
        print("6.  💾 Backup Data")
        print("7.  ❌ Exit")
        print("-"*60)
    
    def add_expense(self):
        print("\n➕ ADD NEW EXPENSE")
        print("-" * 30)
        
        amount = get_valid_input("Enter amount: ₹", validate_amount)
        print("\nCategories:", ", ".join(self.categories))
        category = get_valid_input("Enter category: ").title()
        if category not in self.categories:
            category = 'Other'
        
        date = get_valid_input("Enter date (YYYY-MM-DD): ", validate_date)
        description = get_valid_input("Enter description: ")
        
        expense = Expense(float(amount), category, date, description)
        self.expenses.append(expense)
        
        if self.file_manager.save_expenses(self.expenses):
            print("\n✅ Expense added successfully!")
        input("\nPress Enter to continue...")
    
    def view_expenses(self):
        if not self.expenses:
            print("\n📭 No expenses recorded yet!")
            input("Press Enter to continue...")
            return
        
        print("\n📋 ALL EXPENSES")
        print("-" * 70)
        for i, expense in enumerate(self.expenses[-10:], 1):  # Show last 10
            print(f"{i:2d}. {expense}")
        print(f"\nTotal expenses: {len(self.expenses)} records")
        input("\nPress Enter to continue...")
    
    def category_summary(self):
        if not self.expenses:
            print("\n📭 No data available!")
            return
        
        summary = Reports.category_summary(self.expenses)
        Reports.print_category_summary(summary)
        print(f"\n💰 TOTAL: ₹{Reports.total_expenses(self.expenses):,.2f}")
        input("\nPress Enter to continue...")
    
    def monthly_report(self):
        year_month = get_valid_input("Enter year-month (YYYY-MM): ")
        report = Reports.monthly_report(self.expenses, year_month)
        
        if report['count'] == 0:
            print("📅 No expenses found for this period.")
        else:
            print(f"\n📅 {year_month} REPORT")
            print("-" * 30)
            Reports.print_category_summary(report['categories'])
            print(f"\n💰 MONTH TOTAL: ₹{report['total']:,.2f} ({report['count']} transactions)")
        input("\nPress Enter to continue...")
    
    def search_expenses(self):
        keyword = get_valid_input("Enter search keyword: ").lower()
        matches = [e for e in self.expenses if keyword in e.description.lower() or keyword in e.category.lower()]
        
        if not matches:
            print("🔍 No matching expenses found.")
        else:
            print(f"\n🔍 FOUND {len(matches)} MATCHES:")
            print("-" * 50)
            for expense in matches[:10]:
                print(expense)
        input("\nPress Enter to continue...")
    
    def backup_data(self):
        backup_name = f"backup_datetime.now().strftime('%Y%m%d_%H%M%S').csv"
        if self.file_manager.backup_data(backup_name):
            print(f"✅ Backup created: reports/{backup_name}")
        else:
            print("❌ Backup failed!")
        input("\nPress Enter to continue...")
    
    def run(self):
        while True:
            clear_screen()
            self.display_main_menu()
            
            choice = get_valid_input("Enter your choice (1-7): ")
            if choice == '1':
                self.add_expense()
            elif choice == '2':
                self.view_expenses()
            elif choice == '3':
                self.category_summary()
            elif choice == '4':
                self.monthly_report()
            elif choice == '5':
                self.search_expenses()
            elif choice == '6':
                self.backup_data()
            elif choice == '7':
                print("\n👋 Thank you for using Personal Finance Manager!")
                break
            else:
                print("❌ Invalid choice! Please select 1-7.")
                input("Press Enter to continue...")
