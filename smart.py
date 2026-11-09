import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

#  DATABASE:-

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    transaction_type TEXT,
    category TEXT,
    amount REAL,
    description TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    name TEXT PRIMARY KEY,
    value REAL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO settings (name, value)
VALUES ('monthly_budget', 5000)
""")

conn.commit()


# MAIN WINDOW:- 

root = tk.Tk()
root.title("Smart Expense Tracker for Students")
root.geometry("950x650")
root.configure(bg="#f0f4f8")

budget = tk.DoubleVar(value=5000)

title = tk.Label(
    root,
    text="SMART EXPENSE TRACKER",
    font=("Arial", 22, "bold"),
    bg="#17365d",
    fg="white",
    pady=15
)
title.pack(fill="x")


# SUMMARY :-

summary_frame = tk.Frame(root, bg="#f0f4f8")
summary_frame.pack(pady=15)

income_label = tk.Label(
    summary_frame, text="Income: ₹0",
    font=("Arial", 13, "bold"), bg="#d9ead3",
    width=20, pady=12
)
income_label.grid(row=0, column=0, padx=8)

expense_label = tk.Label(
    summary_frame, text="Expenses: ₹0",
    font=("Arial", 13, "bold"), bg="#f4cccc",
    width=20, pady=12
)
expense_label.grid(row=0, column=1, padx=8)

balance_label = tk.Label(
    summary_frame, text="Balance: ₹0",
    font=("Arial", 13, "bold"), bg="#cfe2f3",
    width=20, pady=12
)
balance_label.grid(row=0, column=2, padx=8)


#INPUT FORM :-

form = tk.LabelFrame(
    root,
    text="Add New Transaction",
    font=("Arial", 12, "bold"),
    bg="#f0f4f8",
    padx=15,
    pady=10
)
form.pack(fill="x", padx=20, pady=5)

tk.Label(form, text="Type:", bg="#f0f4f8").grid(
    row=0, column=0, padx=5, pady=8
)

type_box = ttk.Combobox(
    form, values=["Income", "Expense"],
    state="readonly", width=15
)
type_box.set("Expense")
type_box.grid(row=0, column=1, padx=5)

tk.Label(form, text="Category:", bg="#f0f4f8").grid(
    row=0, column=2, padx=5
)

category_box = ttk.Combobox(
    form,
    values=[
        "Pocket Money", "Food", "Hostel","mobile recharge",
        "Travel", "Books", "Shopping", "Other"
    ],
    state="readonly",
    width=15
)
category_box.set("Food")
category_box.grid(row=0, column=3, padx=5)

tk.Label(form, text="Amount (₹):", bg="#f0f4f8").grid(
    row=1, column=0, padx=5, pady=8
)

amount_entry = tk.Entry(form, width=18)
amount_entry.grid(row=1, column=1, padx=5)

tk.Label(form, text="Description:", bg="#f0f4f8").grid(
    row=1, column=2, padx=5
)

description_entry = tk.Entry(form, width=18)
description_entry.grid(row=1, column=3, padx=5)


# BUDGET:-

budget_frame = tk.Frame(root, bg="#f0f4f8")
budget_frame.pack(pady=8)

tk.Label(
    budget_frame,
    text="Monthly Budget (₹):",
    font=("Arial", 11),
    bg="#f0f4f8"
).pack(side="left", padx=5)

budget_entry = tk.Entry(budget_frame, width=12)
budget_entry.pack(side="left", padx=5)


def load_budget():
    cursor.execute(
        "SELECT value FROM settings WHERE name = 'monthly_budget'"
    )
    result = cursor.fetchone()

    if result:
        budget.set(result[0])

    budget_entry.delete(0, tk.END)
    budget_entry.insert(0, str(budget.get()))


def save_budget():
    try:
        new_budget = float(budget_entry.get())

        if new_budget < 0:
            raise ValueError

        budget.set(new_budget)

        cursor.execute("""
            UPDATE settings
            SET value = ?
            WHERE name = 'monthly_budget'
        """, (new_budget,))

        conn.commit()
        refresh_data()

        messagebox.showinfo(
            "Success", "Monthly budget updated!"
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid non-negative budget."
        )


tk.Button(
    budget_frame,
    text="Save Budget",
    command=save_budget,
    bg="#17365d",
    fg="white"
).pack(side="left", padx=5)


# ADD TRANSACTION:-

def add_transaction():
    transaction_type = type_box.get()
    category = category_box.get()
    description = description_entry.get().strip()

    try:
        amount = float(amount_entry.get())

        if amount <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Error", "Enter a valid amount greater than zero."
        )
        return

    if not category:
        messagebox.showerror(
            "Error", "Please select a category."
        )
        return

    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO transactions
        (date, transaction_type, category, amount, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        date,
        transaction_type,
        category,
        amount,
        description
    ))

    conn.commit()

    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

    refresh_data()

    messagebox.showinfo(
        "Success", "Transaction added successfully!"
    )


tk.Button(
    form,
    text="Add Transaction",
    command=add_transaction,
    bg="#198754",
    fg="white",
    font=("Arial", 10, "bold")
).grid(row=2, column=1, columnspan=2, pady=10)


#TRANSACTION TABLE :-

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = (
    "ID", "Date", "Type",
    "Category", "Amount", "Description"
)

table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=120, anchor="center")

table.column("ID", width=45)
table.column("Description", width=200)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)

table.configure(yscrollcommand=scrollbar.set)

table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


#  REFRESH DATA:- 

def refresh_data():
    for row in table.get_children():
        table.delete(row)

    cursor.execute("""
        SELECT id, date, transaction_type,
               category, amount, description
        FROM transactions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    total_income = 0
    total_expenses = 0

    current_month = datetime.now().strftime("%Y-%m")

    for row in rows:
        table.insert("", "end", values=row)

        transaction_date = row[1]
        transaction_type = row[2]
        amount = row[4]

        # Calculate totals for the current month only.
        if transaction_date.startswith(current_month):
            if transaction_type == "Income":
                total_income += amount
            else:
                total_expenses += amount

    balance = total_income - total_expenses

    income_label.config(
        text=f"Monthly Income: ₹{total_income:.2f}"
    )

    expense_label.config(
        text=f"Monthly Expenses: ₹{total_expenses:.2f}"
    )

    balance_label.config(
        text=f"Balance: ₹{balance:.2f}"
    )

    if total_expenses > budget.get():
        messagebox.showwarning(
            "Budget Alert",
            "Your monthly expenses have exceeded your budget!"
        )


# DELETE TRANSACTION :-

def delete_transaction():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning", "Select a transaction to delete."
        )
        return

    confirmed = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this transaction?"
    )

    if confirmed:
        for item in selected:
            values = table.item(item, "values")
            transaction_id = values[0]

            cursor.execute(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,)
            )

        conn.commit()
        refresh_data()


tk.Button(
    root,
    text="Delete Selected Transaction",
    command=delete_transaction,
    bg="#cc0000",
    fg="white",
    font=("Arial", 10, "bold")
).pack(pady=5)


#  START APPLICATION:-

load_budget()
refresh_data()

root.mainloop()

conn.close()