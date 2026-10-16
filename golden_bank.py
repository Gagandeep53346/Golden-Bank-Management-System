import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import hashlib
import secrets
from datetime import datetime

DATA_FILE = "bank_accounts.json"

BLACK = "#101010"
PANEL = "#1B1B1B"
GOLD = "#D4AF37"
WHITE = "#FFFFFF"
GREEN = "#27AE60"
RED = "#C0392B"

accounts = {}
current_user = None


# ---------------- DATE AND TIME ----------------

def get_datetime():
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")


# ---------------- PASSWORD SECURITY ----------------

def hash_password(password, salt):
    return hashlib.sha256(
        (salt + password).encode()
    ).hexdigest()


# ---------------- SAVE AND LOAD DATA ----------------

def load_accounts():
    global accounts

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                accounts = json.load(file)

            if not isinstance(accounts, dict):
                accounts = {}

        except (json.JSONDecodeError, OSError):
            messagebox.showerror(
                "Data Error",
                "Bank data file read nahi ho saki."
            )
            accounts = {}
    else:
        accounts = {}


def save_accounts():
    try:
        temp_file = DATA_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(accounts, file, indent=4)

        os.replace(temp_file, DATA_FILE)
        return True

    except OSError as error:
        messagebox.showerror(
            "Save Error",
            "Data save nahi hua:\n" + str(error)
        )
        return False


def add_transaction(account, transaction_type, amount, details=""):
    transaction = {
        "type": transaction_type,
        "amount": round(amount, 2),
        "date_time": get_datetime(),
        "details": details
    }

    account.setdefault("transactions", []).append(transaction)
    return transaction


# ---------------- WINDOW HELPERS ----------------

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def heading(text, size=22):
    tk.Label(
        root,
        text=text,
        font=("Arial", size, "bold"),
        bg=BLACK,
        fg=GOLD
    ).pack(pady=15)


def button(text, command, color=GOLD):
    tk.Button(
        root,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        bg=color,
        fg=BLACK if color == GOLD else WHITE,
        width=27,
        pady=7
    ).pack(pady=5)


# ---------------- WELCOME SCREEN ----------------

def show_welcome():
    clear_window()
    root.configure(bg=BLACK)

    heading("GOLDEN BANK", 30)

    tk.Label(
        root,
        text="BANK MANAGEMENT SYSTEM",
        font=("Arial", 12, "bold"),
        bg=BLACK,
        fg=WHITE
    ).pack(pady=5)

    clock = tk.Label(
        root,
        text=get_datetime(),
        font=("Arial", 11),
        bg=BLACK,
        fg=GOLD
    )
    clock.pack(pady=10)

    def update_clock():
        try:
            clock.config(text=get_datetime())
            root.after(1000, update_clock)
        except tk.TclError:
            pass

    update_clock()

    button("CREATE ACCOUNT", create_account)
    button("LOGIN", login)
    button("EXIT", root.destroy, RED)


# ---------------- CREATE ACCOUNT ----------------

def create_account():
    name = simpledialog.askstring(
        "Create Account",
        "Enter your full name:",
        parent=root
    )

    if name is None:
        return

    username = simpledialog.askstring(
        "Create Account",
        "Choose a username:",
        parent=root
    )

    if username is None:
        return

    name = name.strip()
    username = username.strip()

    if not name or not username:
        messagebox.showerror(
            "Error",
            "Name aur username khaali nahi ho sakte."
        )
        return

    if username in accounts:
        messagebox.showerror(
            "Error",
            "Username already exists! Dusra username choose karo."
        )
        return

    password = simpledialog.askstring(
        "Create Account",
        "Create a password:",
        show="*",
        parent=root
    )

    if password is None:
        return

    if len(password) < 4:
        messagebox.showerror(
            "Error",
            "Password kam se kam 4 characters ka hona chahiye."
        )
        return

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    account_numbers = {
        str(account.get("account_number", ""))
        for account in accounts.values()
    }

    while True:
        account_number = str(
            secrets.randbelow(9000000000) + 1000000000
        )

        if account_number not in account_numbers:
            break

    accounts[username] = {
        "name": name,
        "account_number": account_number,
        "salt": salt,
        "password_hash": password_hash,
        "balance": 1000.00,
        "transactions": []
    }

    add_transaction(
        accounts[username],
        "Account Created",
        1000.00,
        "Opening balance"
    )

    if not save_accounts():
        accounts.pop(username, None)
        return

    messagebox.showinfo(
        "Success",
        "Account created successfully!\n\n"
        "Account Number: " + account_number +
        "\nOpening Balance: Rs. 1000.00"
    )


# ---------------- LOGIN ----------------

