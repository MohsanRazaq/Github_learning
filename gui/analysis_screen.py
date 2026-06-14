"""
Analysis Screen — Displays repository analysis results.
Shows repo info, difficulty badge, learning roadmap,
contribution advice, and language breakdown in a scrollable layout.
"""
import threading
import customtkinter as ctk
from tkinter import messagebox

from config import COLORS
from api.github_api import fetch_languages, validate_github_url
from roadmap.roadmap_generator import get_roadmap, get_difficulty
from roadmap.contribution_helper import get_contribution_advice
from database.db_manager import save_repository, update_progress
from utils.learning_resources import get_resources


class AnalysisScreen(ctk.CTkToplevel):

    def __init__(self, parent, data):
        super().__init__(parent)

        self.data = data
        self.title(f"Analysis — {data['repo_name']}")
        self.geometry("920x780")
        self.minsize(800, 600)
        self.configure(fg_color=COLORS["bg_primary"])

        self.progress_percentage = data.get("progress_percentage", 0)
        completed_steps_str = data.get("completed_steps", "")
        self.completed_steps = [int(x) for x in completed_steps_str.split(",") if x.strip().isdigit()]

        self._create_widgets()
        self._fetch_extra_data()

    def _create_widgets(self):
        """Build the analysis screen with scrollable content."""

        # --- Top bar ---
        top_bar = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"],
            corner_radius=0, height=55
        )
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkButton(
            top_bar, text="← Back", width=80, height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            command=self.destroy
        )
        back_btn.pack(side="left", padx=15, pady=10)

        title = ctk.CTkLabel(
            top_bar,
            text=f"🔬  {self.data['repo_name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            top_bar, text="💾 Save Analysis",
            width=130, height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            command=self._save_analysis
        )
        save_btn.pack(side="right", padx=15, pady=10)

        export_btn = ctk.CTkButton(
            top_bar, text="📥 Export Report",
            width=130, height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            command=self._show_export_menu
        )
        export_btn.pack(side="right", padx=(0, 5), pady=10)

        explorer_btn = ctk.CTkButton(
            top_bar, text="📂 Explore Code",
            width=130, height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            command=self._open_code_explorer
        )
        explorer_btn.pack(side="right", padx=(0, 5), pady=10)

        # --- Scrollable Content ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # === SECTION 1: Repository Info Card ===
        self._create_info_card()

        # === SECTION 2: Stats Row ===
        self._create_stats_row()

        # === SECTION 3: Difficulty Badge ===
        self._create_difficulty_section()

        # === SECTION 4: Languages (placeholder, filled async) ===
        self.lang_card = self._create_section_card("  Languages Used", "Loading...")

        # === SECTION 5: Learning Roadmap ===
        self._create_roadmap_section()

        # === SECTION 6: Contribution Advice ===
        self._create_advice_section()
        self._create_resources_section()

    # -------------------------------------------------------
    # Section builders
    # -------------------------------------------------------

    def _create_info_card(self):
        """Repository info card with owner, description, topics."""
        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        # Repo name + owner
        name_row = ctk.CTkFrame(inner, fg_color="transparent")
        name_row.pack(fill="x")

        ctk.CTkLabel(
            name_row,
            text=f"👤 {self.data['owner']}  /  ",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        ctk.CTkLabel(
            name_row,
            text=self.data["repo_name"],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        # Description
        ctk.CTkLabel(
            inner,
            text=self.data["description"],
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=800, justify="left", anchor="w"
        ).pack(fill="x", pady=(10, 8))

        # Topics
        topics = self.data.get("topics", [])
        if topics:
            topics_frame = ctk.CTkFrame(inner, fg_color="transparent")
            topics_frame.pack(fill="x", pady=(4, 0))

            for topic in topics[:10]:  # Max 10 topics
                tag = ctk.CTkLabel(
                    topics_frame,
                    text=f"  {topic}  ",
                    font=ctk.CTkFont(size=10),
                    fg_color=COLORS["accent_glow"],
                    text_color=COLORS["accent"],
                    corner_radius=6, height=24
                )
                tag.pack(side="left", padx=(0, 6), pady=2)

        # URL
        ctk.CTkLabel(
            inner,
            text=f"  {self.data['url']}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", pady=(8, 0))

    def _create_stats_row(self):
        """Grid of 10 repository stat cards arranged in 2 rows."""
        stats_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color="transparent"
        )
        stats_frame.pack(fill="x", pady=(0, 12))

        # Configure columns for equal sizing
        for c in range(5):
            stats_frame.grid_columnconfigure(c, weight=1, uniform="stat_col")

        size_kb = self.data.get("size_kb", 0)
        if size_kb >= 1024 * 1024:
            size_str = f"{size_kb / (1024 * 1024):.2f} GB"
        elif size_kb >= 1024:
            size_str = f"{size_kb / 1024:.1f} MB"
        else:
            size_str = f"{size_kb} KB"

        # List of (emoji, label_text, initial_value, is_contributors)
        stats = [
            ("⭐", "Stars", f"{self.data['stars']:,}", False),
            ("🍴", "Forks", f"{self.data['forks']:,}", False),
            ("📋", "Issues", f"{self.data.get('open_issues', 0):,}", False),
            ("👁️", "Watchers", f"{self.data.get('watchers', 0):,}", False),
            ("💾", "Size", size_str, False),
            ("👥", "Contributors", "Loading...", True),
            ("📄", "License", self.data.get("license", "None"), False),
            ("🌿", "Branch", self.data.get("default_branch", "main"), False),
            ("📅", "Created", self.data.get("created_at", "")[:10] or "N/A", False),
            ("🔄", "Updated", self.data.get("updated_at", "")[:10] or "N/A", False),
        ]

        for idx, (emoji, label, value, is_contrib) in enumerate(stats):
            row = idx // 5
            col = idx % 5

            stat_card = ctk.CTkFrame(
                stats_frame, fg_color=COLORS["bg_card"],
                corner_radius=10, border_width=1,
                border_color=COLORS["border"]
            )
            stat_card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(
                stat_card,
                text=f"{emoji} {label}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"]
            ).pack(pady=(8, 0))

            val_label = ctk.CTkLabel(
                stat_card,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"]
            )
            val_label.pack(pady=(0, 8))

            if is_contrib:
                self.contributors_value_label = val_label

    def _create_difficulty_section(self):
        """Difficulty badge with multi-signal calculation."""
        difficulty_name, score, color_key = get_difficulty(
            self.data["stars"],
            self.data.get("forks", 0),
            self.data.get("open_issues", 0),
            self.data.get("size_kb", 0)
        )

        diff_color = COLORS.get(color_key, COLORS["accent"])

        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=16)

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(
            row,
            text="  Difficulty Level",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        badge = ctk.CTkLabel(
            row,
            text=f"  {difficulty_name}  (score: {score}/10)  ",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=diff_color,
            text_color=COLORS["bg_primary"],
            corner_radius=8, height=30
        )
        badge.pack(side="right")

        ctk.CTkLabel(
            inner,
            text="Based on stars, forks, open issues, and repository size.",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", pady=(6, 0))

    def _create_section_card(self, title_text, content_text):
        """Generic section card with title and content label."""
        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=16)

        ctk.CTkLabel(
            inner,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x")

        content_label = ctk.CTkLabel(
            inner,
            text=content_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=800, justify="left", anchor="w"
        )
        content_label.pack(fill="x", pady=(8, 0))

        return content_label  # Return for later updates

    def _create_roadmap_section(self):
        """Learning roadmap section with interactive progress tracking."""
        language = self.data.get("language", "Not specified")
        roadmap = get_roadmap(language)
        total_steps = len(roadmap)

        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=16)

        # Title and stats row
        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            title_row,
            text=f"🗺️  Learning Roadmap for {language}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(side="left")

        # Progress Label
        self.progress_label = ctk.CTkLabel(
            title_row,
            text=f"Progress: {self.progress_percentage}% (0 of {total_steps} completed)",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self.progress_label.pack(side="right")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            inner,
            fg_color=COLORS["progress_track"],
            progress_color=COLORS["accent"],
            height=8,
            corner_radius=4
        )
        self.progress_bar.pack(fill="x", pady=(0, 15))
        self.progress_bar.set(self.progress_percentage / 100.0)

        # List of checkboxes
        self.step_checkboxes = []

        for i, step in enumerate(roadmap, start=1):
            step_frame = ctk.CTkFrame(inner, fg_color="transparent")
            step_frame.pack(fill="x", pady=4)

            # Step number badge
            num_lbl = ctk.CTkLabel(
                step_frame,
                text=f" {i} ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=COLORS["accent"],
                text_color="white",
                corner_radius=12,
                width=24, height=24
            )
            num_lbl.pack(side="left", padx=(0, 10))

            # Checkbox variable
            var = ctk.IntVar(value=1 if i in self.completed_steps else 0)
            
            chk = ctk.CTkCheckBox(
                step_frame,
                text=step,
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                border_color=COLORS["border"],
                corner_radius=6,
                command=lambda step_idx=i, v=var, tot=total_steps: self._on_step_toggle(step_idx, v, tot)
            )
            chk.pack(side="left", fill="x", expand=True)
            self.step_checkboxes.append((var, chk))

        # Update initial progress label details
        self._update_progress_ui(total_steps)

    def _on_step_toggle(self, step_idx, var, total_steps):
        """Update checklist state and save progress to the database."""
        is_checked = var.get() == 1
        if is_checked:
            if step_idx not in self.completed_steps:
                self.completed_steps.append(step_idx)
        else:
            if step_idx in self.completed_steps:
                self.completed_steps.remove(step_idx)

        # Recalculate progress
        self.progress_percentage = int((len(self.completed_steps) / total_steps) * 100)
        self._update_progress_ui(total_steps)

        # Save to database
        self.data["progress_percentage"] = self.progress_percentage
        self.data["completed_steps"] = ",".join(str(x) for x in self.completed_steps)
        
        # Save or update progress
        save_repository(self.data)
        # Notify callback in parent if exists to update sidebar
        if hasattr(self.master, "_update_sidebar"):
            self.master._update_sidebar()

    def _update_progress_ui(self, total_steps):
        """Update progress bar value and progress text."""
        completed_count = len(self.completed_steps)
        self.progress_bar.set(self.progress_percentage / 100.0)
        self.progress_label.configure(
            text=f"Progress: {self.progress_percentage}% ({completed_count} of {total_steps} completed)"
        )

    def _create_advice_section(self):
        """Contribution advice section."""
        advice_list = get_contribution_advice(
            self.data["stars"],
            self.data.get("forks", 0),
            self.data.get("open_issues", 0),
            self.data.get("has_wiki", False),
            self.data.get("license", "None"),
            self.data.get("topics", [])
        )

        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=16)

        ctk.CTkLabel(
            inner,
            text="Contribution Advice",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x")

        for tip in advice_list:
            ctk.CTkLabel(
                inner,
                text=tip,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
                wraplength=800, justify="left", anchor="w"
            ).pack(fill="x", pady=2)

    # -------------------------------------------------------
    # Async data loading
    # -------------------------------------------------------

    def _fetch_extra_data(self):
        """Fetch languages and contributors count in background thread."""
        owner, repo = validate_github_url(self.data["url"])
        if not owner:
            return

        def _worker():
            # Fetch languages
            languages = fetch_languages(owner, repo)
            self.after(0, lambda: self._update_languages(languages))

            # Fetch contributors count
            from api.github_api import fetch_contributors_count
            contrib_count = fetch_contributors_count(owner, repo)
            self.after(0, lambda: self._update_contributors(contrib_count))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _update_languages(self, languages):
        """Update the languages section with fetched data."""
        self.languages = languages
        if not languages:
            self.lang_card.configure(text="Could not fetch language data.")
            return

        total = sum(languages.values())
        lines = []
        for lang, bytes_count in sorted(
            languages.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (bytes_count / total) * 100 if total > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            lines.append(f"{lang:<15} {bar}  {pct:.1f}%")

        self.lang_card.configure(
            text="\n".join(lines),
            font=ctk.CTkFont(family="Consolas", size=11),
            justify="left"
        )

    def _update_contributors(self, count):
        """Update the contributors stat card with the fetched value."""
        if hasattr(self, "contributors_value_label"):
            if count > 0:
                self.contributors_value_label.configure(text=f"{count:,}")
            else:
                self.contributors_value_label.configure(text="N/A")

    def _create_resources_section(self):
        """Learning resources section based on repository language."""
        language = self.data.get("language", "Not specified")
        resources = get_resources(language)
        content_label = self._create_section_card(f"  Learning Resources for {language}", "Loading...")
        if not resources:
            content_label.configure(text="No resources found for this language.")
            return
        lines = []
        for title, url in resources:
            lines.append(f"{title}: {url}")
        content_label.configure(text="\n".join(lines))

    # -------------------------------------------------------
    # Actions
    # -------------------------------------------------------

    def _save_analysis(self):
        """Save the analysis to the database."""
        self.data["progress_percentage"] = self.progress_percentage
        self.data["completed_steps"] = ",".join(str(x) for x in self.completed_steps)
        is_new = save_repository(self.data)

        if is_new:
            messagebox.showinfo(
                "Saved ✓",
                f"Analysis for '{self.data['repo_name']}' saved successfully!"
            )
        else:
            messagebox.showinfo(
                "Updated ✓",
                f"Analysis for '{self.data['repo_name']}' was already saved.\n"
                "Record has been updated with latest data and progress."
            )

    def _show_export_menu(self):
        """Show dialog to choose export format."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Export Report")
        dialog.geometry("320x180")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["bg_primary"])
        dialog.transient(self)
        # Schedule grab after the window is drawn to avoid grab errors
        self.after(10, lambda: dialog.grab_set())

        # Center dialog relative to parent analysis window
        x = self.winfo_x() + (self.winfo_width() // 2) - 160
        y = self.winfo_y() + (self.winfo_height() // 2) - 90
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text="Choose Export Format",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(20, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        def export_as(fmt):
            dialog.destroy()
            self._perform_export(fmt)

        ctk.CTkButton(
            btn_frame, text="📝 Markdown (.md)",
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=lambda: export_as("md")
        ).pack(fill="x", pady=5)

        ctk.CTkButton(
            btn_frame, text="🌐 Interactive HTML (.html)",
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=lambda: export_as("html")
        ).pack(fill="x", pady=5)

    def _perform_export(self, format_type):
        """Run the export utility based on the selected format."""
        from roadmap.roadmap_generator import get_roadmap, get_difficulty
        from roadmap.contribution_helper import get_contribution_advice
        from utils.learning_resources import get_resources

        language = self.data.get("language", "Not specified")
        roadmap = get_roadmap(language)
        difficulty_info = get_difficulty(
            self.data["stars"],
            self.data.get("forks", 0),
            self.data.get("open_issues", 0),
            self.data.get("size_kb", 0)
        )
        advice_list = get_contribution_advice(
            self.data["stars"],
            self.data.get("forks", 0),
            self.data.get("open_issues", 0),
            self.data.get("has_wiki", False),
            self.data.get("license", "None"),
            self.data.get("topics", [])
        )

        languages_dict = getattr(self, "languages", None)

        if format_type == "md":
            from utils.export_utils import export_analysis_markdown
            filepath = export_analysis_markdown(
                self.data, roadmap, advice_list, difficulty_info,
                languages=languages_dict, progress=self.progress_percentage
            )
        else:
            from utils.export_utils import export_analysis_html
            resources_list = get_resources(language)
            filepath = export_analysis_html(
                self.data, roadmap, advice_list, difficulty_info,
                languages=languages_dict, progress=self.progress_percentage,
                completed_steps=self.completed_steps, resources=resources_list
            )

        if filepath:
            messagebox.showinfo(
                "Export Successful ✓",
                f"Report successfully saved to:\n\n{filepath}"
            )
        else:
            messagebox.showerror(
                "Export Failed",
                "An error occurred while generating or saving the export report."
            )

    def _open_code_explorer(self):
        """Open the interactive Code Explorer for this repository."""
        from gui.code_explorer_screen import CodeExplorerScreen
        CodeExplorerScreen(
            self,
            self.data["owner"],
            self.data["repo_name"],
            self.data.get("default_branch", "main")
        )