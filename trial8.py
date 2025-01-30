import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pymysql
from PIL import Image, ImageTk

# Database Connection
def db_connect():
    try:
        connection = pymysql.connect(host='localhost', 
                                     user='root', 
                                     password='vaibhav@2004',  
                                     database='unimgt',  
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Connection Error", str(e))
        return None

# Custom Dialog for Data Entry
class DataEntryDialog(tk.Toplevel):
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.title(title)
        self.result = None

        # Frame for the form entries
        self.configure(bg='#FFFFFF')  # Set background color
        entry_frame = ttk.Frame(self, padding=20, style='Custom.TFrame')
        entry_frame.pack(fill='both', expand=True)

        self.entries = {}
        for field in fields:
            row = ttk.Frame(entry_frame, padding=(0, 5))
            row.pack(fill='x')

            label = ttk.Label(row, text=f"{field}:", width=15, anchor='e', font=('Arial', 12, 'bold'), style='Custom.TLabel')
            label.pack(side='left')

            entry = ttk.Entry(row, style='Custom.TEntry', font=('Arial', 10))
            entry.pack(side='right', fill='x', expand=True)
            self.entries[field] = entry

        # Frame for the buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Submit", command=self.on_submit, style='Custom.TButton', image=submit_icon, compound='left').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, style='Custom.TButton', image=cancel_icon, compound='left').pack(side='left', padx=5)

    def on_submit(self):
        self.result = {field: entry.get() for field, entry in self.entries.items()}
        self.destroy()

    def cancel(self):
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result


# CRUD Operations
def add_data(table, columns):
    dialog = DataEntryDialog(window, f"Add Data to {table}", columns)
    data = dialog.show()
    if data:
        conn = db_connect()
        if conn is None:
            return
        with conn.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(data))
            column_names = ', '.join(columns)
            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, list(data.values()))
                conn.commit()
                messagebox.showinfo("Success", f"Data added to {table} successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

def view_data(table, treeview, columns):
    conn = db_connect()
    if conn is None:
        return
    with conn.cursor() as cursor:
        sql = f"SELECT * FROM {table}"
        cursor.execute(sql)
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for row in records:
            treeview.insert('', tk.END, values=[row[col] for col in columns])
    conn.close()

def delete_data(table, id_column):
    record_id = simpledialog.askstring("Delete Record", f"Enter {id_column} to delete:")
    if record_id:
        conn = db_connect()
        if conn is None:
            return
        with conn.cursor() as cursor:
            sql = f"DELETE FROM {table} WHERE {id_column} = %s"
            try:
                cursor.execute(sql, (record_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    messagebox.showinfo("Info", "No record found with the given ID.")
                else:
                    messagebox.showinfo("Success", "Record deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()
    else:
        messagebox.showinfo("Info", "Deletion cancelled, no ID provided.")

# Setup GUI with Tabs
def setup_ui(window):
    window.title("University Management System")
    window.geometry('1200x600')

    style = ttk.Style()
    style.theme_use('clam')

    # Customizing the style for data and tables
    style.configure('Custom.Treeview', background='#FFFFFF', foreground='#333333', font=('Arial', 10))
    style.map('Custom.Treeview', background=[('selected', '#FF6347')])

    # Load icons with reduced size
    global submit_icon, cancel_icon, view_icon, add_icon, delete_icon
    submit_icon = tk.PhotoImage(file='submit_icon.png').subsample(4)  # Reduce size to quarter
    cancel_icon = tk.PhotoImage(file='cancel_icon.png').subsample(4)  # Reduce size to quarter
    view_icon = tk.PhotoImage(file='view_icon.png').subsample(4)  # Reduce size to quarter
    add_icon = tk.PhotoImage(file='add_icon.png').subsample(4)  # Reduce size to quarter
    delete_icon = tk.PhotoImage(file='images.png').subsample(4)  # Reduce size to quarter

    tab_control = ttk.Notebook(window)

    # Table details
    tables = {
        'University': ['UNIVERSITYID', 'ADDRESS', 'S_NAME'],
        'People': ['PEOPLEID', 'NAME', 'GENDER', 'DOB'],
        'Faculty': ['F_ID', 'NAME', 'DEPARTMENT', 'SALARY', 'MOBILE_NO'],
        'Student': ['S_ID', 'NAME', 'ADDRESS', 'PHONE_NO', 'DOB'],
        'Course': ['COURSE_ID', 'CREDITS', 'COURSE_NAME'],
        'Fees': ['STUID', 'FEEID', 'AMOUNT', 'DATE_'],
        'Attendance': ['ATT_ID', 'COURSE_ID', 'STU_ID', 'DATE_'],
        'Library': ['LIBRARYID', 'NAME', 'LOCATION'],
        'Department': ['DEPARTMENT_ID', 'D_NAME', 'HOD'],
        'Hostel': ['HOSTELID', 'NAME', 'LOCATION'],
        'Scholarship': ['SCHOLARSHIPID', 'NAME', 'AMOUNT'],
        'Book': ['ISBN', 'TITLE', 'AUTHOR'],
        'Grade': ['GRADEID', 'NAME', 'RANGE_'],
        'Boys': ['HOSTELID', 'NAME', 'GENDER'],  
        'Girls': ['HOSTELID', 'NAME', 'GENDER'], 
        'Faculty_Quater': ['QUATERID', 'FACILITIES', 'LOCATION'],
        'Exam': ['EXAMID', 'COURSEID', 'DATE_']
    }

    for table, cols in tables.items():
        tab = ttk.Frame(tab_control)
        tab_control.add(tab, text=table)

        # Treeview for displaying data with custom style
        tree = ttk.Treeview(tab, columns=cols, show='headings', style='Custom.Treeview')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=150)
        tree.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

        # Buttons for CRUD operations with smaller icons
        ttk.Button(tab, text="View Data", command=lambda t=table, tr=tree, c=cols: view_data(t, tr, c), style='Custom.TButton', image=view_icon, compound='left').grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(tab, text="Add Data", command=lambda t=table, c=cols: add_data(t, c), style='Custom.TButton', image=add_icon, compound='left').grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(tab, text="Delete Data", command=lambda t=table, id_col=cols[0]: delete_data(t, id_col), style='Custom.TButton', image=delete_icon, compound='left').grid(row=2, column=0, padx=5, pady=5)

    tab_control.pack(expand=1, fill='both')


# Main function
def main():
    global window
    window = tk.Tk()
    setup_ui(window)
    window.mainloop()

if __name__ == "__main__":
    main()
