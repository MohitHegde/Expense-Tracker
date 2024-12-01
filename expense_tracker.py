import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from datetime import datetime
import csv
from collections import defaultdict

CSV_FILE = "expenses.csv"

# Function to add a new transaction
def add_transaction():
    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    trans_type = trans_type_var.get()
    description = description_entry.get()

    if not (date and category and amount and trans_type and description):
        messagebox.showerror("Input Error", "All fields are required.")
        return

    try:
        datetime.strptime(date, "%Y-%m-%d") 
        if trans_type not in ["Credit", "Debit"]:
            raise ValueError("Transaction type must be 'Credit' or 'Debit'.")

        # Ensure the CSV file exists with headers
        try:
            with open(CSV_FILE, "x") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Amount", "Type", "Description"])
        except FileExistsError:
            pass 

        # Append the transaction
        with open(CSV_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, category, amount, trans_type, description])
        
        messagebox.showinfo("Success", "Transaction added successfully!")
        clear_form()
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# Function to view transactions in a date range
def view_transactions():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        balance = 0
        transactions_in_range = []

        # Read CSV and collect transactions within the date range
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                transaction_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                if start_date <= transaction_date <= end_date:
                    amount = float(row["Amount"])
                    if row["Type"].lower() == "credit":
                        balance += amount
                    elif row["Type"].lower() == "debit":
                        balance -= amount
                    transactions_in_range.append(row)

        # Sort transactions by date
        transactions_in_range.sort(key=lambda x: x["Date"])

        # Display results
        transactions_list.delete(*transactions_list.get_children())
        for transaction in transactions_in_range:
            transactions_list.insert("", "end", values=(transaction["Date"], transaction["Category"], transaction["Amount"], transaction["Type"], transaction["Description"]))

        balance_label.config(text=f"Current Balance: {balance}")
    except FileNotFoundError:
        messagebox.showerror("File Error", "No transactions recorded yet.")
    except ValueError:
        messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD.")

def plot_category_spending():
    try:
        # Read transactions from CSV
        category_totals = defaultdict(float)
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Type"].lower() == "debit":
                    category_totals[row["Category"]] += float(row["Amount"])

        # Check if there's data to plot
        if not category_totals:
            messagebox.showinfo("No Data", "No spending data available to plot.")
            return

        # Prepare data for plotting
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())

        # Plot the graph
        plt.figure(figsize=(8, 6))
        plt.bar(categories, amounts, color="skyblue")
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Total Amount Spent")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        messagebox.showerror("File Error", "No transactions recorded yet.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def plot_daily_spending(start_date, end_date):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        daily_totals = defaultdict(float)
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                transaction_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                if start_date <= transaction_date <= end_date and row["Type"].lower() == "debit":
                    daily_totals[row["Date"]] += float(row["Amount"])

        if not daily_totals:
            messagebox.showinfo("No Data", "No spending data for this date range.")
            return

        # Prepare data for plotting
        dates = sorted(daily_totals.keys())
        amounts = [daily_totals[date] for date in dates]

        # Plot the graph
        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, marker="o", color="green", label="Daily Spending")
        plt.title("Daily Spending Trends")
        plt.xlabel("Date")
        plt.ylabel("Amount Spent")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.legend()
        plt.show()

    except FileNotFoundError:
        messagebox.showerror("File Error", "No transactions recorded yet.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to delete selected transaction
def delete_transaction():
    selected_item = transactions_list.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No transaction selected.")
        return

    try:
        transaction_data = transactions_list.item(selected_item, "values")
        date, category, amount, trans_type, description = transaction_data

        # Remove the transaction from the CSV file
        transactions = []
        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            transactions = [row for row in reader if row != list(transaction_data)]

        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(transactions)

        # Update the transaction list display
        transactions_list.delete(selected_item)
        messagebox.showinfo("Success", "Transaction deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Clear the input form
def clear_form():
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    trans_type_var.set("")
    description_entry.delete(0, tk.END)

# Tkinter window setup
root = tk.Tk()
root.title("Expense Tracker")

style = ttk.Style()
style.configure("TButton", padding=5, relief="flat", background="#87CEFA")
style.configure("TLabel", padding=5, background="#f0f0f0")
root.configure(bg="#f0f8ff")

# Add Transaction Section
tk.Label(root, text="Add Transaction", bg="#4682B4", fg="white", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(root, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="e")
date_entry = tk.Entry(root)
date_entry.grid(row=1, column=1)

tk.Label(root, text="Category:").grid(row=2, column=0, sticky="e")
category_entry = tk.Entry(root)
category_entry.grid(row=2, column=1)

tk.Label(root, text="Amount:").grid(row=3, column=0, sticky="e")
amount_entry = tk.Entry(root)
amount_entry.grid(row=3, column=1)

tk.Label(root, text="Type (Credit/Debit):").grid(row=4, column=0, sticky="e")
trans_type_var = tk.StringVar()
trans_type_menu = ttk.Combobox(root, textvariable=trans_type_var, values=["Credit", "Debit"])
trans_type_menu.grid(row=4, column=1)

tk.Label(root, text="Description:").grid(row=5, column=0, sticky="e")
description_entry = tk.Entry(root)
description_entry.grid(row=5, column=1)

tk.Button(root, text="Add Transaction", command=add_transaction).grid(row=6, column=0, columnspan=2, pady=10)

# View Transactions Section
tk.Label(root, text="View Transactions", bg="#4682B4", fg="white", font=("Arial", 16)).grid(row=7, column=0, columnspan=2, pady=10)

tk.Label(root, text="Start Date (YYYY-MM-DD):").grid(row=8, column=0, sticky="e")
start_date_entry = tk.Entry(root)
start_date_entry.grid(row=8, column=1)

tk.Label(root, text="End Date (YYYY-MM-DD):").grid(row=9, column=0, sticky="e")
end_date_entry = tk.Entry(root)
end_date_entry.grid(row=9, column=1)

tk.Button(root, text="View Transactions", command=view_transactions).grid(row=10, column=0, columnspan=2, pady=10)

# Transactions List
transactions_list = ttk.Treeview(root, columns=("Date", "Category", "Amount", "Type", "Description"), show="headings")
transactions_list.grid(row=11, column=0, columnspan=2)
for col in ("Date", "Category", "Amount", "Type", "Description"):
    transactions_list.heading(col, text=col)

tk.Button(root, text="Delete Transaction", command=delete_transaction).grid(row=12, column=0, columnspan=2, pady=10)
tk.Button(root, text="Plot Category Spending", command=plot_category_spending).grid(row=13, column=0, columnspan=2, pady=10)
tk.Button(root, text="Plot Daily Spending", command=lambda: plot_daily_spending("2024-01-01", "2024-12-31")).grid(row=14, column=0, columnspan=2, pady=10)

balance_label = tk.Label(root, text="Current Balance: 0", bg="#f0f8ff", font=("Arial", 12))
balance_label.grid(row=15, column=0, columnspan=2, pady=10)

root.mainloop()
