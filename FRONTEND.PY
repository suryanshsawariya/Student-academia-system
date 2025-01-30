import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pymysql

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
        entry_frame = ttk.Frame(self)
        entry_frame.pack(padx=10, pady=10, fill='x', expand=True)

        self.entries = {}
        for field in fields:
            row = ttk.Frame(entry_frame)
            row.pack(side='top', fill='x', padx=5, pady=5)

            label = ttk.Label(row, text=f"{field}:", width=15)
            label.pack(side='left')

            entry = ttk.Entry(row)
            entry.pack(side='right', expand=True, fill='x')
            self.entries[field] = entry

        # Frame for the buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10)

        ttk.Button(button_frame, text="Submit", command=self.on_submit).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)

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

        # Treeview for displaying data
        tree = ttk.Treeview(tab, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=100)
        tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Buttons for CRUD operations
        ttk.Button(tab, text="View Data", command=lambda t=table, tr=tree, c=cols: view_data(t, tr, c)).pack(pady=10, padx=10, side='left')
        ttk.Button(tab, text="Add Data", command=lambda t=table, c=cols: add_data(t, c)).pack(pady=10, padx=10, side='left')
        ttk.Button(tab, text="Delete Data", command=lambda t=table, id_col=cols[0]: delete_data(t, id_col)).pack(pady=10, padx=10, side='left')

    tab_control.pack(expand=1, fill='both')

# Main function
def main():
    global window
    window = tk.Tk()
    setup_ui(window)
    window.mainloop()

if __name__ == "__main__":
    main()