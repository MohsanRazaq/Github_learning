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
from database.db_manager import save_repository
from utils.learning_resources import get_resources


class AnalysisScreen(ctk.CTkToplevel):

    def __init__(self, parent, data):
        super().__init__(parent)

        self.data = data
        self.title(f"Analysis — {data['repo_name']}")
        self.geometry("920x780")
        self.minsize(800, 600)
        self.configure(fg_color=COLORS["bg_primary"])

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
            width=140, height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            command=self._save_analysis
        )
        save_btn.pack(side="right", padx=15, pady=10)

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
        """Row of stat badges."""
        stats_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color="transparent"
        )
        stats_frame.pack(fill="x", pady=(0, 12))

        stats = [
            ( "Stars", str(self.data["stars"])),
            ("Forks", str(self.data["forks"])),
            ( "Issues", str(self.data.get("open_issues", 0))),
            ( "License", self.data.get("license", "N/A")),
            ( "Branch", self.data.get("default_branch", "main")),
            ( "Updated", self.data.get("updated_at", "")[:10]),
        ]

        for emoji, label, value in stats:
            stat_card = ctk.CTkFrame(
                stats_frame, fg_color=COLORS["bg_card"],
                corner_radius=10, border_width=1,
                border_color=COLORS["border"]
            )
            stat_card.pack(side="left", fill="x", expand=True, padx=3)

            ctk.CTkLabel(
                stat_card,
                text=f"{emoji} {label}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"]
            ).pack(pady=(8, 0))

            ctk.CTkLabel(
                stat_card,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(pady=(0, 8))

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
        """Learning roadmap section."""
        language = self.data.get("language", "Not specified")
        roadmap = get_roadmap(language)

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
            text=f"  Learning Roadmap for {language}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x")

        for i, step in enumerate(roadmap, start=1):
            step_frame = ctk.CTkFrame(inner, fg_color="transparent")
            step_frame.pack(fill="x", pady=3)

            # Step number circle
            ctk.CTkLabel(
                step_frame,
                text=f"  {i}  ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=COLORS["accent"],
                text_color="white",
                corner_radius=12,
                width=28, height=28
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                step_frame,
                text=step,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(side="left", fill="x")

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
        """Fetch languages in background thread."""
        owner, repo = validate_github_url(self.data["url"])
        if not owner:
            return

        def _worker():
            languages = fetch_languages(owner, repo)
            self.after(0, lambda: self._update_languages(languages))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _update_languages(self, languages):
        """Update the languages section with fetched data."""
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
                "Record has been updated with latest data."
            )