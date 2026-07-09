import csv
import os

FILENAME = "expenses.csv"
FIELDNAMES = ["amount", "category", "description"]


def show_menu():
    print("\n=== Expense Tracker ===")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Exit")


def save_expense(expense):
    """Append a single expense to the CSV file."""
    file_exists = os.path.isfile(FILENAME)
    with open(FILENAME, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(expense)


def load_expenses():
    """Load all expenses from the CSV file into a list of dicts."""
    expenses = []
    if not os.path.isfile(FILENAME):
        return expenses

    with open(FILENAME, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expenses.append(row)
    return expenses


def add_expense(expenses):
    amount = input("Enter amount: ")
    category = input("Enter category (e.g. Food, Travel): ")
    description = input("Enter description: ")

    expense = {
        "amount": amount,
        "category": category,
        "description": description
    }
    expenses.append(expense)
    save_expense(expense)  # NEW: write it to disk immediately
    print("Expense added!")


def view_expenses(expenses):
    if not expenses:
        print("No expenses yet.")
        return

    print("\n--- Your Expenses ---")
    for i, exp in enumerate(expenses, start=1):
        print(f"{i}. ₹{exp['amount']} | {exp['category']} | {exp['description']}")


def main():
    expenses = load_expenses()  # NEW: load whatever was saved last time

    while True:
        show_menu()
        choice = input("Choose an option (1-3): ")

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()