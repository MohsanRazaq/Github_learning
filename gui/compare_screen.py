"""
Compare Screen — Displays a side-by-side comparison matrix for two or more repositories.
"""
import customtkinter as ctk
from config import COLORS
from roadmap.roadmap_generator import get_difficulty

class CompareScreen(ctk.CTkToplevel):

    def __init__(self, parent, repos_data):
        super().__init__(parent)

        self.parent = parent
        self.repos = repos_data

        self.title("Repository Comparison Matrix")
        self.geometry("960x550")
        self.minsize(800, 450)
        self.configure(fg_color=COLORS["bg_primary"])

        # Make window modal and focus
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        # --- Title ---
        title_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        ctk.CTkLabel(
            title_frame,
            text="⚖️  Repository Comparison Dashboard",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            title_frame,
            text=f"Comparing {len(self.repos)} repositories",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        ).pack(side="right", padx=20)

        # --- Content Container ---
        scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # We will build a grid layout.
        # Column 0: Metric Names
        # Column 1..N: Repo values
        num_repos = len(self.repos)
        
        # Configure columns
        scroll_frame.grid_columnconfigure(0, weight=2, minsize=180)
        for c in range(1, num_repos + 1):
            scroll_frame.grid_columnconfigure(c, weight=3, minsize=180)

        # Metrics lists
        # Format: (label, key_name, formatter_func, type_for_comparison)
        
        def format_size(size_kb):
            if not size_kb:
                return "0 KB"
            if size_kb >= 1024 * 1024:
                return f"{size_kb / (1024 * 1024):.2f} GB"
            elif size_kb >= 1024:
                return f"{size_kb / 1024:.1f} MB"
            return f"{size_kb} KB"

        def get_diff_text(repo):
            diff_name, score, _ = get_difficulty(
                repo.get("stars", 0),
                repo.get("forks", 0),
                repo.get("open_issues", 0),
                repo.get("size_kb", 0)
            )
            return f"{diff_name} (Score: {score}/10)"

        def get_diff_score(repo):
            _, score, _ = get_difficulty(
                repo.get("stars", 0),
                repo.get("forks", 0),
                repo.get("open_issues", 0),
                repo.get("size_kb", 0)
            )
            return score

        metrics = [
            ("Repository", "repo_name", lambda r: f"{r['owner']}/{r['repo_name']}", None),
            ("Primary Language", "language", lambda r: r.get("language") or "Not specified", None),
            ("Difficulty Level", "difficulty", get_diff_text, get_diff_score),
            ("Stars", "stars", lambda r: f"⭐ {r.get('stars', 0):,}", lambda r: r.get("stars", 0)),
            ("Forks", "forks", lambda r: f"🍴 {r.get('forks', 0):,}", lambda r: r.get("forks", 0)),
            ("Open Issues", "open_issues", lambda r: f"📋 {r.get('open_issues', 0):,}", lambda r: r.get("open_issues", 0)),
            ("Watchers", "watchers", lambda r: f"👁️ {r.get('watchers', 0):,}", lambda r: r.get("watchers", 0)),
            ("Size", "size_kb", lambda r: f"💾 {format_size(r.get('size_kb', 0))}", lambda r: r.get("size_kb", 0)),
            ("License", "license", lambda r: r.get("license") or "None", None),
            ("Learning Progress", "progress", lambda r: f"📈 {r.get('progress_percentage', 0)}%", lambda r: r.get("progress_percentage", 0)),
        ]

        # Determine best/worst values for highlights (highest stars/forks/progress, lowest difficulty/issues)
        best_indices = {}
        for label, key_name, _, comparer in metrics:
            if comparer is None:
                continue
            
            vals = [comparer(r) for r in self.repos]
            if not vals:
                continue

            if key_name in ["stars", "forks", "watchers", "progress"]:
                # Higher is better
                max_val = max(vals)
                best_indices[key_name] = [i for i, v in enumerate(vals) if v == max_val]
            elif key_name in ["open_issues", "difficulty", "size_kb"]:
                # Lower is better (excluding size=0 which usually means unrecorded)
                valid_vals = [v for v in vals if v > 0]
                if valid_vals:
                    min_val = min(valid_vals)
                    best_indices[key_name] = [i for i, v in enumerate(vals) if v == min_val]

        # Draw Table Headers
        hdr_lbl = ctk.CTkLabel(
            scroll_frame, text="Metric",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_muted"], anchor="w"
        )
        hdr_lbl.grid(row=0, column=0, padx=12, pady=10, sticky="w")
        
        for idx, repo in enumerate(self.repos):
            title_lbl = ctk.CTkLabel(
                scroll_frame, text=repo["repo_name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["accent"], anchor="center"
            )
            title_lbl.grid(row=0, column=idx + 1, padx=10, pady=10, sticky="ew")

        # Draw Grid Rows
        for r_idx, (label, key_name, formatter, comparer) in enumerate(metrics, start=1):
            # Row shading background frame
            row_bg = COLORS["row_even"] if r_idx % 2 == 0 else COLORS["row_odd"]
            
            # Draw row background frames
            f_metric = ctk.CTkFrame(scroll_frame, fg_color=row_bg, corner_radius=6, height=36)
            f_metric.grid(row=r_idx, column=0, columnspan=num_repos + 1, sticky="nsew", pady=2)
            f_metric.grid_columnconfigure(0, weight=2, minsize=180)
            for c in range(1, num_repos + 1):
                f_metric.grid_columnconfigure(c, weight=3, minsize=180)

            # Metric Label
            lbl = ctk.CTkLabel(
                f_metric, text=f"  {label}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"], anchor="w"
            )
            lbl.grid(row=0, column=0, padx=12, pady=6, sticky="w")

            # Repository values
            for idx, repo in enumerate(self.repos):
                val_text = formatter(repo)
                
                # Check for highlight
                is_best = False
                if key_name in best_indices and idx in best_indices[key_name]:
                    is_best = True

                t_color = COLORS["success"] if is_best and key_name != "repo_name" else COLORS["text_primary"]
                weight_val = "bold" if is_best or key_name == "repo_name" else "normal"

                val_lbl = ctk.CTkLabel(
                    f_metric, text=val_text,
                    font=ctk.CTkFont(size=12, weight=weight_val),
                    text_color=t_color, anchor="center"
                )
                val_lbl.grid(row=0, column=idx + 1, padx=10, pady=6, sticky="ew")

        # --- Close Button ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(
            btn_frame, text="Close Comparison",
            width=150, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            command=self.destroy
        ).pack(side="right")
