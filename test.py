import random
from datetime import datetime
from collections import defaultdict

users = [2, 10, 11, 12, 14]
expense_items = range(1, 11)  # 1 to 10
years = [2022, 2023, 2024]
months = list(range(1, 12))  # First 11 months

# Generate expenses and group them by month
def generate_monthly_expenses(num_expenses):
    monthly_expenses = defaultdict(list)  # Group expenses by Year-Month
    expense_queries = []

    for _ in range(num_expenses):
        user_id = random.choice(users)
        item_id = random.choice(expense_items)
        year = random.choice(years)
        month = random.choice(months)
        day = random.randint(1, 28)  # Ensuring valid days for all months
        expense_date = datetime(year, month, day).strftime('%Y-%m-%d')
        expense_amount = round(random.uniform(10.0, 500.0), 2)  # Random expense amount between 10 and 500

        # Add to expense queries
        expense_query = (
            f"INSERT INTO expense (user_id, item_id, amount, date) "
            f"VALUES ({user_id}, {item_id}, {expense_amount}, '{expense_date}');"
        )
        expense_queries.append(expense_query)

        # Add to monthly group
        year_month = f"{year}-{month:02d}"  # Format as YYYY-MM
        monthly_expenses[year_month].append(expense_amount)

    return expense_queries, monthly_expenses

# Generate income queries based on monthly expenses split among users
def generate_income_queries(monthly_expenses):
    income_queries = []

    for year_month, expenses in monthly_expenses.items():
        total_expense = sum(expenses)
        per_user_expense = total_expense / len(users)  # Divide total expense equally among users

        for user_id in users:
            income_amount = round(per_user_expense + random.uniform(-5.0, 5.0), 2)  # ±5 for individual user
            income_date = f"{year_month}-01"  # Use the first day of the month
            income_query = (
                f"INSERT INTO income (user_id, source_id, amount, date) "
                f"VALUES ({user_id}, 1, {income_amount}, '{income_date}');"
            )
            income_queries.append(income_query)

    return income_queries

# Generate data
expense_queries, monthly_expenses = generate_monthly_expenses(100)  # Generate 500 expense entries
income_queries = generate_income_queries(monthly_expenses)

# Print the first 5 queries from each
print("Expense Queries:")
for query in expense_queries:
    print(query)

print("\nIncome Queries:")
for query in income_queries:  # Show income queries for first 2 months
    print(query)