def login():
    global current_user

    username = simpledialog.askstring(
        "Login",
        "Enter username:",
        parent=root
    )

    if username is None:
        return

    username = username.strip()

    if username not in accounts:
        messagebox.showerror(
            "Login Failed",
            "Username nahi mila."
        )
        return

    password = simpledialog.askstring(
        "Login",
        "Enter password:",
        show="*",
        parent=root
    )

    if password is None:
        return

    account = accounts[username]
    salt = account.get("salt", "")
    saved_hash = account.get("password_hash", "")

    if hash_password(password, salt) != saved_hash:
        messagebox.showerror(
            "Login Failed",
            "Password galat hai."
        )
        return

    account.setdefault("transactions", [])
    account.setdefault("balance", 1000.00)

    current_user = username
    show_dashboard()


# ---------------- DASHBOARD ----------------

def show_dashboard():
    clear_window()
    root.configure(bg=BLACK)

    account = accounts[current_user]

    heading("GOLDEN BANK DASHBOARD", 22)

    tk.Label(
        root,
        text="Welcome, " + account.get("name", current_user),
        font=("Arial", 13, "bold"),
        bg=BLACK,
        fg=WHITE
    ).pack(pady=5)

    tk.Label(
        root,
        text="Account Number: " +
        str(account.get("account_number", "N/A")),
        bg=BLACK,
        fg=WHITE
    ).pack(pady=3)

    tk.Label(
        root,
        text="Current Balance: Rs. " +
        format(float(account.get("balance", 0)), ".2f"),
        font=("Arial", 18, "bold"),
        bg=PANEL,
        fg=GOLD,
        padx=20,
        pady=12
    ).pack(pady=12)

    tk.Label(
        root,
        text=get_datetime(),
        bg=BLACK,
        fg=GOLD
    ).pack(pady=5)

    button("DEPOSIT MONEY", deposit_money)
    button("WITHDRAW MONEY", withdraw_money)
    button("TRANSFER MONEY", transfer_money)
    button("TRANSACTION HISTORY", transaction_history)
    button("ACCOUNT PROFILE", account_profile)
    button("CHANGE PASSWORD", change_password)
    button("LOGOUT", logout, RED)


# ---------------- DEPOSIT ----------------

def deposit_money():
    account = accounts[current_user]

    amount = simpledialog.askfloat(
        "Deposit",
        "Enter deposit amount:",
        minvalue=0.01,
        parent=root
    )

    if amount is None:
        return

    old_balance = float(account.get("balance", 0))
    account["balance"] = round(old_balance + amount, 2)

    transaction = add_transaction(
        account,
        "Deposit",
        amount
    )

    if not save_accounts():
        account["balance"] = old_balance
        account["transactions"].pop()
        return

    messagebox.showinfo(
        "Success",
        "Deposit successful!\n"
        "Amount: Rs. " + format(amount, ".2f") +
        "\nNew Balance: Rs. " +
        format(account["balance"], ".2f")
    )

    show_receipt(transaction)
    show_dashboard()


# ---------------- WITHDRAW ----------------

def withdraw_money():
    account = accounts[current_user]

    amount = simpledialog.askfloat(
        "Withdraw",
        "Enter withdrawal amount:",
        minvalue=0.01,
        parent=root
    )

    if amount is None:
        return

    old_balance = float(account.get("balance", 0))

    if amount > old_balance:
        messagebox.showerror(
            "Error",
            "Insufficient balance!"
        )
        return

    account["balance"] = round(old_balance - amount, 2)

    transaction = add_transaction(
        account,
        "Withdrawal",
        amount
    )

    if not save_accounts():
        account["balance"] = old_balance
        account["transactions"].pop()
        return

    messagebox.showinfo(
        "Success",
        "Withdrawal successful!\n"
        "Remaining Balance: Rs. " +
        format(account["balance"], ".2f")
    )

    show_receipt(transaction)
    show_dashboard()


# ---------------- MONEY TRANSFER ----------------

def transfer_money():
    sender = accounts[current_user]

    receiver_number = simpledialog.askstring(
        "Transfer Money",
        "Enter receiver account number:",
        parent=root
    )

    if receiver_number is None:
        return

    receiver_number = receiver_number.strip()

    receiver_username = None
    receiver = None

    for username, account in accounts.items():
        if str(account.get("account_number", "")) == receiver_number:
            receiver_username = username
            receiver = account
            break

    if receiver is None:
        messagebox.showerror(
            "Error",
            "Receiver account nahi mila."
        )
        return

    if receiver_username == current_user:
        messagebox.showerror(
            "Error",
            "Apne hi account mein transfer nahi kar sakte."
        )
        return

    amount = simpledialog.askfloat(
        "Transfer Money",
        "Enter amount:",
        minvalue=0.01,
        parent=root
    )

    if amount is None:
        return

    sender_balance = float(sender.get("balance", 0))
    receiver_balance = float(receiver.get("balance", 0))

    if amount > sender_balance:
        messagebox.showerror(
            "Error",
            "Insufficient balance!"
        )
        return

    sender["balance"] = round(sender_balance - amount, 2)
    receiver["balance"] = round(receiver_balance + amount, 2)

    sender_transaction = add_transaction(
        sender,
        "Transfer Sent",
        amount,
        "To: " + receiver.get("name", receiver_username)
    )

    add_transaction(
        receiver,
        "Transfer Received",
        amount,
        "From: " + sender.get("name", current_user)
    )

    if not save_accounts():
        sender["balance"] = sender_balance
        receiver["balance"] = receiver_balance

        sender["transactions"].pop()
        receiver["transactions"].pop()
        return

    messagebox.showinfo(
        "Success",
        "Transfer successful!\n"
        "Amount: Rs. " + format(amount, ".2f")
    )

    show_receipt(sender_transaction)
    show_dashboard()


