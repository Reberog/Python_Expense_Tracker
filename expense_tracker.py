#!/usr/bin/env python3

import csv
import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
import uuid

class ExpenseManager:
    def __init__(self, data_file: str = "expenses.json"):
        self.data_file = data_file
        self.expenses = []
        self.load_expenses()
    
    def load_expenses(self) -> None:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.expenses = []
        else:
            self.expenses = []
    
    def save_expenses(self) -> bool:
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.expenses, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving expenses: {e}")
            return False
    
    def add_expense(self, amount: float, category: str, description: str, expense_date: str = None) -> Dict:
        if expense_date is None:
            expense_date = date.today().isoformat()
        
        expense = {
            "id": str(uuid.uuid4())[:8],
            "amount": float(amount),
            "category": category.strip(),
            "description": description.strip(),
            "date": expense_date,
            "created_at": datetime.now().isoformat()
        }
        
        self.expenses.append(expense)
        return expense
    
    def get_all_expenses(self) -> List[Dict]:
        return sorted(self.expenses, key=lambda x: x['created_at'], reverse=True)
    
    def get_expenses_by_category(self, category: str) -> List[Dict]:
        return [exp for exp in self.expenses if exp['category'].lower() == category.lower()]
    
    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        return [exp for exp in self.expenses 
                if start_date <= exp['date'] <= end_date]
    
    def delete_expense(self, expense_id: str) -> bool:
        original_length = len(self.expenses)
        self.expenses = [exp for exp in self.expenses if exp['id'] != expense_id]
        return len(self.expenses) < original_length
    
    def get_summary(self) -> Dict:
        if not self.expenses:
            return {
                "total": 0,
                "count": 0,
                "average": 0,
                "categories": {}
            }
        
        total = sum(exp['amount'] for exp in self.expenses)
        count = len(self.expenses)
        
        categories = {}
        for exp in self.expenses:
            cat = exp['category']
            categories[cat] = categories.get(cat, 0) + exp['amount']
        
        return {
            "total": total,
            "count": count,
            "average": total / count if count > 0 else 0,
            "categories": categories
        }
    
    def get_categories(self) -> List[str]:
        categories = set(exp['category'] for exp in self.expenses)
        return sorted(list(categories))
    
    def validate_expense(self, amount: str, category: str, description: str) -> List[str]:
        errors = []
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                errors.append("Amount must be positive")
        except ValueError:
            errors.append("Amount must be a valid number")
        
        if not category.strip():
            errors.append("Category is required")
        
        if not description.strip():
            errors.append("Description is required")
        
        return errors

