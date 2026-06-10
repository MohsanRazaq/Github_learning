"""
Roadmap generator module.
Loads learning roadmaps from a JSON config file instead of hardcoded data.
Calculates difficulty using multiple repository signals.
"""
import json
from pathlib import Path


# Load roadmaps from JSON config
_ROADMAP_FILE = Path(__file__).parent / "roadmaps.json"

try:
    with open(_ROADMAP_FILE, "r", encoding="utf-8") as f:
        _ROADMAPS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _ROADMAPS = {}

# Default roadmap for unknown languages
_DEFAULT_ROADMAP = [
    "Learn the language basics & syntax",
    "Understand package/dependency management",
    "Study testing frameworks for this language",
    "Learn Git & GitHub workflows",
    "Read & understand the repository structure",
    "Start with documentation or small bug fixes",
]


def get_roadmap(language):
    """
    Get a learning roadmap for the given programming language.
    Falls back to a generic roadmap for unsupported languages.
    """
    if not language or language == "Not specified":
        return _DEFAULT_ROADMAP

    # Try exact match first, then case-insensitive
    if language in _ROADMAPS:
        return _ROADMAPS[language]

    for key, value in _ROADMAPS.items():
        if key.lower() == language.lower():
            return value

    return _DEFAULT_ROADMAP


def get_supported_languages():
    """Return list of languages with custom roadmaps."""
    return list(_ROADMAPS.keys())


def get_difficulty(stars, forks=0, open_issues=0, size_kb=0):
    """
    Calculate repository difficulty using multiple signals.
    Returns a tuple: (level_name, score, color_key)
    """
    score = 0

    # Star-based scoring (popularity ≈ complexity)
    if stars < 50:
        score += 1
    elif stars < 500:
        score += 2
    elif stars < 5000:
        score += 3
    else:
        score += 4

    # Fork-based scoring
    if forks > 1000:
        score += 2
    elif forks > 100:
        score += 1

    # Open issues (more issues = more complex project)
    if open_issues > 500:
        score += 2
    elif open_issues > 50:
        score += 1

    # Repository size
    if size_kb > 100000:  # > 100MB
        score += 2
    elif size_kb > 10000:  # > 10MB
        score += 1

    # Determine level
    if score <= 2:
        return "Beginner", score, "difficulty_beginner"
    elif score <= 5:
        return "Intermediate", score, "difficulty_intermediate"
    elif score <= 8:
        return "Advanced", score, "difficulty_advanced"
    else:
        return "Expert", score, "difficulty_advanced"