# ---------------- TRANSACTION HISTORY ----------------

def transaction_history():
    account = accounts[current_user]

    history_window = tk.Toplevel(root)
    history_window.title("Transaction History")
    history_window.geometry("700x450")
    history_window.configure(bg=BLACK)

    tk.Label(
        history_window,
        text="TRANSACTION HISTORY",
        font=("Arial", 18, "bold"),
        bg=BLACK,
        fg=GOLD
    ).pack(pady=10)

    text_box = tk.Text(
        history_window,
        bg=PANEL,
        fg=WHITE,
        font=("Arial", 10),
        wrap="word"
    )
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

    transactions = account.get("transactions", [])

    if not transactions:
        text_box.insert("end", "No transactions yet.\n")

    for transaction in reversed(transactions):
        if isinstance(transaction, dict):
            text_box.insert(
                "end",
                str(transaction.get("type", "Transaction")) +
                " | Rs. " +
                format(float(transaction.get("amount", 0)), ".2f") +
                " | " +
                str(transaction.get("date_time", "Date unavailable")) +
                " | " +
                str(transaction.get("details", "")) +
                "\n\n"
            )
        else:
            text_box.insert("end", str(transaction) + "\n\n")

    text_box.config(state="disabled")


# ---------------- RECEIPT ----------------

def show_receipt(transaction):
    receipt = tk.Toplevel(root)
    receipt.title("Transaction Receipt")
    receipt.geometry("400x350")
    receipt.configure(bg=BLACK)

    heading_label = tk.Label(
        receipt,
        text="GOLDEN BANK RECEIPT",
        font=("Arial", 18, "bold"),
        bg=BLACK,
        fg=GOLD
    )
    heading_label.pack(pady=20)

    receipt_text = (
        "Customer: " +
        accounts[current_user].get("name", current_user) +
        "\n\nTransaction: " +
        str(transaction.get("type", "")) +
        "\n\nAmount: Rs. " +
        format(float(transaction.get("amount", 0)), ".2f") +
        "\n\nDate & Time: " +
        str(transaction.get("date_time", "")) +
        "\n\nDetails: " +
        str(transaction.get("details", ""))
    )

    tk.Label(
        receipt,
        text=receipt_text,
        justify="left",
        font=("Arial", 11),
        bg=BLACK,
        fg=WHITE
    ).pack(padx=20, pady=10, anchor="w")

    tk.Button(
        receipt,
        text="CLOSE",
        command=receipt.destroy,
        bg=GOLD,
        fg=BLACK
    ).pack(pady=10)


# ---------------- ACCOUNT PROFILE ----------------

def account_profile():
    account = accounts[current_user]

    messagebox.showinfo(
        "Account Profile",
        "Name: " + account.get("name", current_user) +
        "\nUsername: " + current_user +
        "\nAccount Number: " +
        str(account.get("account_number", "N/A")) +
        "\nBalance: Rs. " +
        format(float(account.get("balance", 0)), ".2f") +
        "\nTransactions: " +
        str(len(account.get("transactions", []))) +
        "\nDate & Time: " + get_datetime()
    )


# ---------------- CHANGE PASSWORD ----------------

def change_password():
    account = accounts[current_user]

    old_password = simpledialog.askstring(
        "Change Password",
        "Enter current password:",
        show="*",
        parent=root
    )

    if old_password is None:
        return

    if hash_password(old_password, account.get("salt", "")) != account.get("password_hash", ""):
        messagebox.showerror(
            "Error",
            "Current password galat hai."
        )
        return

    new_password = simpledialog.askstring(
        "Change Password",
        "Enter new password:",
        show="*",
        parent=root
    )

    if new_password is None:
        return

    if len(new_password) < 4:
        messagebox.showerror(
            "Error",
            "Password minimum 4 characters ka hona chahiye."
        )
        return

    old_salt = account.get("salt")
    old_hash = account.get("password_hash")

    new_salt = secrets.token_hex(16)
    account["salt"] = new_salt
    account["password_hash"] = hash_password(new_password, new_salt)

    if not save_accounts():
        account["salt"] = old_salt
        account["password_hash"] = old_hash
        return

    messagebox.showinfo(
        "Success",
        "Password successfully changed."
    )


# ---------------- LOGOUT ----------------

def logout():
    global current_user

    current_user = None
    show_welcome()


# ---------------- START APPLICATION ----------------

load_accounts()

root = tk.Tk()
root.title("Golden Bank Management System")
root.geometry("650x750")
root.configure(bg=BLACK)

show_welcome()

root.mainloop()