class ExpenseTrackerCLI:
    def __init__(self):
        self.manager = ExpenseManager()
    
    def print_header(self, title: str):
        print("\n" + "="*50)
        print(f"  {title}  ")
        print("="*50)
    
    def add_expense_interactive(self):
        self.print_header("Add Expense")
        
        print("How would you like to add expenses?")
        print("  1. Add manually")
        print("  2. Add from CSV file")
        print("  3. Back to main menu")
        
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                self.add_expense_manually()
            elif choice == '2':
                filename = input("Enter CSV filename to add from: ").strip()
                if filename:
                    self.import_expenses(filename)
                else:
                    print("Filename is required for adding from CSV")
            elif choice == '3':
                return
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled")
        except Exception as e:
            print(f"Error: {e}")

    def add_expense_manually(self):
        self.print_header("Add Expense Manually")
        
        try:
            amount = input("Enter amount (₹): ").strip()
            category = input("Enter category: ").strip()
            description = input("Enter description: ").strip()
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            
            if not date_input:
                date_input = date.today().isoformat()
            
            # Validate
            errors = self.manager.validate_expense(amount, category, description)
            if errors:
                print("Validation errors:")
                for error in errors:
                    print(f"  - {error}")
                return
            
            # Add expense
            expense = self.manager.add_expense(float(amount), category, description, date_input)
            
            if self.manager.save_expenses():
                print(" Expense added successfully!")
                self.print_expense_details(expense)
            else:
                print(" Failed to save expense")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled")
        except Exception as e:
            print(f"Error: {e}")

    def print_expense_details(self, expense: Dict):
        print(f"  ID: {expense['id']}")
        print(f"  Amount: ₹{expense['amount']:.2f}")
        print(f"  Category: {expense['category']}")
        print(f"  Description: {expense['description']}")
        print(f"  Date: {expense['date']}")
    
    def list_expenses(self, category: str = None, start_date: str = None, end_date: str = None):
        expenses = self.manager.get_all_expenses()
        
        # Apply filters
        if category:
            expenses = [exp for exp in expenses if exp['category'].lower() == category.lower()]
        
        if start_date and end_date:
            expenses = [exp for exp in expenses if start_date <= exp['date'] <= end_date]
        
        if not expenses:
            print("No expenses found.")
            return
        
        self.print_header("View Expenses")
        
        for i, expense in enumerate(expenses, 1):
            print(f"\n{i}. {expense['description']}")
            print(f"   ID: {expense['id']}")
            print(f"   Amount: ₹{expense['amount']:.2f}")
            print(f"   Category: {expense['category']}")
            print(f"   Date: {expense['date']}")
            print(f"   Created: {expense['created_at'][:10]}")
        
        # Add delete option if there are expenses
        if len(expenses) > 0:
            print("\nOptions:")
            print("  1. Delete an expense")
            print("  2. Back to main menu")
            
            try:
                choice = input("\nEnter your choice (1-2): ").strip()
                if choice == '1':
                    self.delete_expense()
                elif choice == '2':
                    return
                else:
                    print("Invalid choice.")
            except KeyboardInterrupt:
                print("\nOperation cancelled")
    
    def show_summary(self):
        summary = self.manager.get_summary()
        
        self.print_header("Track Budget")
        
        print(f"Total Expenses: ₹{summary['total']:.2f}")
        print(f"Number of Expenses: {summary['count']}")
        print(f"Average Expense: ₹{summary['average']:.2f}")
        
        if summary['categories']:
            print(f"\nBy Category:")
            for category, total in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True):
                percentage = (total / summary['total'] * 100) if summary['total'] > 0 else 0
                print(f"  {category}: ₹{total:.2f} ({percentage:.1f}%)")
    
    def list_categories(self):
        categories = self.manager.get_categories()
        
        if not categories:
            print("No categories found.")
            return
        
        self.print_header("Categories")
        
        for category in categories:
            count = len(self.manager.get_expenses_by_category(category))
            total = sum(exp['amount'] for exp in self.manager.get_expenses_by_category(category))
            print(f"  {category}: {count} expenses, ₹{total:.2f}")
    
    def delete_expense(self, expense_id: str = None):
        if not expense_id:
            # Interactive deletion
            expenses = self.manager.get_all_expenses()
            if not expenses:
                print("No expenses found.")
                return

            self.print_header("Delete Expense")
            print("Available expenses:")
            
            for i, expense in enumerate(expenses[:10], 1):  # Show only first 10
                print(f"  {i}. {expense['description']} - ₹{expense['amount']:.2f} ({expense['date']}) [ID: {expense['id']}]")
            
            try:
                expense_id = input("\nEnter expense ID to delete: ").strip()
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return
        
        if self.manager.delete_expense(expense_id):
            if self.manager.save_expenses():
                print("Expense deleted successfully!")
            else:
                print(" Failed to save changes")
        else:
            print(" Expense not found")

    def export_expenses(self, filename: str = None):
        if not filename:
            filename = f"expenses_export_{date.today().isoformat()}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if not self.manager.expenses:
                    print("No expenses to save")
                    return
                
                fieldnames = ['id', 'amount', 'category', 'description', 'date', 'created_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for expense in self.manager.expenses:
                    writer.writerow(expense)
            
            print(f"Expenses saved to {filename}")
        except Exception as e:
            print(f" Save failed: {e}")

    def import_expenses(self, filename: str):
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                imported_expenses = []
                
                for row in reader:
                    # Validate required fields
                    if not all(key in row for key in ['id', 'amount', 'category', 'description', 'date']):
                        print(" Invalid CSV format - missing required columns")
                        return
                    
                    # Convert amount to float and validate
                    try:
                        amount = float(row['amount'])
                        if amount <= 0:
                            print(f" Skipping invalid amount: {row['amount']}")
                            continue
                    except ValueError:
                        print(f" Skipping invalid amount: {row['amount']}")
                        continue
                    
                    # Create expense with proper data types
                    expense = {
                        'id': row['id'],
                        'amount': amount,
                        'category': row['category'].strip(),
                        'description': row['description'].strip(),
                        'date': row['date'],
                        'created_at': row.get('created_at', datetime.now().isoformat())
                    }
                    imported_expenses.append(expense)
            
            if not imported_expenses:
                print("No valid expenses found in CSV file")
                return
            
            original_count = len(self.manager.expenses)
            self.manager.expenses.extend(imported_expenses)
            
            if self.manager.save_expenses():
                new_count = len(imported_expenses)
                print(f"Added {new_count} expenses successfully!")
            else:
                print(" Failed to save imported expenses")

        except FileNotFoundError:
            print(f" File '{filename}' not found")
        except csv.Error as e:
            print(f" CSV file error: {e}")
        except Exception as e:
            print(f" Import failed: {e}")

    def interactive_mode(self):
        while True:
            self.print_header("Personal Expense Tracker")
            
            print("What would you like to do?")
            print("  1. Add expense")
            print("  2. View expenses")
            print("  3. Track budget")
            print("  4. Save expenses")
            print("  5. Exit")
            
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    self.add_expense_interactive()
                elif choice == '2':
                    self.list_expenses()
                elif choice == '3':
                    self.show_summary()
                elif choice == '4':
                    filename = input("Enter CSV filename to save to (or press Enter for default): ").strip()
                    self.export_expenses(filename if filename else None)
                elif choice == '5':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")

                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    cli = ExpenseTrackerCLI()
    cli.interactive_mode()

if __name__ == "__main__":
    main()
