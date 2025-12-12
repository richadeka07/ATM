import tkinter as tk
from tkinter import messagebox, font as tkfont
import mysql.connector

# --- 1. CONFIGURATION ---
# IMPORTANT: Double-check these credentials against your running MySQL server
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "Richa",      
    "password": "atmin",
    "database": "atm"            
}

conn = mysql.connector.connect(**DB_CONFIG)
print("Database connection established successfully.")
CURRENT_ACCOUNT = None # Global variable to store the logged-in account number

def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    print("Attempting to connect to the database...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        # This will show the error in the GUI
        messagebox.showerror("Database Error", f"Failed to connect to MySQL: {err}\nPlease check your database server status and login credentials.")
        # This will show the error in your terminal/command line where you run the Python script
        print(f"DEBUGGING CONNECTION ERROR: {err}") 
        return None

# --- 2. TKINTER GUI SETUP ---

class ATM_App:
    def __init__(self, master):
        self.master = master
        master.title("VARDAN ATM")
        master.geometry("800x600")
        master.config(bg="#1E90FF") 
        
        # Define Custom Fonts
        self.title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.label_font = tkfont.Font(family="Arial", size=14)
        self.button_font = tkfont.Font(family="Arial", size=12, weight="bold")

        self.show_login_screen()

    def clear_screen(self):
        """Destroys all widgets on the current screen."""
        for widget in self.master.winfo_children():
            widget.destroy()
            
    # --- 2a. LOGIN SCREEN ---
    def show_login_screen(self):
        self.clear_screen()
        
        # Main Frame
        self.login_frame = tk.Frame(self.master, bg="#F0F0F0", padx=50, pady=50, relief="raised", borderwidth=5)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        tk.Label(self.login_frame, text="WELCOME TO VARDAN ATM", font=self.title_font, fg="#000080", bg="#F0F0F0").pack(pady=20)
        
        # Account Number Input
        tk.Label(self.login_frame, text="Account No:", font=self.label_font, bg="#F0F0F0").pack(pady=5)
        self.acc_entry = tk.Entry(self.login_frame, font=self.label_font, width=25, justify='center')
        self.acc_entry.pack(pady=5)
        
        # PIN Input
        tk.Label(self.login_frame, text="PIN:", font=self.label_font, bg="#F0F0F0").pack(pady=5)
        self.pin_entry = tk.Entry(self.login_frame, font=self.label_font, width=25, justify='center', show="*")
        self.pin_entry.pack(pady=5)
        
        # Login Button
        tk.Button(self.login_frame, text="LOGIN", font=self.button_font, bg="#32CD32", fg="white", 
                  command=self.verify_login, width=20, height=2).pack(pady=20)

    def verify_login(self):
        global CURRENT_ACCOUNT
        account_no = self.acc_entry.get().strip()
        pin = self.pin_entry.get().strip()
        
        if not account_no.isdigit() or not pin.isdigit():
            messagebox.showwarning("Input Error", "Account No and PIN must be numeric.")
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Use snake_case names as per your latest SQL pattern
                sql = "SELECT Account_no FROM Account_details WHERE Account_no = %s AND PIN = %s"
                cursor.execute(sql, (account_no, pin))
                result = cursor.fetchone()
                
                if result:
                    CURRENT_ACCOUNT = account_no
                    messagebox.showinfo("Success", "Login Successful!")
                    self.show_transaction_screen()
                else:
                    messagebox.showerror("Login Failed", "Invalid Account Number or PIN.")
                    
            except mysql.connector.Error as err:
                # CRITICAL FIX: Correcting the messagebox call syntax
                messagebox.showerror("Error", f"Database query error during login: {err}")
            finally:
                cursor.close()
                conn.close()

    # --- 2b. TRANSACTION SCREEN ---
    def show_transaction_screen(self):
        self.clear_screen()
        
        # Main Frame
        self.trans_frame = tk.Frame(self.master, bg="#F0F0F0", padx=50, pady=50, relief="raised", borderwidth=5)
        self.trans_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(self.trans_frame, text="ACCOUNT TRANSACTIONS", font=self.title_font, fg="#000080", bg="#F0F0F0").pack(pady=20)
        
        # Balance Display
        self.balance_label = tk.Label(self.trans_frame, text="Current Balance: Loading...", font=self.label_font, bg="#F0F0F0")
        self.balance_label.pack(pady=10)
        self.update_balance_display()
        
        # Amount Input
        tk.Label(self.trans_frame, text="Enter Amount:", font=self.label_font, bg="#F0F0F0").pack(pady=5)
        self.amount_entry = tk.Entry(self.trans_frame, font=self.label_font, width=25, justify='center')
        self.amount_entry.pack(pady=10)
        
        # Buttons Frame
        button_frame = tk.Frame(self.trans_frame, bg="#F0F0F0")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="DEPOSIT", font=self.button_font, bg="#32CD32", fg="white", 
                  command=self.deposit_money, width=15, height=2).grid(row=0, column=0, padx=10)
        
        tk.Button(button_frame, text="WITHDRAW", font=self.button_font, bg="#FF4500", fg="white", 
                  command=self.withdraw_money, width=15, height=2).grid(row=0, column=1, padx=10)
                  
        tk.Button(self.trans_frame, text="LOGOUT", font=self.button_font, bg="#A9A9A9", fg="white", 
                  command=self.logout, width=35).pack(pady=10)

    def update_balance_display(self):
        """Fetches the current balance and updates the GUI label."""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "SELECT Balance FROM Account_details WHERE Account_no = %s"
                cursor.execute(sql, (CURRENT_ACCOUNT,))
                result = cursor.fetchone()
                if result:
                    balance = result[0]
                    self.balance_label.config(text=f"Current Balance: ₹{balance:,.2f}")
                else:
                    self.balance_label.config(text="Current Balance: N/A")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Balance fetch error: {err}")
            finally:
                cursor.close()
                conn.close()

    # --- 3. CORE ATM LOGIC ---

    def deposit_money(self):
        amount_str = self.amount_entry.get().strip()
        # Basic validation
        if not amount_str or not amount_str.replace('.', '', 1).isdigit():
            messagebox.showwarning("Input Error", "Please enter a valid numeric amount.")
            return

        amount = float(amount_str)
        if amount <= 0:
            messagebox.showwarning("Input Error", "Deposit amount must be positive.")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # SQL to update the balance: Balance = Balance + Amount
                sql = "UPDATE Account_details SET Balance = Balance + %s WHERE Account_no = %s"
                cursor.execute(sql, (amount, CURRENT_ACCOUNT))
                conn.commit()
                messagebox.showinfo("Success", f"Successfully deposited ₹{amount:,.2f}.")
                self.update_balance_display()
                self.amount_entry.delete(0, tk.END) # Clear the entry box
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Deposit failed: {err}")
                conn.rollback() # Rollback changes if an error occurred
            finally:
                cursor.close()
                conn.close()

    def withdraw_money(self):
        amount_str = self.amount_entry.get().strip()
        # Basic validation
        if not amount_str or not amount_str.replace('.', '', 1).isdigit():
            messagebox.showwarning("Input Error", "Please enter a valid numeric amount.")
            return

        amount = float(amount_str)
        if amount <= 0:
            messagebox.showwarning("Input Error", "Withdrawal amount must be positive.")
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # 1. Check current balance first (to prevent overdrawing)
                sql_check = "SELECT Balance FROM Account_details WHERE Account_no = %s"
                cursor.execute(sql_check, (CURRENT_ACCOUNT,))
                
                # Check if account was found before fetching balance
                balance_result = cursor.fetchone()
                if not balance_result:
                    messagebox.showerror("Error", "Account not found or balance unavailable.")
                    return
                
                current_balance = balance_result[0]

                if amount > current_balance:
                    messagebox.showerror("Insufficient Funds", f"Withdrawal failed. Current balance: ₹{current_balance:,.2f}")
                else:
                    # 2. Update the balance: Balance = Balance - Amount
                    sql_update = "UPDATE Account_details SET Balance = Balance - %s WHERE Account_no = %s"
                    cursor.execute(sql_update, (amount, CURRENT_ACCOUNT))
                    conn.commit()
                    messagebox.showinfo("Success", f"Successfully withdrew ₹{amount:,.2f}.")
                    self.update_balance_display()
                    self.amount_entry.delete(0, tk.END)
                    
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Withdrawal failed: {err}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()

    def logout(self):
        global CURRENT_ACCOUNT
        CURRENT_ACCOUNT = None
        messagebox.showinfo("Logout", "You have been successfully logged out.")
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = ATM_App(root)
    root.mainloop()