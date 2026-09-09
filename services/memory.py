import sqlite3
from pathlib import Path


DB_PATH = Path("data/memory.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DB_PATH)


def initialize_memory():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            preferred_make TEXT,
            preferred_model TEXT,
            min_year INTEGER,
            max_year INTEGER,
            budget REAL
        )
    """)

    connection.commit()
    connection.close()


def save_message(user_id, role, message):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO messages (user_id, role, message)
        VALUES (?, ?, ?)
        """,
        (user_id, role, message)
    )

    connection.commit()
    connection.close()


def get_recent_messages(user_id, limit=10):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT role, message
        FROM messages
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()

    connection.close()

    return list(reversed(rows))


def save_preferences(
    user_id,
    name=None,
    preferred_make=None,
    preferred_model=None,
    min_year=None,
    max_year=None,
    budget=None
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO user_preferences
        (user_id, name, preferred_make, preferred_model,
         min_year, max_year, budget)

        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            name = COALESCE(excluded.name, user_preferences.name),
            preferred_make = COALESCE(
                excluded.preferred_make,
                user_preferences.preferred_make
            ),
            preferred_model = COALESCE(
                excluded.preferred_model,
                user_preferences.preferred_model
            ),
            min_year = COALESCE(
                excluded.min_year,
                user_preferences.min_year
            ),
            max_year = COALESCE(
                excluded.max_year,
                user_preferences.max_year
            ),
            budget = COALESCE(
                excluded.budget,
                user_preferences.budget
            )
        """,
        (
            user_id,
            name,
            preferred_make,
            preferred_model,
            min_year,
            max_year,
            budget
        )
    )

    connection.commit()
    connection.close()


def get_preferences(user_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            name,
            preferred_make,
            preferred_model,
            min_year,
            max_year,
            budget
        FROM user_preferences
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    if not row:
        return {}

    return {
        "name": row[0],
        "preferred_make": row[1],
        "preferred_model": row[2],
        "min_year": row[3],
        "max_year": row[4],
        "budget": row[5]
    }