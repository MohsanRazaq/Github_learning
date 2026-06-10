"""
History Screen — View, search, filter, and manage saved analyses.
Modern table with search bar, language filter, and styled rows.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox

from config import COLORS
from database.db_manager import get_history, delete_record, get_all_languages


class HistoryScreen(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Analysis History")
        self.geometry("1050x620")
        self.minsize(900, 500)
        self.configure(fg_color=COLORS["bg_primary"])

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
            rowheight=34
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
        """Build the history screen UI."""

        # --- Top Bar ---
        top_bar = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"],
            corner_radius=0, height=55
        )
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar,
            text=" Analysis History",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=10)

        self.count_label = ctk.CTkLabel(
            top_bar,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.count_label.pack(side="right", padx=20)

        # --- Search / Filter Bar ---
        filter_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        filter_frame.pack(fill="x", padx=20, pady=(12, 8))

        # Search entry
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search by name, owner, or description...",
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._load_data())

        # Language filter dropdown
        self.lang_var = ctk.StringVar(value="All Languages")
        self.lang_dropdown = ctk.CTkComboBox(
            filter_frame,
            values=["All Languages"],
            variable=self.lang_var,
            width=180, height=36,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            command=lambda _: self._load_data()
        )
        self.lang_dropdown.pack(side="left", padx=(0, 10))

        # Clear button
        clear_btn = ctk.CTkButton(
            filter_frame,
            text="✕ Clear",
            width=80, height=36,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["danger"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=8,
            command=self._clear_filters
        )
        clear_btn.pack(side="left")

        # --- Treeview ---
        tree_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1,
            border_color=COLORS["border"]
        )
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        columns = ("ID", "Repository", "Owner", "Language", "Stars", "Forks", "Issues", "Date")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Dark.Treeview",
            selectmode="browse"
        )

        # Column configuration
        col_widths = {
            "ID": 50, "Repository": 180, "Owner": 140,
            "Language": 100, "Stars": 70, "Forks": 70,
            "Issues": 70, "Date": 150
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(
                col,
                width=col_widths.get(col, 100),
                anchor="w",
                minwidth=50
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # --- Action Buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="  Delete Selected",
            width=160, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#ff7070",
            corner_radius=10,
            command=self._delete_selected
        )
        delete_btn.pack(side="left", padx=(0, 10))

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="  Refresh",
            width=120, height=38,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            command=self._load_data
        )
        refresh_btn.pack(side="left")

        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            width=100, height=38,
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

    def _load_data(self):
        """Load data from database with search/filter applied."""
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Get filters
        search = self.search_entry.get().strip()
        lang = self.lang_var.get()
        lang_filter = "" if lang == "All Languages" else lang

        # Fetch data
        records = get_history(
            search_query=search,
            language_filter=lang_filter
        )

        for row in records:
            self.tree.insert("", "end", values=(
                row["id"],
                row["repo_name"],
                row["owner"],
                row["language"] or "N/A",
                row["stars"],
                row["forks"],
                row["open_issues"],
                row["analyzed_date"],
            ))

        # Update count
        self.count_label.configure(
            text=f"{len(records)} {'record' if len(records) == 1 else 'records'}"
        )

        # Update language dropdown
        self._update_language_dropdown()

    def _update_language_dropdown(self):
        """Refresh the language filter dropdown."""
        languages = get_all_languages()
        values = ["All Languages"] + languages
        self.lang_dropdown.configure(values=values)

    def _clear_filters(self):
        """Clear search and filter, reload data."""
        self.search_entry.delete(0, "end")
        self.lang_var.set("All Languages")
        self._load_data()

    def _delete_selected(self):
        """Delete the selected record after confirmation."""
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a record to delete."
            )
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]
        repo_name = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the analysis for '{repo_name}'?\n\n"
            "This action cannot be undone."
        )

        if confirm:
            delete_record(record_id)
            self._load_data()
            messagebox.showinfo("Deleted", "Record deleted successfully.")