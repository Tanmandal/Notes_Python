import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes")
        self.root.geometry("400x600")

        self.conn = sqlite3.connect("notes.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.edit_icon = tk.PhotoImage(file="edit_icon.png")
        self.delete_icon = tk.PhotoImage(file="delete_icon.png")
        self.save_icon = tk.PhotoImage(file="save_icon.png")
        self.cancel_icon = tk.PhotoImage(file="cancel_icon.png")

        self.notes_frame = tk.Frame(self.root)
        self.notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        add_button = tk.Button(self.root, text="+ Add Note", font=("Arial", 14), command=self.add_note_popup)
        add_button.pack(fill=tk.X, pady=10, padx=5)

        self.display_notes()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                color TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_note_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Note")
        popup.geometry("300x400")

        tk.Label(popup, text="Title:").pack(pady=5)
        title_entry = tk.Entry(popup, font=("Arial", 12))
        title_entry.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(popup, text="Content:").pack(pady=5)
        content_text = tk.Text(popup, font=("Arial", 12), height=10)
        content_text.pack(pady=5, fill=tk.BOTH, padx=10, expand=True)

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        save_button = tk.Button(button_frame, image=self.save_icon, command=lambda: self.save_note(popup, title_entry.get(), content_text.get(1.0, tk.END).strip()))
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, image=self.cancel_icon, command=popup.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def save_note(self, popup, title, content):
        if not title.strip() or not content.strip():
            messagebox.showwarning("Warning", "Both title and content are required!")
            return

        timestamp = datetime.now().strftime("%I:%M %p")
        color = ["#FFEBEE", "#E8F5E9", "#E3F2FD", "#FFF3E0"][self.get_note_count() % 4]

        self.cursor.execute("INSERT INTO notes (title, content, timestamp, color) VALUES (?, ?, ?, ?)", 
                            (title.strip(), content.strip(), timestamp, color))
        self.conn.commit()
        popup.destroy()
        self.display_notes()

    def edit_note_popup(self, note_id):
        self.cursor.execute("SELECT title, content FROM notes WHERE id=?", (note_id,))
        note = self.cursor.fetchone()
        if not note:
            return

        popup = tk.Toplevel(self.root)
        popup.title("Edit Note")
        popup.geometry("300x400")

        tk.Label(popup, text="Title:").pack(pady=5)
        title_entry = tk.Entry(popup, font=("Arial", 12))
        title_entry.insert(0, note[0])
        title_entry.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(popup, text="Content:").pack(pady=5)
        content_text = tk.Text(popup, font=("Arial", 12), height=10)
        content_text.insert(1.0, note[1])
        content_text.pack(pady=5, fill=tk.BOTH, padx=10, expand=True)

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        save_button = tk.Button(button_frame, image=self.save_icon, command=lambda: self.update_note(popup, note_id, title_entry.get(), content_text.get(1.0, tk.END).strip()))
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, image=self.cancel_icon, command=popup.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def update_note(self, popup, note_id, title, content):
        if not title.strip() or not content.strip():
            messagebox.showwarning("Warning", "Both title and content are required!")
            return

        self.cursor.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title.strip(), content.strip(), note_id))
        self.conn.commit()
        popup.destroy()
        self.display_notes()

    def delete_note(self, note_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?")
        if confirm:
            self.cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
            self.conn.commit()
            self.display_notes()

    def get_note_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM notes")
        return self.cursor.fetchone()[0]

    def display_notes(self):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, title, content, timestamp, color FROM notes ORDER BY id DESC")
        notes = self.cursor.fetchall()

        for note in notes:
            note_id, title, content, timestamp, color = note

            frame = tk.Frame(self.notes_frame, bg=color, bd=1, relief=tk.RIDGE)
            frame.pack(fill=tk.X, pady=5, padx=5)

            tk.Label(frame, text=title, font=("Arial", 12, "bold"), bg=color).pack(anchor="w", padx=5, pady=2)
            tk.Label(frame, text=content, font=("Arial", 10), bg=color, wraplength=350, justify="left").pack(anchor="w", padx=5, pady=2)
            tk.Label(frame, text=timestamp, font=("Arial", 9, "italic"), bg=color).pack(anchor="e", padx=5, pady=2)

            button_frame = tk.Frame(frame, bg=color)
            button_frame.pack(anchor="e", pady=2, padx=5)

            tk.Button(button_frame, image=self.edit_icon, command=lambda id=note_id: self.edit_note_popup(id)).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, image=self.delete_icon, command=lambda id=note_id: self.delete_note(id)).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()
