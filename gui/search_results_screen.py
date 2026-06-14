"""
Search Results Screen — Displays results from GitHub repository searches.
Allows selecting a repository to analyze or view on GitHub.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import webbrowser

from config import COLORS, APP_THEME
from api.github_api import fetch_repository_data


class SearchResultsScreen(ctk.CTkToplevel):

    def __init__(self, parent, skill_query, repos):
        super().__init__(parent)

        self.parent = parent
        self.skill_query = skill_query
        self.repos = repos

        self.title(f"Search Results — {skill_query}")
        self.geometry("1050x600")
        self.minsize(900, 450)
        self.configure(fg_color=COLORS["bg_primary"])

        # Make window modal and focus it
        self.transient(parent)
        self.grab_set()

        self._setup_treeview_style()
        self._create_widgets()
        self._load_data()

    def _setup_treeview_style(self):
        """Configure ttk.Treeview to match the dark theme."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Dark.Treeview",
            background=COLORS["bg_card"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_card"],
            borderwidth=0,
            font=("Segoe UI", 11),
            rowheight=36
        )

        style.configure("Dark.Treeview.Heading",
            background=COLORS["bg_secondary"],
            foreground=COLORS["text_primary"],
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )

        style.map("Dark.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")]
        )

        style.map("Dark.Treeview.Heading",
            background=[("active", COLORS["bg_card_hover"])]
        )

    def _create_widgets(self):
        """Build the search results screen UI."""

        # --- Top Bar ---
        top_bar = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"],
            corner_radius=0, height=60
        )
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar,
            text=f"🔍  GitHub Repositories for '{self.skill_query}'",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=10)

        self.count_label = ctk.CTkLabel(
            top_bar,
            text=f"{len(self.repos)} repositories found",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.count_label.pack(side="right", padx=20)

        # --- Description Panel at bottom ---
        self.desc_card = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"],
            corner_radius=10, border_width=1,
            border_color=COLORS["border"],
            height=80
        )
        self.desc_card.pack(side="bottom", fill="x", padx=20, pady=(0, 15))
        self.desc_card.pack_propagate(False)

        self.desc_title = ctk.CTkLabel(
            self.desc_card,
            text="Repository Description",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.desc_title.pack(fill="x", padx=15, pady=(8, 2))

        self.desc_label = ctk.CTkLabel(
            self.desc_card,
            text="Select a repository to view its description.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=980, justify="left", anchor="w"
        )
        self.desc_label.pack(fill="x", padx=15, pady=(0, 8))

        # --- Action Buttons (above description) ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 12))

        self.analyze_btn = ctk.CTkButton(
            btn_frame,
            text="🚀  Analyze Repository",
            width=180, height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=10,
            command=self._analyze_selected
        )
        self.analyze_btn.pack(side="left", padx=(0, 10))

        github_btn = ctk.CTkButton(
            btn_frame,
            text="🌐  View on GitHub",
            width=150, height=40,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            command=self._open_github
        )
        github_btn.pack(side="left")

        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            width=100, height=40,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=10,
            command=self.destroy
        )
        close_btn.pack(side="right")

        # --- Treeview ---
        tree_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1,
            border_color=COLORS["border"]
        )
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(15, 10))

        columns = ("Repository", "Language", "Stars", "Forks", "URL")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Dark.Treeview",
            selectmode="browse"
        )

        # Column configuration
        col_widths = {
            "Repository": 280,
            "Language": 130,
            "Stars": 100,
            "Forks": 100,
            "URL": 380
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(
                col,
                width=col_widths.get(col, 150),
                anchor="w",
                minwidth=80
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Double click to analyze
        self.tree.bind("<Double-1>", lambda e: self._analyze_selected())
        # Selection change to update description
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_description())

    def _load_data(self):
        """Populate the treeview with search results."""
        for repo in self.repos:
            self.tree.insert("", "end", values=(
                repo["full_name"],
                repo.get("language", "Not specified"),
                f"⭐ {repo.get('stars', 0):,}",
                f"🍴 {repo.get('forks', 0):,}",
                repo["html_url"]
            ))

        # Select first row by default if exists
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self._update_description()

    def _update_description(self):
        """Update description label when selection changes."""
        selected = self.tree.selection()
        if not selected:
            self.desc_label.configure(text="Select a repository to view its description.")
            return

        item = self.tree.item(selected[0])
        full_name = item["values"][0]

        # Find repo in repos list
        matching_repo = next((r for r in self.repos if r["full_name"] == full_name), None)
        if matching_repo:
            desc = matching_repo.get("description", "") or "No description provided."
            self.desc_label.configure(text=desc)
            self.desc_title.configure(text=f"Description for {full_name}")

    def _get_selected_repo_url(self):
        """Get the URL of the selected repository row."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a repository first.")
            return None
        item = self.tree.item(selected[0])
        return item["values"][4]

    def _open_github(self):
        """Open selected repo URL in web browser."""
        url = self._get_selected_repo_url()
        if url:
            webbrowser.open(url)

    def _analyze_selected(self):
        """Send selected repo URL back to the main home screen to run analysis."""
        url = self._get_selected_repo_url()
        if not url:
            return

        # Close search results modal first
        self.destroy()

        # Update entry in parent home screen and trigger analysis
        self.parent.url_entry.delete(0, "end")
        self.parent.url_entry.insert(0, url)
        self.parent._analyze_repo()
