"""
GitHub Learning Assistant — Main Entry Point
A desktop application to analyze GitHub repositories,
generate learning roadmaps, and track analysis history.
"""
import sys
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import create_table
from gui.home_screen import HomeScreen


def main():
    """Initialize database and launch the application."""
    create_table()

    app = HomeScreen()
    app.mainloop()


if __name__ == "__main__":
    main()