import sqlite3
from datetime import datetime

DB_NAME = "database.db"


def create_table():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repositories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_name TEXT,
        owner TEXT,
        language TEXT,
        stars INTEGER,
        forks INTEGER,
        url TEXT,
        analyzed_date TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_repository(data):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO repositories(
        repo_name,
        owner,
        language,
        stars,
        forks,
        url,
        analyzed_date
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        data["repo_name"],
        data["owner"],
        data["language"],
        data["stars"],
        data["forks"],
        data["url"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_history():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM repositories
    ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def delete_record(record_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM repositories WHERE id=?",
        (record_id,)
    )

    conn.commit()
    conn.close()