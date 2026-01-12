import sqlite3
import time
import sys
from colorama import init, Fore

# /c:/Users/Richa Deka/Coding/atm/ai_atm2.py

init(autoreset=True)

DB = "atm.db"

def loading_simulation():
    for _ in range(3):
        print(".", end="", flush=True)
        time.sleep(0.5)
    print()

def setup_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_no TEXT PRIMARY KEY,
        account_holder TEXT,
        pin TEXT,
        balance REAL
    )
    """)
    # insert rows if not present
    rows = [
        ("3691215182124273","Steve","3691",12530.98),
        ("4812162024283236","Lucas","4812",5000.00),
        ("6121824303642546","Dustin","6121",85670.67),
        ("1234567890","Vardan Sharma","1234",50000.00)
    ]
    for r in rows:
        cur.execute("INSERT OR IGNORE INTO accounts(account_no, account_holder, pin, balance) VALUES (?, ?, ?, ?)", r)
    conn.commit()
    conn.close()

def get_account(account_no, pin):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT account_no, account_holder, pin, balance FROM accounts WHERE account_no = ? AND pin = ?", (account_no, pin))
    row = cur.fetchone()
    conn.close()
    return row

def update_balance(account_no, new_balance):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = ? WHERE account_no = ?", (new_balance, account_no))
    conn.commit()
    conn.close()

def format_money(x):
    return f"{x:,.2f}"

def atm_menu(account):
    account_no, account_holder, pin, balance = account
    print()
    print("Logging in", end="", flush=True)
    loading_simulation()
    print(f"{account_holder} welcome to VARDAN ATM")
    while True:
        print("\nSelect an option:")
        print("1) Check balance")
        print("2) Withdraw")
        print("3) Deposit")
        print("4) Logout")
        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            print(f"Your balance is: {format_money(balance)}")
        elif choice == "2":
            amt_str = input("Enter amount to withdraw: ").strip()
            try:
                amt = float(amt_str)
                if amt <= 0:
                    print("Enter a positive amount.")
                    continue
            except:
                print("Invalid amount.")
                continue
            print("Processing withdrawal", end="", flush=True)
            loading_simulation()
            if amt > balance:
                print("You do not have that much in this account.")
                continue
            balance -= amt
            update_balance(account_no, balance)
            print(Fore.RED + f"Your withdrawal was successful. Thank you.")
            print(Fore.RED + f"Remaining balance: {format_money(balance)}")
        elif choice == "3":
            amt_str = input("Enter amount to deposit: ").strip()
            try:
                amt = float(amt_str)
                if amt <= 0:
                    print("Enter a positive amount.")
                    continue
            except:
                print("Invalid amount.")
                continue
            print("Processing deposit", end="", flush=True)
            loading_simulation()
            balance += amt
            update_balance(account_no, balance)
            print(Fore.GREEN + "Your deposit was successful. Thank you.")
            print(Fore.GREEN + f"New balance: {format_money(balance)}")
        elif choice == "4":
            print("Logging out", end="", flush=True)
            loading_simulation()
            break
        else:
            print("Invalid selection.")

def main():
    setup_db()
    while True:
        print("\nWelcome to VARDAN ATM")
        print("1) Login")
        print("2) Quit")
        sel = input("Select an option (1-2): ").strip()
        if sel == "2":
            print("Goodbye.")
            sys.exit(0)
        if sel != "1":
            print("Invalid selection.")
            continue
        acc_no = input("Enter account number: ").strip()
        pin = input("Enter PIN: ").strip()
        account = get_account(acc_no, pin)
        if not account:
            print("Invalid account number or PIN.")
            continue
        atm_menu(account)

if __name__ == "__main__":
    main()