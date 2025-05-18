import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from math import ceil, log
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv
import os
from openpyxl import Workbook


def save_as_csv(filepath, data):
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Month", "Payment", "Interest", "Principal", "Balance"])
        writer.writerows(data)


def save_as_excel(filepath, data):
    wb = Workbook()
    ws = wb.active
    ws.title = "Amortization Table"

    headers = ["Month", "Payment", "Interest", "Principal", "Balance"]
    ws.append(headers)

    for row in data:
        ws.append(row)

    wb.save(filepath)


def entry_to_float(value):
    try:
        return float(value)
    except:
        return None


def entry_to_int(value):
    try:
        return int(value)
    except:
        return None


def calculate():
    try:
        loan_type = loan_type_var.get()
        principal = entry_to_float(principal_entry.get())
        payment = entry_to_float(payment_entry.get())
        periods = entry_to_int(periods_entry.get())
        interest = entry_to_float(interest_entry.get())

        if interest is None or interest <= 0:
            raise ValueError("Interest must be a positive number")

        i = interest / 100 / 12  # monthly rate
        result_text = ""

        if loan_type == 'annuity':
            if principal is not None and payment is not None and periods is None:
                periods = log(payment / (payment - i * principal), 1 + i)
                periods = ceil(periods)
                years = periods // 12
                months = periods % 12
                result_text += f"It will take {years} years and {months} months to repay this loan.\n"
                result_text += f"Overpayment = {ceil(payment * periods - principal)}"

            elif principal is not None and periods is not None and payment is None:
                payment = (principal * i * (1 + i) ** periods) / ((1 + i) ** periods - 1)
                payment = ceil(payment)
                result_text += f"Your annuity payment = {payment}\n"
                result_text += f"Overpayment = {payment * periods - int(principal)}"

            elif payment is not None and periods is not None and principal is None:
                principal = payment / ((i * (1 + i) ** periods) / ((1 + i) ** periods - 1))
                principal = ceil(principal)
                result_text += f"Your loan principal = {principal}\n"
                result_text += f"Overpayment = {payment * periods - principal}"

            else:
                raise ValueError("Please fill exactly two of: principal, payment, periods")

        elif loan_type == 'diff':
            if principal is None or periods is None:
                raise ValueError("Principal and periods required for 'diff'")
            total = 0
            for m in range(1, periods + 1):
                d = ceil(principal / periods + i * (principal - (principal * (m - 1) / periods)))
                result_text += f"Month {m}: payment is {d}\n"
                total += d
            result_text += f"\nOverpayment = {ceil(total - principal)}"

        else:
            raise ValueError("Invalid loan type")

        result_label.config(text=result_text)

    except Exception as e:
        messagebox.showerror("Input Error", str(e))


def show_chart():
    try:
        principal = entry_to_float(principal_entry.get())
        payment = entry_to_float(payment_entry.get())
        periods = entry_to_int(periods_entry.get())
        interest = entry_to_float(interest_entry.get())

        if None in (principal, payment, periods, interest):
            messagebox.showerror("Error", "All values must be filled to show chart and table.")
            return

        rate = interest / 100 / 12
        remaining_principal = principal
        interest_payments = []
        principal_payments = []
        amortization_data = []

        for m in range(1, periods + 1):
            interest_component = remaining_principal * rate
            principal_component = payment - interest_component
            remaining_principal -= principal_component
            remaining_principal = max(0, remaining_principal)  # Prevent negative drift

            interest_payments.append(interest_component)
            principal_payments.append(principal_component)

            amortization_data.append([
                m,
                f"{payment:.2f}",
                f"{interest_component:.2f}",
                f"{principal_component:.2f}",
                f"{remaining_principal:.2f}"
            ])

        # Create chart
        months = list(range(1, periods + 1))
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.stackplot(months, principal_payments, interest_payments, labels=["Principal", "Interest"])
        ax.set_title("Amortization Breakdown")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        ax.legend(loc="upper right")

        # Show in popup window
        chart_window = tk.Toplevel(root)
        chart_window.title("Amortization Chart and Table")

        # Chart display
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Table display
        table_frame = ttk.Frame(chart_window)
        table_frame.pack(fill='both', expand=True)

        columns = ("Month", "Payment", "Interest", "Principal", "Balance")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='e', stretch=True, width=100)

        for row in amortization_data:
            tree.insert('', 'end', values=row)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        # Save button
        def save_table():
            file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
                title="Save Amortization Schedule"
            )
            if file:
                try:
                    if file.endswith('.csv'):
                        save_as_csv(file, amortization_data)
                    elif file.endswith('.xlsx'):
                        save_as_excel(file, amortization_data)
                    else:
                        messagebox.showerror("Error", "Unsupported file type selected.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {str(e)}")

        save_button = tk.Button(chart_window, text="Save Table As...", command=save_table)
        save_button.pack(pady=5)

    except Exception as e:
        messagebox.showerror("Error", f"Could not generate chart and table: {str(e)}")


# ==== GUI Setup ====
root = tk.Tk()
root.title("Loan Calculator")

tk.Label(root, text="Loan Calculator", font=("Helvetica", 16)).grid(column=0, row=0, columnspan=2, pady=10)

# Loan type
tk.Label(root, text="Loan Type:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
loan_type_var = tk.StringVar(value='annuity')
ttk.Combobox(root, textvariable=loan_type_var, values=["annuity", "diff"], state="readonly").grid(row=1, column=1, pady=2)

# Entries
labels = ["Principal", "Payment", "Periods", "Interest Rate (%)"]
entries = []
for idx, label in enumerate(labels, start=2):
    tk.Label(root, text=label + ":").grid(row=idx, column=0, sticky='e', padx=5, pady=2)
    entry = tk.Entry(root)
    entry.grid(row=idx, column=1, pady=2)
    entries.append(entry)

principal_entry, payment_entry, periods_entry, interest_entry = entries

# Buttons
tk.Button(root, text="Calculate", command=calculate).grid(row=6, column=0, columnspan=2, pady=10)
tk.Button(root, text="Show Chart", command=show_chart).grid(row=7, column=0, columnspan=2)

# Output Label
result_label = tk.Label(root, text="", justify='left', font=("Courier", 10))
result_label.grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()
