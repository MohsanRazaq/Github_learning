"""
Code Explorer Screen — Browse repository directories and preview source code files.
Uses the GitHub Git Trees API to fetch files recursively and downloads previews dynamically.
"""
import os
import threading
import requests
import customtkinter as ctk
from tkinter import ttk, messagebox
from config import COLORS, GITHUB_API_BASE, GITHUB_TOKEN


class CodeExplorerScreen(ctk.CTkToplevel):

    def __init__(self, parent, owner, repo, default_branch="main"):
        super().__init__(parent)

        self.owner = owner
        self.repo = repo
        self.branch = default_branch or "main"

        self.title(f"Code Explorer — {owner}/{repo}")
        self.geometry("1000x650")
        self.minsize(800, 500)
        self.configure(fg_color=COLORS["bg_primary"])

        # Make the window appear as a normal top-level (no modal grab)
        # self.transient(parent)  # Disabled to avoid grab errors when parent is not viewable
        # self.grab_set()       # Disabled modal behavior


        self._setup_treeview_style()
        self._create_widgets()
        
        # Load directory structure in background
        self._load_tree_data()

    def _setup_treeview_style(self):
        """Configure the ttk.Treeview style for the explorer sidebar."""
        style = ttk.Style(self)
        style.configure("Explorer.Treeview",
            background=COLORS["bg_card"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_card"],
            borderwidth=0,
            font=("Segoe UI", 11),
            rowheight=26
        )
        style.configure("Explorer.Treeview.Heading",
            background=COLORS["bg_secondary"],
            foreground=COLORS["text_primary"],
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )
        style.map("Explorer.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")]
        )

    def _create_widgets(self):
        # --- Top Header ---
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=0, height=55)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"📂  Code Explorer: {self.owner}/{self.repo}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=10)

        # Status Label is stored on self so we can update it
        self.status_lbl = ctk.CTkLabel(
            header,
            text="Initializing...",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.status_lbl.pack(side="right", padx=20)

        # --- Main Layout Splitter ---
        main_pane = ctk.CTkFrame(self, fg_color="transparent")
        main_pane.pack(fill="both", expand=True, padx=15, pady=15)

        # Left Container (Tree Explorer)
        left_container = ctk.CTkFrame(main_pane, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"], width=320)
        left_container.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_container.pack_propagate(False)

        # Treeview Header Label
        ctk.CTkLabel(
            left_container, text="Workspace Files",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Files Treeview
        self.tree = ttk.Treeview(
            left_container,
            show="tree",
            style="Explorer.Treeview"
        )
        self.tree.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self._on_item_select)

        # Right Container (File Previewer)
        right_container = ctk.CTkFrame(main_pane, fg_color="transparent")
        right_container.pack(side="left", fill="both", expand=True)

        # File Preview Header
        self.preview_header = ctk.CTkFrame(right_container, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"], height=45)
        self.preview_header.pack(fill="x", pady=(0, 10))
        self.preview_header.pack_propagate(False)

        self.file_name_label = ctk.CTkLabel(
            self.preview_header,
            text="Select a file to preview",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.file_name_label.pack(side="left", padx=15, pady=8)

        self.file_size_label = ctk.CTkLabel(
            self.preview_header,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.file_size_label.pack(side="right", padx=15, pady=8)

        # Text Code Box
        self.code_text = ctk.CTkTextbox(
            right_container,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
            corner_radius=12
        )
        self.code_text.pack(fill="both", expand=True)
        self.code_text.configure(state="disabled")

    def _get_headers(self):
        """Prepare GitHub request headers."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
        return headers

    def _load_tree_data(self):
        """Initiate background thread to load folder structure."""
        # Insert a loading row
        self.tree.insert("", "end", text="⏳ Loading directory structure...")

        def _worker():
            # Get default branch tree recursively
            url = f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
            try:
                resp = requests.get(url, headers=self._get_headers(), timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    self.after(0, lambda: self._populate_tree(data))
                else:
                    self.after(0, lambda: self._on_error(f"GitHub API error (Code: {resp.status_code})"))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _populate_tree(self, data):
        """Clear loading indicator and render files recursively in the treeview."""
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        items = data.get("tree", [])
        if not items:
            self.tree.insert("", "end", text="⚠️ Empty Repository")
            self.status_lbl.configure(text="Empty Repository")
            return

        # Sort items: folders first, then alphabetically
        items = sorted(items, key=lambda x: (0 if x["type"] == "tree" else 1, x["path"]))

        nodes = {"": ""} # Map path strings to treeview node IDs

        for item in items:
            path = item["path"]
            type_ = item["type"]
            size = item.get("size", 0)

            # Determine name and parent folder path
            parts = path.split("/")
            name = parts[-1]
            parent_path = "/".join(parts[:-1])

            # Retrieve parent node ID
            parent_node = nodes.get(parent_path, "")

            # Set emoji/icon
            icon = "📁 " if type_ == "tree" else "📄 "

            # Insert node
            node_id = self.tree.insert(
                parent_node, "end",
                text=f"{icon}{name}",
                values=(path, type_, size)
            )

            # Keep reference if this is a directory
            if type_ == "tree":
                nodes[path] = node_id

        self.status_lbl.configure(text=f"{len(items)} items found")

    def _on_error(self, message):
        """Display error banner inside Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", text=f"❌ Load Failed: {message}")
        self.status_lbl.configure(text="Loading failed")
        messagebox.showerror("Connection Error", f"Could not load repository structure:\n{message}")

    def _on_item_select(self, event):
        """Triggered when user clicks a node in the tree."""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        if not values:
            return

        path, type_, size = values[0], values[1], values[2]

        if type_ == "tree":
            # Don't preview directories
            return

        # Handle file selection
        self._preview_file(path, size)

    def _preview_file(self, path, size):
        """Download and preview selected file text content."""
        # Format size display
        size_lbl = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} Bytes"
        
        self.file_name_label.configure(text=f"📄 {path}")
        self.file_size_label.configure(text=size_lbl)

        # Check for binary file extensions to avoid garbled viewing
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz',
            '.exe', '.dll', '.so', '.bin', '.woff', '.woff2', '.ttf', '.eot',
            '.mp4', '.mp3', '.db', '.sqlite', '.pyc', '.class', '.o'
        }
        _, ext = os.path.splitext(path)
        if ext.lower() in binary_extensions or size > 1024 * 1024 * 2: # Limit to 2MB previews
            self.code_text.configure(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert(
                "1.0",
                f"❌ Cannot preview binary or extremely large file: {path}\n\n"
                f"File size: {size_lbl}\n"
                f"Please inspect this file directly on GitHub."
            )
            self.code_text.configure(state="disabled")
            return

        # Show loading text
        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", "⏳ Fetching file content from GitHub raw servers...")
        self.code_text.configure(state="disabled")

        def _fetch():
            url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    text_content = resp.text
                    self.after(0, lambda: self._update_preview_text(text_content))
                else:
                    self.after(0, lambda: self._update_preview_text(f"❌ Failed to fetch file: HTTP {resp.status_code}"))
            except Exception as e:
                self.after(0, lambda: self._update_preview_text(f"❌ Error fetching file:\n{str(e)}"))

        threading.Thread(target=_fetch, daemon=True).start()

    def _update_preview_text(self, content):
        """Update code textbox content safely."""
        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", content)
        self.code_text.configure(state="disabled")
