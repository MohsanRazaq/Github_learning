"""
Home Screen — Main application window.
Features: animated loading spinner, sample repo quick-links,
recent analyses panel, keyboard shortcuts, threaded API calls.
"""
import threading
import webbrowser
import customtkinter as ctk
from tkinter import messagebox

from config import COLORS, APP_THEME, APP_NAME, APP_VERSION, SAMPLE_REPOS
from utils.github_search import search_top_repos_by_skill
from api.github_api import fetch_repository_data
from gui.analysis_screen import AnalysisScreen
from gui.history_screen import HistoryScreen
from database.db_manager import get_record_count, get_recent_repos


class HomeScreen(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode(APP_THEME)
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("860x640")
        self.minsize(760, 560)
        self.configure(fg_color=COLORS["bg_primary"])

        # Loading animation state
        self._loading = False
        self._spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_idx = 0

        self._create_widgets()
        self._fetch_extra_data()
        self.current_skill = None  # holds skill from skill search
        
        self._update_sidebar()

        # Keyboard shortcuts
        self.bind("<Control-Return>", lambda e: self._analyze_repo())
        self.bind("<Control-h>", lambda e: self._open_history())
        self.bind("<Escape>", lambda e: self.url_entry.delete(0, "end"))

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _create_widgets(self):
        """Build the full home screen layout."""

        # ── Sidebar (left) ─────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"],
            width=220, corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # ── Main area (right) ───────────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)

        self._build_header(main)
        self._build_search_card(main)
        self._build_quick_access(main)
        self._build_footer(main)

    def _fetch_extra_data(self):
        """Placeholder for future extra data fetching (e.g., skill resources). Currently does nothing."""
        pass

    # ── Sidebar ─────────────────────────────────────────────────────────

    def _build_sidebar(self):
        """Left sidebar: logo, nav buttons, recent repos."""
        sb = self.sidebar

        # Logo block
        logo_frame = ctk.CTkFrame(sb, fg_color=COLORS["bg_primary"], corner_radius=0)
        logo_frame.pack(fill="x")

        ctk.CTkLabel(
            logo_frame, text="🔬",
            font=ctk.CTkFont(size=36)
        ).pack(pady=(22, 0))

        ctk.CTkLabel(
            logo_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"],
            wraplength=200
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            logo_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        ).pack(pady=(2, 16))

        # Divider
        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).pack(fill="x")

        # Nav buttons
        nav_items = [
            ("  Home", self._focus_entry),
            ("  History", self._open_history),
            ("  GitHub", lambda: webbrowser.open("https://github.com")),
        ]

        nav_frame = ctk.CTkFrame(sb, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=12)

        for label, cmd in nav_items:
            btn = ctk.CTkButton(
                nav_frame, text=label,
                height=36, anchor="w",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color=COLORS["bg_card_hover"],
                text_color=COLORS["text_secondary"],
                corner_radius=8,
                command=cmd
            )
            btn.pack(fill="x", pady=2)

        # Divider
        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).pack(fill="x")

        # Recent repos section
        ctk.CTkLabel(
            sb,
            text="RECENT",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", padx=14, pady=(10, 4))

        self.recent_frame = ctk.CTkFrame(sb, fg_color="transparent")
        self.recent_frame.pack(fill="x", padx=10)

        # Stats at bottom of sidebar
        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).pack(
            fill="x", side="bottom"
        )

        stats_frame = ctk.CTkFrame(sb, fg_color="transparent")
        stats_frame.pack(side="bottom", fill="x", padx=14, pady=10)

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text=" 0 analyses saved",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.stats_label.pack(fill="x")

        token_color = COLORS["success"] if __import__("config").GITHUB_TOKEN else COLORS["warning"]
        token_text = " Token: Active" if __import__("config").GITHUB_TOKEN else " No API token"
        ctk.CTkLabel(
            stats_frame,
            text=token_text,
            font=ctk.CTkFont(size=10),
            text_color=token_color,
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

    # ── Header ──────────────────────────────────────────────────────────

    def _build_header(self, parent):
        """Top gradient-style header."""
        header = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_secondary"],
            corner_radius=0, height=70
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(expand=True)

        ctk.CTkLabel(
            inner,
            text="Analyze · Learn · Contribute",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack()

        ctk.CTkLabel(
            inner,
            text="Paste any GitHub repository URL to get an instant learning roadmap",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        ).pack(pady=(2, 0))

    # ── Search card ─────────────────────────────────────────────────────

    def _build_search_card(self, parent):
        """Main URL input card with analyze button and status."""
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"],
            corner_radius=18, border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", padx=28, pady=(22, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=22)

        # Label row
        lbl_row = ctk.CTkFrame(inner, fg_color="transparent")
        lbl_row.pack(fill="x")

        ctk.CTkLabel(
            lbl_row,
            text="  GitHub Repository URL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            lbl_row,
            text="Ctrl+Enter to analyze",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"],
        ).pack(side="right")

        ctk.CTkLabel(
            inner,
            text="Supports: full URL · github.com/owner/repo · owner/repo",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", pady=(2, 8))

       
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.url_entry = ctk.CTkEntry(
            row,
            placeholder_text="https://github.com/owner/repository",
            height=44,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            corner_radius=10
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self._analyze_repo())
        self.url_entry.focus_set()

        self.analyze_btn = ctk.CTkButton(
            row,
            text=" Analyze",
            width=140, height=44,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=10,
            command=self._analyze_repo
        )
        self.analyze_btn.pack(side="right")

        # Skill search row
        skill_row = ctk.CTkFrame(inner, fg_color="transparent")
        skill_row.pack(fill="x", pady=(10, 0))

        self.skill_entry = ctk.CTkEntry(
            skill_row,
            placeholder_text="e.g., AI Engineer",
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            corner_radius=10
        )
        self.skill_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.skill_btn = ctk.CTkButton(
            skill_row,
            text="🔎 Find Repos",
            width=120, height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=10,
            command=self._search_by_skill
        )
        self.skill_btn.pack(side="right")
        # Status label for spinner / messages
        self.status_label = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=11), text_color=COLORS["accent"], anchor="w")
        self.status_label.pack(fill="x", pady=(8, 0))


    # ── Quick access ────────────────────────────────────────────────────

    def _build_quick_access(self, parent):
        """Sample repos quick-access chips."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=28, pady=(0, 6))

        ctk.CTkLabel(
            frame,
            text="Try a sample:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(0, 10))

        for repo_slug, emoji in SAMPLE_REPOS:
            chip = ctk.CTkButton(
                frame,
                text=f"{emoji} {repo_slug}",
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["accent_soft"],
                hover_color=COLORS["accent_glow"],
                text_color=COLORS["accent"],
                border_width=1,
                border_color=COLORS["accent_glow"],
                corner_radius=14,
                command=lambda s=repo_slug: self._load_sample(s)
            )
            chip.pack(side="left", padx=(0, 6))

    # ── Footer ──────────────────────────────────────────────────────────

    def _build_footer(self, parent):
        """Bottom footer with shortcuts and credits."""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=28, pady=10)

        # Shortcut hints
        shortcuts = ctk.CTkLabel(
            footer,
            text="⌨  Ctrl+Enter = Analyze  ·  Ctrl+H = History  ·  Esc = Clear",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        )
        shortcuts.pack(side="left")

        credits = ctk.CTkLabel(
            footer,
            text="Mohsan Razaq & H. Abdul Rehman",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        )
        credits.pack(side="right")

    # ------------------------------------------------------------------
    # Data / State
    # ------------------------------------------------------------------

    def _update_sidebar(self):
        """Refresh recent repos list and stats in the sidebar."""
        # Stats
        try:
            count = get_record_count()
            self.stats_label.configure(
                text=f" {count} {'analysis' if count == 1 else 'analyses'} saved"
            )
        except Exception:
            pass

        # Recent repos
        for w in self.recent_frame.winfo_children():
            w.destroy()

        try:
            recent = get_recent_repos(limit=6)
            if not recent:
                ctk.CTkLabel(
                    self.recent_frame,
                    text="No history yet",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_muted"],
                    anchor="w"
                ).pack(fill="x", padx=4, pady=2)
            else:
                for row in recent:
                    btn = ctk.CTkButton(
                        self.recent_frame,
                        text=f"  {row['repo_name']}",
                        height=30, anchor="w",
                        font=ctk.CTkFont(size=11),
                        fg_color="transparent",
                        hover_color=COLORS["bg_card_hover"],
                        text_color=COLORS["text_secondary"],
                        corner_radius=6,
                        command=lambda u=row["url"]: self._load_from_history(u)
                    )
                    btn.pack(fill="x", pady=1)
        except Exception:
            pass

    def _load_sample(self, slug):
        """Fill the entry with a sample repo URL and analyze."""
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, f"https://github.com/{slug}")
        self._analyze_repo()

    def _load_from_history(self, url):
        """Fill entry with a previously analyzed URL."""
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self.url_entry.focus_set()

    def _focus_entry(self):
        self.url_entry.focus_set()

    # ------------------------------------------------------------------
    # Loading spinner
    # ------------------------------------------------------------------

    def _start_spinner(self):
        self._loading = True
        self._tick_spinner()

    def _tick_spinner(self):
        if not self._loading:
            return
        char = self._spinner_chars[self._spinner_idx % len(self._spinner_chars)]
        self._spinner_idx += 1
        self.status_label.configure(
            text=f"{char}  Fetching repository data from GitHub API..."
        )
        self.after(80, self._tick_spinner)

    def _stop_spinner(self):
        self._loading = False
        self.status_label.configure(text="")
    def _analyze_repo(self):
        """Validate and analyze a repository in a background thread."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror(
                "Missing URL",
                "Please enter a GitHub repository URL.\n\n"
                "Examples:\n"
                "  • https://github.com/facebook/react\n"
                "  • torvalds/linux"
            )
            return

        self.analyze_btn.configure(state="disabled", text="⏳  Loading...")
        self._start_spinner()

        def _worker():
            data = fetch_repository_data(url)
            self.after(0, lambda: self._on_fetch_complete(data))

        threading.Thread(target=_worker, daemon=True).start()
    # ------------------------------------------------------------------
    # Core actions
    # ------------------------------------------------------------------

    def _search_by_skill(self):
        """Search GitHub for top repos matching the entered skill."""
        skill = self.skill_entry.get().strip()
        if not skill:
            messagebox.showerror("Missing Skill", "Please enter a skill to search.")
            return
        self.current_skill = skill
        repos = search_top_repos_by_skill(skill)
        if not repos:
            messagebox.showinfo("No results", f"No repositories found for skill '{skill}'.")
            return
        # Use the first repo result
        repo_url = repos[0]["html_url"]
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, repo_url)
        self._analyze_repo()

    def _on_fetch_complete(self, data):
        """Handle API response on the main thread."""
        self._stop_spinner()
        self.analyze_btn.configure(state="normal", text="🚀  Analyze")

        if not data:
            messagebox.showerror(
                "Fetch Failed",
                "Could not retrieve repository data.\n\n"
                "Possible reasons:\n"
                "  • Invalid URL or repository not found\n"
                "  • No internet connection\n"
                "  • GitHub API rate limit exceeded (60 req/hr without token)\n\n"
                " Tip: Add GITHUB_TOKEN in .env for 5,000 req/hr"
            )
            return

        win = AnalysisScreen(self, data)
        win.on_saved_callback = self._update_sidebar
        self._update_sidebar()

    def _open_history(self):
        """Open the history window."""
        win = HistoryScreen(self)
        win.on_close_callback = self._update_sidebar