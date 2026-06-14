"""
History Screen — View, search, filter, and manage saved analyses.
Features: segmented view (List vs Dashboard), multiple repo comparison, custom canvas analytics.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import collections

from config import COLORS
from database.db_manager import get_history, delete_record, get_all_languages
from roadmap.roadmap_generator import get_difficulty
from gui.compare_screen import CompareScreen


class HistoryScreen(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Analysis History & Dashboard")
        self.geometry("1100x680")
        self.minsize(950, 550)
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
        """Build the history screen UI with Segmented View."""

        # --- Top Bar ---
        top_bar = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"],
            corner_radius=0, height=55
        )
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar,
            text=" 📊  Analysis History & Dashboard",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=10)

        # Segmented view selector
        self.view_selector = ctk.CTkSegmentedButton(
            top_bar,
            values=["📋 History List", "📈 Analytics Dashboard"],
            font=ctk.CTkFont(size=12, weight="bold"),
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            fg_color=COLORS["bg_primary"],
            unselected_color="transparent",
            unselected_hover_color=COLORS["bg_card_hover"],
            command=self._toggle_view
        )
        self.view_selector.pack(side="right", padx=20, pady=10)
        self.view_selector.set("📋 History List")

        # --- Main View Frames ---
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        self.dashboard_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Dashboard packed dynamically via _toggle_view

        self._build_list_view()
        self._build_dashboard_view()

    def _build_list_view(self):
        """Build the list view containing table and search tools."""
        lf = self.list_frame

        # Search/Filter Bar
        filter_frame = ctk.CTkFrame(lf, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(12, 8))

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

        # Treeview (multi-select enabled via selectmode="extended")
        tree_container = ctk.CTkFrame(
            lf, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1,
            border_color=COLORS["border"]
        )
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        columns = ("ID", "Repository", "Owner", "Language", "Progress", "Stars", "Forks", "Issues", "Date")

        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Dark.Treeview",
            selectmode="extended"
        )

        col_widths = {
            "ID": 50, "Repository": 180, "Owner": 140,
            "Language": 110, "Progress": 85, "Stars": 80, "Forks": 80,
            "Issues": 80, "Date": 130
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(
                col,
                width=col_widths.get(col, 100),
                anchor="w",
                minwidth=50
            )

        scrollbar = ttk.Scrollbar(
            tree_container, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Action Buttons
        btn_frame = ctk.CTkFrame(lf, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Multiple compare button
        self.compare_btn = ctk.CTkButton(
            btn_frame,
            text="⚖️  Compare Selected",
            width=160, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=10,
            command=self._compare_selected
        )
        self.compare_btn.pack(side="left", padx=(0, 10))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️  Delete Selected",
            width=150, height=38,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["danger"],
            hover_color="#ff7070",
            corner_radius=10,
            command=self._delete_selected
        )
        delete_btn.pack(side="left", padx=(0, 10))

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            width=100, height=38,
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

        # Label showing total count in footer
        self.count_label = ctk.CTkLabel(
            btn_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.count_label.pack(side="right", padx=10)

    def _build_dashboard_view(self):
        """Build the container layout for analytics dashboard."""
        df = self.dashboard_frame

        # Scrollable content
        self.dash_scroll = ctk.CTkScrollableFrame(
            df, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        self.dash_scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def _load_dashboard_data(self):
        """Compute statistics and render dashboard elements."""
        # Clear existing elements in dashboard scroll
        for widget in self.dash_scroll.winfo_children():
            widget.destroy()

        records = get_history()
        total_repos = len(records)

        if total_repos == 0:
            ctk.CTkLabel(
                self.dash_scroll,
                text="📊 No analysis history available yet.\nSave some repositories to view the analytics dashboard!",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text_muted"]
            ).pack(pady=100)
            return

        # Computations
        total_stars = sum(r["stars"] for r in records)
        total_forks = sum(r["forks"] for r in records)
        avg_progress = int(sum(r.get("progress_percentage", 0) for r in records) / total_repos)
        
        languages = [r["language"] for r in records if r["language"] and r["language"] != "Not specified"]
        lang_counts = collections.Counter(languages)
        active_langs = len(lang_counts)

        # Count difficulties
        diff_counts = {"Beginner": 0, "Intermediate": 0, "Advanced": 0, "Expert": 0}
        for r in records:
            lvl, _, _ = get_difficulty(r["stars"], r.get("forks", 0), r.get("open_issues", 0), r.get("size_kb", 0))
            if lvl in diff_counts:
                diff_counts[lvl] += 1

        # --- KPI Cards Row ---
        kpi_frame = ctk.CTkFrame(self.dash_scroll, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 15))

        kpis = [
            ("📁 Total Repos", f"{total_repos}", COLORS["accent_soft"]),
            ("⭐ Total Stars", f"{total_stars:,}", COLORS["warning"]),
            ("📈 Avg Progress", f"{avg_progress}%", COLORS["success"]),
            ("🌐 Languages", f"{active_langs} Active", COLORS["info"]),
        ]

        for title, val, accent_col in kpis:
            card = ctk.CTkFrame(
                kpi_frame, fg_color=COLORS["bg_card"],
                corner_radius=12, border_width=1,
                border_color=COLORS["border"]
            )
            card.pack(side="left", fill="x", expand=True, padx=5)

            ctk.CTkLabel(
                card, text=title,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"]
            ).pack(pady=(12, 2))

            ctk.CTkLabel(
                card, text=val,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=accent_col
            ).pack(pady=(0, 12))

        # --- Visualizations section (2 Columns) ---
        vis_frame = ctk.CTkFrame(self.dash_scroll, fg_color="transparent")
        vis_frame.pack(fill="both", expand=True, pady=5)
        vis_frame.grid_columnconfigure(0, weight=1, uniform="vis_col")
        vis_frame.grid_columnconfigure(1, weight=1, uniform="vis_col")

        # LEFT COLUMN: Top Languages Canvas Bar Chart
        lang_card = ctk.CTkFrame(
            vis_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        lang_card.grid(row=0, column=0, padx=5, sticky="nsew")

        ctk.CTkLabel(
            lang_card, text="🌐  Top Languages Distribution",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Custom canvas to draw horizontal bar chart
        canvas_height = 200
        canvas = ctk.CTkCanvas(
            lang_card, bg=COLORS["bg_card"],
            highlightthickness=0, height=canvas_height
        )
        canvas.pack(fill="x", padx=15, pady=(0, 15))

        # Calculate percentages for top 5 languages
        sorted_langs = lang_counts.most_common(5)
        max_count = max(lang_counts.values()) if lang_counts else 1

        y_offset = 15
        row_height = 34
        for idx, (lang, count) in enumerate(sorted_langs):
            pct = (count / total_repos) * 100
            bar_width_max = 240
            bar_width = int((count / max_count) * bar_width_max)

            # Draw Label
            canvas.create_text(
                10, y_offset + 10, text=f"{lang:<12}",
                fill=COLORS["text_secondary"], font=("Segoe UI", 10, "bold"), anchor="w"
            )

            # Draw Bar Background
            canvas.create_rectangle(
                100, y_offset, 100 + bar_width_max, y_offset + 16,
                fill=COLORS["bg_input"], outline=""
            )

            # Draw Bar Value
            canvas.create_rectangle(
                100, y_offset, 100 + bar_width, y_offset + 16,
                fill=COLORS["accent"], outline=""
            )

            # Draw Percent Value
            canvas.create_text(
                100 + bar_width_max + 12, y_offset + 8, text=f"{count} ({pct:.0f}%)",
                fill=COLORS["text_muted"], font=("Segoe UI", 9), anchor="w"
            )

            y_offset += row_height

        if not sorted_langs:
            canvas.create_text(
                150, 100, text="No language details available.",
                fill=COLORS["text_muted"], font=("Segoe UI", 11)
            )

        # RIGHT COLUMN: Difficulty Level distribution
        diff_card = ctk.CTkFrame(
            vis_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        diff_card.grid(row=0, column=1, padx=5, sticky="nsew")

        ctk.CTkLabel(
            diff_card, text="📊  Difficulty Levels Distribution",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=15, pady=(12, 10))

        diff_frame = ctk.CTkFrame(diff_card, fg_color="transparent")
        diff_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        difficulty_info = [
            ("Beginner", diff_counts["Beginner"], COLORS["difficulty_beginner"]),
            ("Intermediate", diff_counts["Intermediate"], COLORS["difficulty_intermediate"]),
            ("Advanced", diff_counts["Advanced"], COLORS["difficulty_advanced"]),
            ("Expert", diff_counts["Expert"], COLORS["accent"]),
        ]

        for lvl_name, count, color in difficulty_info:
            row_frame = ctk.CTkFrame(diff_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(
                row_frame, text=f"{lvl_name:<15}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_secondary"], width=100, anchor="w"
            ).pack(side="left")

            prog_val = (count / total_repos) if total_repos > 0 else 0
            
            pb = ctk.CTkProgressBar(
                row_frame, fg_color=COLORS["progress_track"],
                progress_color=color, height=12, corner_radius=6
            )
            pb.pack(side="left", fill="x", expand=True, padx=10)
            pb.set(prog_val)

            ctk.CTkLabel(
                row_frame, text=f"{count} repos",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"], width=60, anchor="e"
            ).pack(side="right")

    def _toggle_view(self, view_name):
        """Switch screen display between List View and Dashboard View."""
        if view_name == "📋 History List":
            self.dashboard_frame.pack_forget()
            self.list_frame.pack(fill="both", expand=True)
            self._load_data()
        elif view_name == "📈 Analytics Dashboard":
            self.list_frame.pack_forget()
            self.dashboard_frame.pack(fill="both", expand=True)
            self._load_dashboard_data()

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
                f"{row.get('progress_percentage', 0)}%",
                f"⭐ {row['stars']:,}",
                f"🍴 {row['forks']:,}",
                f"📋 {row['open_issues']}",
                row["analyzed_date"],
            ))

        # Update count in footer
        self.count_label.configure(
            text=f"Total: {len(records)} {'record' if len(records) == 1 else 'records'} found"
        )

        # Update language dropdown values
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
        """Delete the selected records after confirmation."""
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select one or more records to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the {len(selected)} selected analysis records?\n\n"
            "This action cannot be undone."
        )

        if confirm:
            for sel in selected:
                item = self.tree.item(sel)
                record_id = item["values"][0]
                delete_record(record_id)
            
            self._load_data()
            if hasattr(self.master, "_update_sidebar"):
                self.master._update_sidebar()
            messagebox.showinfo("Deleted", "Selected records deleted successfully.")

    def _compare_selected(self):
        """Open comparative matrix for selected rows."""
        selected = self.tree.selection()
        if len(selected) < 2:
            messagebox.showwarning(
                "Compare Repositories",
                "Please select 2 or more repositories to compare.\n\n"
                "Tip: Hold Ctrl or Shift key to select multiple rows."
            )
            return

        # Fetch full data for each selected repository from local records
        selected_ids = [self.tree.item(s)["values"][0] for s in selected]
        
        # Get all records matching selected ids
        all_records = get_history()
        selected_repos = [row for row in all_records if row["id"] in selected_ids]

        # Launch side-by-side comparison screen
        CompareScreen(self, selected_repos)