import tkinter as tk
from tkinter import messagebox

from api.github_api import fetch_repository_data
from gui.analysis_screen import AnalysisScreen
from gui.history_screen import HistoryScreen


class HomeScreen(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("GitHub Learning Assistant")
        self.geometry("700x450")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):

        title = tk.Label(
            self,
            text="GitHub Learning Assistant",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=30)

        tk.Label(
            self,
            text="GitHub Repository URL"
        ).pack()

        self.url_entry = tk.Entry(
            self,
            width=60
        )
        self.url_entry.pack(pady=10)

        analyze_btn = tk.Button(
            self,
            text="Analyze Repository",
            width=20,
            command=self.analyze_repo
        )
        analyze_btn.pack(pady=10)

        history_btn = tk.Button(
            self,
            text="History",
            width=20,
            command=self.open_history
        )
        history_btn.pack(pady=10)

        exit_btn = tk.Button(
            self,
            text="Exit",
            width=20,
            command=self.destroy
        )
        exit_btn.pack(pady=10)

    def analyze_repo(self):

        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror(
                "Error",
                "Please enter a GitHub repository URL."
            )
            return

        data = fetch_repository_data(url)

        if not data:
            messagebox.showerror(
                "Error",
                "Invalid repository or unable to fetch data."
            )
            return

        AnalysisScreen(self, data)

    def open_history(self):
        HistoryScreen(self)