import csv
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

FILENAME = "expenses.csv"
FIELDNAMES = ["date", "amount", "category", "description"]


def show_menu():
    print("\n=== Expense Tracker ===")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Delete Expense")
    print("4. Edit Expense")
    print("5. Total Spending")
    print("6. Spending by Category")
    print("7. Spending by Month")
    print("8. Pie Chart (by Category)")
    print("9. Bar Chart (by Month)")
    print("10. Exit")


def save_expense(expense):
    """Append a single expense to the CSV file."""
    file_exists = os.path.isfile(FILENAME)
    with open(FILENAME, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(expense)


def save_all_expenses(expenses):
    """Rewrite the entire CSV file from the current expenses list."""
    with open(FILENAME, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


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
    date = datetime.now().strftime("%Y-%m-%d")  # auto-filled, e.g. 2026-07-10

    expense = {
        "date": date,
        "amount": amount,
        "category": category,
        "description": description
    }
    expenses.append(expense)
    save_expense(expense)
    print("Expense added!")


def view_expenses(expenses):
    if not expenses:
        print("No expenses yet.")
        return

    print("\n--- Your Expenses ---")
    for i, exp in enumerate(expenses, start=1):
        print(f"{i}. {exp['date']} | ₹{exp['amount']} | {exp['category']} | {exp['description']}")


def delete_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return
    try:
        index = int(input("Enter the number of the expense to delete: ")) - 1
        if 0 <= index < len(expenses):
            removed = expenses.pop(index)
            print(f"Deleted: {removed['description']} (₹{removed['amount']})")
            save_all_expenses(expenses)
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")


def edit_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return
    try:
        index = int(input("Enter the number of the expense to edit: ")) - 1
        if 0 <= index < len(expenses):
            exp = expenses[index]
            print("Leave blank to keep the current value.")

            new_amount = input(f"Amount [{exp['amount']}]: ")
            new_category = input(f"Category [{exp['category']}]: ")
            new_description = input(f"Description [{exp['description']}]: ")

            exp["amount"] = new_amount if new_amount else exp["amount"]
            exp["category"] = new_category if new_category else exp["category"]
            exp["description"] = new_description if new_description else exp["description"]

            save_all_expenses(expenses)
            print("Expense updated!")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")


def total_spending(expenses):
    """Sum of all expense amounts."""
    if not expenses:
        print("No expenses yet.")
        return
    total = sum(float(exp["amount"]) for exp in expenses)
    print(f"\nTotal spending: ₹{total:.2f}")


def spending_by_category(expenses):
    """Group and sum amounts by category."""
    if not expenses:
        print("No expenses yet.")
        return

    totals = defaultdict(float)
    for exp in expenses:
        totals[exp["category"]] += float(exp["amount"])

    print("\n--- Spending by Category ---")
    for category, amount in sorted(totals.items(), key=lambda x: -x[1]):
        print(f"{category}: ₹{amount:.2f}")


def spending_by_month(expenses):
    """Group and sum amounts by year-month (e.g. 2026-07)."""
    if not expenses:
        print("No expenses yet.")
        return

    totals = defaultdict(float)
    for exp in expenses:
        month = exp["date"][:7]  # "2026-07-10" -> "2026-07"
        totals[month] += float(exp["amount"])

    print("\n--- Spending by Month ---")
    for month, amount in sorted(totals.items()):
        print(f"{month}: ₹{amount:.2f}")


def chart_by_category(expenses):
    """Pie chart of spending by category."""
    if not expenses:
        print("No expenses yet.")
        return

    totals = defaultdict(float)
    for exp in expenses:
        totals[exp["category"]] += float(exp["amount"])

    categories = list(totals.keys())
    amounts = list(totals.values())

    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct="%1.1f%%")
    plt.title("Spending by Category")
    plt.show()


def chart_by_month(expenses):
    """Bar chart of spending by month."""
    if not expenses:
        print("No expenses yet.")
        return

    totals = defaultdict(float)
    for exp in expenses:
        month = exp["date"][:7]
        totals[month] += float(exp["amount"])

    months = sorted(totals.keys())
    amounts = [totals[m] for m in months]

    plt.figure(figsize=(8, 5))
    plt.bar(months, amounts, color="skyblue")
    plt.title("Spending by Month")
    plt.xlabel("Month")
    plt.ylabel("Amount (₹)")
    plt.show()


def main():
    expenses = load_expenses()

    while True:
        show_menu()
        choice = input("Choose an option (1-10): ")

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            delete_expense(expenses)
        elif choice == "4":
            edit_expense(expenses)
        elif choice == "5":
            total_spending(expenses)
        elif choice == "6":
            spending_by_category(expenses)
        elif choice == "7":
            spending_by_month(expenses)
        elif choice == "8":
            chart_by_category(expenses)
        elif choice == "9":
            chart_by_month(expenses)
        elif choice == "10":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1-10.")


if __name__ == "__main__":
    main()