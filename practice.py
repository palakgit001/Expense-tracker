name = input("Enter your name: ")
print("Hello",name)

expense = {"category": "Shopping", "amount": 1000, "date": "2026-07-07"}
print(expense["category"], expense["amount"])

expenses = []
expenses.append({"category": "Food", "amount": 250})
expenses.append({"category": "Travel", "amount": 100})
for e in expenses:
    print(e["category"], "-", e["amount"])

def add_expense(expenses, category, amount):
    expenses.append({"category": category, "amount": amount})
    return expenses

add_expense(expenses, "Grocery", 500)

expenses.append({"category ": "Shopping", "amount": 1000})
print(expenses)