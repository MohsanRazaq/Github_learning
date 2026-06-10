"""
Database management module.
Handles SQLite operations with proper context managers,
named columns, and duplicate prevention.
"""
import sqlite3
from datetime import datetime
from config import DB_PATH


def _get_connection():
    """Create a database connection with row factory for named access."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """Create the repositories table if it doesn't exist, and migrate old schemas."""
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                owner TEXT NOT NULL,
                description TEXT DEFAULT '',
                language TEXT DEFAULT '',
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                license TEXT DEFAULT '',
                url TEXT UNIQUE,
                analyzed_date TEXT NOT NULL
            )
        """)

        # --- Migration: add columns that may be missing in older databases ---
        existing_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(repositories)").fetchall()
        }
        migrations = {
            "description": "ALTER TABLE repositories ADD COLUMN description TEXT DEFAULT ''",
            "open_issues": "ALTER TABLE repositories ADD COLUMN open_issues INTEGER DEFAULT 0",
            "license": "ALTER TABLE repositories ADD COLUMN license TEXT DEFAULT ''",
        }
        for col_name, alter_sql in migrations.items():
            if col_name not in existing_cols:
                conn.execute(alter_sql)

        conn.commit()


def save_repository(data):
    """
    Save a repository analysis to the database.
    Returns True if saved, False if duplicate.
    """
    with _get_connection() as conn:
        # Check for duplicate
        existing = conn.execute(
            "SELECT id FROM repositories WHERE url = ?",
            (data["url"],)
        ).fetchone()

        if existing:
            # Update instead of duplicate insert
            conn.execute("""
                UPDATE repositories SET
                    repo_name = ?,
                    owner = ?,
                    description = ?,
                    language = ?,
                    stars = ?,
                    forks = ?,
                    open_issues = ?,
                    license = ?,
                    analyzed_date = ?
                WHERE url = ?
            """, (
                data["repo_name"],
                data["owner"],
                data.get("description", ""),
                data.get("language", ""),
                data.get("stars", 0),
                data.get("forks", 0),
                data.get("open_issues", 0),
                data.get("license", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data["url"],
            ))
            conn.commit()
            return False  # Updated, not new

        conn.execute("""
            INSERT INTO repositories (
                repo_name, owner, description, language,
                stars, forks, open_issues, license,
                url, analyzed_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["repo_name"],
            data["owner"],
            data.get("description", ""),
            data.get("language", ""),
            data.get("stars", 0),
            data.get("forks", 0),
            data.get("open_issues", 0),
            data.get("license", ""),
            data["url"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return True  # New record


def get_history(search_query="", language_filter=""):
    """
    Fetch analysis history with optional search and language filter.
    Returns list of sqlite3.Row objects (supports named access).
    """
    with _get_connection() as conn:
        query = """
            SELECT id, repo_name, owner, description, language,
                   stars, forks, open_issues, license, url, analyzed_date
            FROM repositories
        """
        conditions = []
        params = []

        if search_query:
            conditions.append(
                "(repo_name LIKE ? OR owner LIKE ? OR description LIKE ?)"
            )
            like = f"%{search_query}%"
            params.extend([like, like, like])

        if language_filter:
            conditions.append("language = ?")
            params.append(language_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC"

        return conn.execute(query, params).fetchall()


def get_all_languages():
    """Get list of distinct languages from saved repos."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT language FROM repositories WHERE language != '' ORDER BY language"
        ).fetchall()
        return [row["language"] for row in rows]


def delete_record(record_id):
    """Delete a repository record by ID."""
    with _get_connection() as conn:
        conn.execute(
            "DELETE FROM repositories WHERE id = ?",
            (record_id,)
        )
        conn.commit()


def get_record_count():
    """Get total number of saved analyses."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as count FROM repositories"
        ).fetchone()
        return row["count"] if row else 0


def get_recent_repos(limit=5):
    """Get the most recently analyzed repositories."""
    with _get_connection() as conn:
        return conn.execute(
            "SELECT repo_name, owner, language, stars, url "
            "FROM repositories ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()


def get_top_languages(limit=5):
    """Get the most common languages from saved repos."""
    with _get_connection() as conn:
        return conn.execute(
            "SELECT language, COUNT(*) as cnt "
            "FROM repositories WHERE language != '' "
            "GROUP BY language ORDER BY cnt DESC LIMIT ?",
            (limit,)
        ).fetchall()