import csv
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

FILENAME = "expenses.csv"
FIELDNAMES = ["date", "amount", "category", "description"]

BUDGET_FILENAME = "budgets.csv"
BUDGET_FIELDNAMES = ["month", "budget"]
BUDGET_WARNING_THRESHOLD = 0.9  # warn once spending hits 90% of budget


# Displays the main menu with all available options
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
    print("10. Set Monthly Budget")
    print("11. Exit")
    print("-" * 28)


# ---------- Input validation helpers ----------

def get_valid_amount(prompt, current=None):
    """Keep asking until a positive number is entered.
    If current is given, an empty input keeps the current value (used for editing)."""
    while True:
        raw = input(prompt).strip()
        # Editing mode: blank input means "don't change this field"
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
            writer.writeheader()  # only write header once, on first-ever save
        writer.writerow(expense)


def save_all_expenses(expenses):
    """Rewrite the entire CSV file from the current expenses list.
    Used after edit/delete since those change existing rows, not just append."""
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
            # Skip rows missing any required field
            if not all(row.get(field) for field in FIELDNAMES):
                skipped += 1
                continue
            # Skip rows where amount isn't a valid number
            try:
                float(row["amount"])
            except (ValueError, TypeError):
                skipped += 1
                continue
            expenses.append(row)

    if skipped:
        print(f"Note: skipped {skipped} corrupted row(s) in {FILENAME}.")

    return expenses


# ---------- Budget storage ----------

def load_budgets():
    """Load budgets from CSV into a dict: {'2026-07': 5000.0, ...}."""
    budgets = {}
    if not os.path.isfile(BUDGET_FILENAME):
        return budgets

    with open(BUDGET_FILENAME, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                budgets[row["month"]] = float(row["budget"])
            except (ValueError, TypeError, KeyError):
                continue  # skip corrupted budget rows silently
    return budgets


def save_budgets(budgets):
    """Rewrite the entire budgets CSV file from the current dict."""
    with open(BUDGET_FILENAME, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=BUDGET_FIELDNAMES)
        writer.writeheader()
        for month, budget in sorted(budgets.items()):
            writer.writerow({"month": month, "budget": f"{budget:.2f}"})


def set_budget(budgets):
    """Prompt the user to set (or update) a budget for a given month."""
    default_month = datetime.now().strftime("%Y-%m")
    raw_month = input(f"Enter month as YYYY-MM [{default_month}]: ").strip()
    month = raw_month if raw_month else default_month

    # Validate the month format before saving anything
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month format. Please use YYYY-MM (e.g. 2026-07). Budget not set.")
        return

    amount = get_valid_amount(f"Enter budget for {month}: ₹")
    budgets[month] = float(amount)
    save_budgets(budgets)
    print(f"Budget for {month} set to ₹{float(amount):.2f}")


def check_budget_status(expenses, budgets, month):
    """Print a warning if spending for the given month is close to or over budget.
    Called automatically after adding a new expense."""
    if month not in budgets:
        return  # no budget set for this month, nothing to check

    # Sum only the expenses that fall in the given month
    spent = sum(
        float(exp["amount"]) for exp in expenses if exp["date"][:7] == month
    )
    budget = budgets[month]

    if budget <= 0:
        return

    ratio = spent / budget
    if spent > budget:
        print(f"⚠ Over budget for {month}! Spent ₹{spent:.2f} of ₹{budget:.2f} budget.")
    elif ratio >= BUDGET_WARNING_THRESHOLD:
        print(f"⚠ Heads up: you've used {ratio * 100:.0f}% of your {month} budget "
              f"(₹{spent:.2f} of ₹{budget:.2f}).")


# ---------- Core features ----------

# Prompts for expense details, saves it, and checks budget status for that month
def add_expense(expenses, budgets):
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

    check_budget_status(expenses, budgets, date[:7])


# Prints a numbered list of all expenses
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
            return None  # user chose to cancel
        try:
            index = int(raw) - 1
        except ValueError:
            print("Please enter a valid number.")
            continue
        if 0 <= index < len(expenses):
            return index
        print(f"Please enter a number between 1 and {len(expenses)}.")


# Removes an expense chosen by the user and rewrites the CSV
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


# Lets the user update an existing expense's amount, category, or description
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
    for category, amount in sorted(totals.items(), key=lambda x: -x[1]):  # highest spend first
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


# Builds and displays a pie chart of spending grouped by category
def chart_by_category(expenses):
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


# Builds and displays a bar chart of spending grouped by month
def chart_by_month(expenses):
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


# Main program loop: loads saved data, shows the menu, and routes user choices
def main():
    expenses = load_expenses()
    budgets = load_budgets()

    while True:
        show_menu()
        try:
            choice = input("Choose an option (1-11): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if choice == "1":
            add_expense(expenses, budgets)
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
            set_budget(budgets)
        elif choice == "11":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1-11.")


if __name__ == "__main__":
    main()