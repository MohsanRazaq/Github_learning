import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database.db_manager import (
    get_history,
    delete_record
)


class HistoryScreen(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Analysis History")
        self.geometry("900x500")

        self.create_widgets()

        self.load_data()

    def create_widgets(self):

        title = tk.Label(
            self,
            text="Saved Repository History",
            font=("Arial", 16, "bold")
        )

        title.pack(pady=10)

        columns = (
            "ID",
            "Repository",
            "Owner",
            "Language",
            "Stars",
            "Date"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.tree.heading(
                col,
                text=col
            )

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        delete_btn = tk.Button(
            btn_frame,
            text="Delete Record",
            command=self.delete_selected
        )

        delete_btn.grid(
            row=0,
            column=0,
            padx=10
        )

        refresh_btn = tk.Button(
            btn_frame,
            text="Refresh",
            command=self.load_data
        )

        refresh_btn.grid(
            row=0,
            column=1,
            padx=10
        )

        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=self.destroy
        )

        close_btn.grid(
            row=0,
            column=2,
            padx=10
        )

    def load_data(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        records = get_history()

        for row in records:

            self.tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[7]
                )
            )

    def delete_selected(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Select a record first."
            )
            return

        item = self.tree.item(selected[0])

        record_id = item["values"][0]

        delete_record(record_id)

        self.load_data()

        messagebox.showinfo(
            "Deleted",
            "Record deleted successfully."
        )