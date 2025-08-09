import json
from datetime import datetime
import os

EXPENSE_FILE = "expenses.json"

def _load_expenses():
    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "r") as f:
            return json.load(f)
    return []

def _save_expenses(expenses):
    with open(EXPENSE_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

def log_expense(amount, category, note=""):
    """
    Logs a new expense with current timestamp.
    """
    expenses = _load_expenses()
    entry = {
        "amount": float(amount),
        "category": category,
        "note": note,
        "timestamp": datetime.now().isoformat()
    }
    expenses.append(entry)
    _save_expenses(expenses)
    return entry

def get_total_expense():
    """
    Returns the total amount spent.
    """
    expenses = _load_expenses()
    return sum(e["amount"] for e in expenses)

def list_expenses(limit=None):
    """
    Lists all logged expenses. Optional limit for recent entries.
    """
    expenses = _load_expenses()
    if limit:
        return expenses[-limit:]
    return expenses

def filter_expenses(category=None, date=None):
    """
    Filters expenses by category or date (YYYY-MM-DD).
    """
    expenses = _load_expenses()
    result = expenses
    if category:
        result = [e for e in result if e["category"].lower() == category.lower()]
    if date:
        result = [e for e in result if e["timestamp"].startswith(date)]
    return result
