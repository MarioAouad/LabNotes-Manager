import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
# Function to export data to an SQL file
import re

# Create or connect to a database
conn = sqlite3.connect('lab_notes.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS lab_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    subject TEXT NOT NULL,
    notes TEXT NOT NULL
)
''')
conn.commit()

# Function to add a new note
def add_note():
    subject = subject_entry.get()
    date = date_entry.get()
    notes = notes_entry.get("1.0", tk.END).strip()

    if not date or not subject or not notes:
        messagebox.showwarning("Input Error", "All fields must be filled out.")
        return

    # Format the subject: each word capitalized and separated by underscores, keeping original capitalization
    formatted_subject = '_'.join([word if word.isupper() else word.capitalize() for word in subject.split()])

    try:
        # Validate the date format (DD-MM-YYYY)
        datetime.datetime.strptime(date, '%d-%m-%Y')
    except ValueError:
        messagebox.showerror("Date Error", "Date must be in DD-MM-YYYY format.")
        return

    formatted_date = f"[{date}]"

    cursor.execute("INSERT INTO lab_notes (date, subject, notes) VALUES (?, ?, ?)", (formatted_date, formatted_subject, notes))
    conn.commit()
    messagebox.showinfo("Success", "Note added successfully!")
    clear_entries()

# Function to clear the input fields
def clear_entries():
    subject_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    notes_entry.delete("1.0", tk.END)

# Function to export data to an SQL file
def export_to_sql():
    with open('lab_notes_export.sql', 'w') as f:
        for line in conn.iterdump():
            # Remove double quotes around table and column names
            cleaned_line = re.sub(r'"(\w+)"', r'\1', line)
            # Remove AUTOINCREMENT keyword
            cleaned_line = re.sub(r'AUTOINCREMENT', '', cleaned_line)
            # Remove specific sentences related to sqlite_sequence
            cleaned_line = re.sub(r'DELETE FROM sqlite_sequence;\n?', '', cleaned_line)
            cleaned_line = re.sub(r'INSERT INTO sqlite_sequence VALUES\(.*?\);\n?', '', cleaned_line)
            f.write(f'{cleaned_line}\n')
        f.write("select * from lab_notes")
    messagebox.showinfo("Export Success", "Data exported to lab_notes_export.sql")


# Function to show all subjects and their dates
def show_all_notes():
    all_notes_window = tk.Toplevel(root)
    all_notes_window.title("All Subjects")

    listbox = tk.Listbox(all_notes_window, width=50)
    listbox.grid(row=0, column=0, padx=10, pady=10)

    cursor.execute("SELECT id, date, subject FROM lab_notes")
    records = cursor.fetchall()

    for record in records:
        listbox.insert(tk.END, f"{record[0]} - {record[2]} - {record[1]}")

    def show_selected_note():
        selected = listbox.get(tk.ACTIVE)
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a subject.")
            return

        note_id = selected.split(' ')[0]
        cursor.execute("SELECT notes FROM lab_notes WHERE id=?", (note_id,))
        note = cursor.fetchone()

        if note:
            note_window = tk.Toplevel(all_notes_window)
            note_window.title("Note Details")
            text_widget = tk.Text(note_window, wrap=tk.WORD, height=15, width=50)
            text_widget.insert(tk.END, note[0])
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(padx=10, pady=10)

    show_button = tk.Button(all_notes_window, text="Show Notes", command=show_selected_note)
    show_button.grid(row=1, column=0, padx=10, pady=5)

# Function to confirm quit
def confirm_quit():
    if messagebox.askyesno("Quit Confirmation", "Are you sure you want to quit?"):
        root.quit()

# Function to reset the database
def reset_database():
    if messagebox.askyesno("Reset Confirmation", "Are you sure you want to reset the database? This will delete all notes."):
        cursor.execute("DROP TABLE IF EXISTS lab_notes")
        cursor.execute(''' 
        CREATE TABLE lab_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            notes TEXT NOT NULL
        )
        ''')
        conn.commit()

        # Clear and re-export the empty database to SQL file
        with open('lab_notes_export.sql', 'w') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')

        messagebox.showinfo("Reset Success", "Database and SQL file have been reset.")

# Create the main window
root = tk.Tk()
root.title("Lab Notes Management System")

# Create and place widgets
tk.Label(root, text="Subject").grid(row=0, column=0, padx=10, pady=5)
subject_entry = tk.Entry(root)
subject_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Date (DD-MM-YYYY)").grid(row=1, column=0, padx=10, pady=5)
date_entry = tk.Entry(root)
date_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Notes").grid(row=2, column=0, padx=10, pady=5)
notes_entry = tk.Text(root, wrap=tk.WORD, height=10, width=50)
notes_entry.grid(row=2, column=1, padx=10, pady=5)

show_all_button = tk.Button(root, text="Show All Notes", command=show_all_notes)
show_all_button.grid(row=3, column=0, padx=10, pady=10)

add_button = tk.Button(root, text="Add Note", command=add_note)
add_button.grid(row=3, column=1, padx=10, pady=10)

export_button = tk.Button(root, text="Export to SQL", command=export_to_sql)
export_button.grid(row=4, column=0, padx=10, pady=10)

reset_button = tk.Button(root, text="Reset Database", command=reset_database)
reset_button.grid(row=4, column=1, padx=10, pady=10)

quit_button = tk.Button(root, text="Quit", command=confirm_quit)
quit_button.grid(row=4, column=2, columnspan=2, padx=10, pady=10)

# Run the application
root.mainloop()

# Close the connection when the app is closed
conn.close()
