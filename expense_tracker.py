import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class ExpenseTrackerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Personal Expenses Tracker")
    self.root.geometry("700x500")

    # Initialize Database Connection
    self.conn = sqlite3.connect("expenses.db")
    self.cursor = self.conn.cursor()
    self.create_table()

    # Form Frame
    form_frame = tk.LabelFrame(
        self.root, text="Add New Expense", padx=10, pady=10
    )
    form_frame.pack(fill="x", padx=15, pady=10)

    # Date Label & Entry
    tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(
        row=0, column=0, sticky="w", pady=5
    )
    self.date_entry = tk.Entry(form_frame)
    self.date_entry.grid(row=0, column=1, padx=5, pady=5)

    # Category Label & Entry
    tk.Label(form_frame, text="Category:").grid(
        row=0, column=2, sticky="w", pady=5
    )
    self.category_combobox = ttk.Combobox(
        form_frame,
        values=[
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Entertainment",
            "Other",
        ],
    )
    self.category_combobox.grid(row=0, column=3, padx=5, pady=5)
    self.category_combobox.set("Food")

    # Description Label & Entry
    tk.Label(form_frame, text="Description:").grid(
        row=1, column=0, sticky="w", pady=5
    )
    self.desc_entry = tk.Entry(form_frame)
    self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

    # Amount Label & Entry
    tk.Label(form_frame, text="Amount (₹):").grid(
        row=1, column=2, sticky="w", pady=5
    )
    self.amount_entry = tk.Entry(form_frame)
    self.amount_entry.grid(row=1, column=3, padx=5, pady=5)

    # Add Expense Button
    add_btn = tk.Button(
        form_frame,
        text="Add Expense",
        command=self.add_expense,
        bg="#4CAF50",
        fg="white",
    )
    add_btn.grid(row=2, column=3, pady=10, sticky="e")

    # Treeview Frame for displaying records
    tree_frame = tk.Frame(self.root)
    tree_frame.pack(fill="both", expand=True, padx=15, pady=5)

    self.tree = ttk.Treeview(
        tree_frame,
        columns=("ID", "Date", "Category", "Description", "Amount"),
        show="headings",
    )
    self.tree.heading("ID", text="ID")
    self.tree.heading("Date", text="Date")
    self.tree.heading("Category", text="Category")
    self.tree.heading("Description", text="Description")
    self.tree.heading("Amount", text="Amount")

    self.tree.column("ID", width=40, anchor="center")
    self.tree.column("Date", width=100, anchor="center")
    self.tree.column("Category", width=120)
    self.tree.column("Description", width=220)
    self.tree.column("Amount", width=100, anchor="e")

    self.tree.pack(side="left", fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(
        tree_frame, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Action Buttons Frame
    btn_frame = tk.Frame(self.root, pady=10)
    btn_frame.pack(fill="x", padx=15)

    delete_btn = tk.Button(
        btn_frame,
        text="Delete Selected",
        command=self.delete_expense,
        bg="#f44336",
        fg="white",
    )
    delete_btn.pack(side="left")

    self.total_label = tk.Label(
        btn_frame,
        text="Total Spent: ₹0.00",
        font=("Helvetica", 11, "bold"),
    )
    self.total_label.pack(side="right")

    # Load initial data into the table
    self.fetch_expenses()

  def create_table(self):
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL
            )
        """)
    self.conn.commit()

  def add_expense(self):
    date = self.date_entry.get()
    category = self.category_combobox.get()
    desc = self.desc_entry.get()
    amount = self.amount_entry.get()

    if not date or not category or not amount:
      messagebox.showwarning("Input Error", "Please fill in all required fields!")
      return

    try:
      amount = float(amount)
    except ValueError:
      messagebox.showwarning("Input Error", "Amount must be a valid number!")
      return

    self.cursor.execute(
        """
            INSERT INTO expenses (date, category, description, amount)
            VALUES (?, ?, ?, ?)
        """,
        (date, category, desc, amount),
    )
    self.conn.commit()

    # Clear input fields
    self.date_entry.delete(0, tk.END)
    self.desc_entry.delete(0, tk.END)
    self.amount_entry.delete(0, tk.END)

    self.fetch_expenses()
    messagebox.showinfo("Success", "Expense added successfully!")

  def fetch_expenses(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    self.cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    rows = self.cursor.fetchall()

    total = 0.0
    for row in rows:
      self.tree.insert("", "end", values=row)
      total += row[4]

    self.total_label.config(text=f"Total Spent: ₹{total:.2f}")

  def delete_expense(self):
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning(
          "Selection Error", "Please select an expense to delete."
      )
      return

    item_values = self.tree.item(selected_item)["values"]
    expense_id = item_values[0]

    self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    self.conn.commit()
    self.fetch_expenses()
    messagebox.showinfo("Success", "Expense deleted successfully!")


if __name__ == "__main__":
  root = tk.Tk()
  app = ExpenseTrackerApp(root)
  root.mainloop()
