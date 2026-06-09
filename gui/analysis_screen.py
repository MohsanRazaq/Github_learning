import tkinter as tk
from tkinter import messagebox

from roadmap.roadmap_generator import (
    get_roadmap,
    get_difficulty
)

from roadmap.contribution_helper import (
    get_contribution_advice
)

from database.db_manager import save_repository


class AnalysisScreen(tk.Toplevel):

    def __init__(self, parent, data):

        super().__init__(parent)

        self.data = data

        self.title("Repository Analysis")

        self.geometry("850x700")

        self.create_widgets()

    def create_widgets(self):

        difficulty = get_difficulty(
            self.data["stars"]
        )

        advice = get_contribution_advice(
            self.data["stars"]
        )

        roadmap = get_roadmap(
            self.data["language"]
        )

        topics = ", ".join(
            self.data.get("topics", [])
        )

        if not topics:
            topics = "No topics available"

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

Topics:
{topics}

Stars: {self.data['stars']}

Forks: {self.data['forks']}

Last Updated:
{self.data['updated_at']}

Difficulty Level:
{difficulty}
"""

        info_label = tk.Label(
            self,
            text=info,
            justify="left",
            anchor="w",
            wraplength=800
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

            roadmap_text += (
                f"{i}. {step}\n"
            )

        roadmap_label = tk.Label(
            self,
            text=roadmap_text,
            justify="left"
        )

        roadmap_label.pack(
            pady=10
        )

        # Contribution Advice Section

        advice_title = tk.Label(
            self,
            text="Contribution Advice",
            font=("Arial", 14, "bold")
        )

        advice_title.pack(
            pady=10
        )

        advice_label = tk.Label(
            self,
            text=advice,
            justify="left",
            wraplength=700
        )

        advice_label.pack(
            pady=5
        )

        save_btn = tk.Button(
            self,
            text="Save Analysis",
            width=20,
            command=self.save_analysis
        )

        save_btn.pack(
            pady=10
        )

        close_btn = tk.Button(
            self,
            text="Close",
            width=20,
            command=self.destroy
        )

        close_btn.pack()

    def save_analysis(self):

        save_repository(
            self.data
        )

        messagebox.showinfo(
            "Success",
            "Analysis saved successfully."
        )