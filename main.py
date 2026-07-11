import csv
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

FILENAME = "expenses.csv"
FIELDNAMES = ["date", "amount", "category", "description"]


def show_menu():
    print("\n" + "=" * 28)
    print("      EXPENSE TRACKER")
    print("=" * 28)
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
    print("-" * 28)


# ---------- Input validation helpers ----------

def get_valid_amount(prompt, current=None):
    """Keep asking until a positive number is entered.
    If current is given, an empty input keeps the current value (used for editing)."""
    while True:
        raw = input(prompt).strip()
        if current is not None and raw == "":
            return current
        try:
            value = float(raw)
            if value <= 0:
                print("Amount must be greater than 0. Try again.")
                continue
            return f"{value:.2f}"
        except ValueError:
            print("That's not a valid number. Try again (e.g. 250 or 99.99).")


def get_non_empty(prompt, current=None):
    """Keep asking until non-empty text is entered.
    If current is given, an empty input keeps the current value (used for editing)."""
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        if current is not None:
            return current
        print("This field can't be empty. Try again.")


# ---------- File I/O ----------

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
    """Load all expenses from the CSV file into a list of dicts.
    Skips rows that are missing fields or have a bad amount, so one
    corrupted line doesn't crash the whole program."""
    expenses = []
    if not os.path.isfile(FILENAME):
        return expenses

    skipped = 0
    with open(FILENAME, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not all(row.get(field) for field in FIELDNAMES):
                skipped += 1
                continue
            try:
                float(row["amount"])
            except (ValueError, TypeError):
                skipped += 1
                continue
            expenses.append(row)

    if skipped:
        print(f"Note: skipped {skipped} corrupted row(s) in {FILENAME}.")

    return expenses


# ---------- Core features ----------

def add_expense(expenses):
    amount = get_valid_amount("Enter amount: ")
    category = get_non_empty("Enter category (e.g. Food, Travel): ")
    description = get_non_empty("Enter description: ")
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
        print(f"{i}. {exp['date']} | ₹{float(exp['amount']):.2f} | {exp['category']} | {exp['description']}")


def get_valid_index(expenses, prompt):
    """Ask for a 1-based index, validate it, return 0-based index or None if cancelled."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            index = int(raw) - 1
        except ValueError:
            print("Please enter a valid number.")
            continue
        if 0 <= index < len(expenses):
            return index
        print(f"Please enter a number between 1 and {len(expenses)}.")


def delete_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return
    index = get_valid_index(expenses, "Enter the number of the expense to delete (blank to cancel): ")
    if index is None:
        print("Cancelled.")
        return
    removed = expenses.pop(index)
    print(f"Deleted: {removed['description']} (₹{float(removed['amount']):.2f})")
    save_all_expenses(expenses)


def edit_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return
    index = get_valid_index(expenses, "Enter the number of the expense to edit (blank to cancel): ")
    if index is None:
        print("Cancelled.")
        return

    exp = expenses[index]
    print("Leave blank to keep the current value.")

    exp["amount"] = get_valid_amount(f"Amount [{exp['amount']}]: ", current=exp["amount"])
    exp["category"] = get_non_empty(f"Category [{exp['category']}]: ", current=exp["category"])
    exp["description"] = get_non_empty(f"Description [{exp['description']}]: ", current=exp["description"])

    save_all_expenses(expenses)
    print("Expense updated!")


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
        try:
            choice = input("Choose an option (1-10): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

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