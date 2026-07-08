def show_menu():
    print("\n=== Expense Tracker ===")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Exit")

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
    print("Expense added!")

def view_expenses(expenses):
    if not expenses:
        print("No expenses yet.")
        return

    print("\n--- Your Expenses ---")
    for i, exp in enumerate(expenses, start=1):
        print(f"{i}. ₹{exp['amount']} | {exp['category']} | {exp['description']}")

def main():
    expenses = []  # this list lives only while the program runs

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