"""
Central configuration module.
Loads settings from .env file and provides project-wide constants.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Project root directory (where main.py lives)
PROJECT_ROOT = Path(__file__).parent

# Load .env from project root
env_path = PROJECT_ROOT / ".env"
if load_dotenv and env_path.exists():
    load_dotenv(env_path)

# --- GitHub API ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_API_BASE = "https://api.github.com"

# --- Database ---
DB_PATH = PROJECT_ROOT / os.getenv("DB_PATH", "database.db")

# --- Export directory ---
EXPORT_DIR = PROJECT_ROOT / "exports"

# --- App Appearance ---
APP_THEME = os.getenv("APP_THEME", "dark").lower()

# --- Colors (Premium Dark Theme) ---
COLORS = {
    # Backgrounds
    "bg_primary": "#0d0d1a",
    "bg_secondary": "#151528",
    "bg_card": "#1a1a35",
    "bg_card_hover": "#222250",
    "bg_input": "#12122a",

    # Accent palette
    "accent": "#7c6cff",
    "accent_hover": "#9488ff",
    "accent_glow": "#9b86ff",
    "accent_soft": "#c5b3ff",

    # Semantic colors
    "success": "#00e676",
    "success_soft": "#00e67620",
    "warning": "#ffab40",
    "warning_soft": "#ffab4020",
    "danger": "#ff5252",
    "danger_soft": "#ff525220",
    "info": "#40c4ff",
    "info_soft": "#40c4ff20",

    # Text
    "text_primary": "#eaeaf5",
    "text_secondary": "#a8a8c8",
    "text_muted": "#65658a",
    "text_link": "#82b1ff",

    # Borders & separators
    "border": "#2a2a50",
    "border_light": "#35356a",
    "separator": "#1e1e3a",

    # Difficulty
    "difficulty_beginner": "#00e676",
    "difficulty_intermediate": "#ffab40",
    "difficulty_advanced": "#ff5252",

    # Progress bar backgrounds
    "progress_bg": "#1a1a35",
    "progress_track": "#252548",

    # Row alternating
    "row_even": "#1a1a35",
    "row_odd": "#161630",
}

# --- Sample repos for quick-access ---
SAMPLE_REPOS = [
    ("facebook/react", ""),
    ("torvalds/linux", ""),
    ("microsoft/vscode", ""),
    ("flutter/flutter", ""),
    ("python/cpython", ""),
]

# --- App info ---
APP_NAME = "GitHub Learning Assistant"
APP_VERSION = "2.0"
