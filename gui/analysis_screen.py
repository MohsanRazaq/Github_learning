import tkinter as tk
from tkinter import messagebox
from roadmap.contribution_helper import (
    get_contribution_advice
)
from roadmap.roadmap_generator import (
    get_roadmap,
    get_difficulty
)

from database.db_manager import save_repository


class AnalysisScreen(tk.Toplevel):

    def __init__(self, parent, data):
        super().__init__(parent)

        self.data = data

        self.title("Repository Analysis")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):

        difficulty = get_difficulty(
            self.data["stars"]
        )

        roadmap = get_roadmap(
            self.data["language"]
        )

        title = tk.Label(
            self,
            text="Repository Analysis",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=10)

        info = f"""
Repository Name: {self.data['repo_name']}

Owner: {self.data['owner']}

Description:
{self.data['description']}

Language: {self.data['language']}

Stars: {self.data['stars']}

Forks: {self.data['forks']}

Topics:
{", ".join(
    self.data.get("topics", [])
)}

Last Updated:
{self.data['updated_at']}

Difficulty Level:
{difficulty}

advice : {get_contribution_advice(
    self.data["stars"]
)}
"""

        info_label = tk.Label(
            self,
            text=info,
            justify="left",
            anchor="w"
        )

        info_label.pack(
            padx=20,
            pady=10,
            anchor="w"
        )

        roadmap_title = tk.Label(
            self,
            text="Learning Roadmap",
            font=("Arial", 14, "bold")
        )

        roadmap_title.pack()

        roadmap_text = ""

        for i, step in enumerate(
            roadmap,
            start=1
        ):
            roadmap_text += f"{i}. {step}\n"

        roadmap_label = tk.Label(
            self,
            text=roadmap_text,
            justify="left"
        )

        roadmap_label.pack(pady=10)

        save_btn = tk.Button(
            self,
            text="Save Analysis",
            width=20,
            command=self.save_analysis
        )

        save_btn.pack(pady=10)

        back_btn = tk.Button(
            self,
            text="Close",
            width=20,
            command=self.destroy
        )

        back_btn.pack()

    def save_analysis(self):

        save_repository(self.data)

        messagebox.showinfo(
            "Success",
            "Analysis saved successfully."
        )