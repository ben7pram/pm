"""Database initialization and management for the kanban app."""
import sqlite3
import json
from pathlib import Path
from typing import Optional

# Database file path (relative to project root)
DB_PATH = Path(__file__).parent.parent / "kanban.db"


def get_db() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_db():
    """Initialize the database: create tables and seed MVP user if needed."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create boards table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            title TEXT NOT NULL DEFAULT 'My Board',
            data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    # Seed MVP user if not present
    cursor.execute("SELECT id FROM users WHERE username = 'user'")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("user", "password"),  # MVP: plain text for now
        )
        user_id = cursor.lastrowid

        # Create a default board with initial columns and cards
        default_board_data = {
            "columns": [
                {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
                {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
                {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
                {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
                {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
            ],
            "cards": {
                "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
                "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
                "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
                "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
                "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
                "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
                "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
                "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."},
            },
        }

        cursor.execute(
            "INSERT INTO boards (user_id, title, data) VALUES (?, ?, ?)",
            (user_id, "My Board", json.dumps(default_board_data)),
        )

    conn.commit()
    conn.close()


def get_user_by_username(username: str) -> Optional[dict]:
    """Retrieve a user by username."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_board_for_user(user_id: int) -> Optional[dict]:
    """Retrieve the board for a given user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, title, data, updated_at FROM boards WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "title": row["title"],
            "data": json.loads(row["data"]),
            "updated_at": row["updated_at"],
        }
    return None


def update_board_for_user(user_id: int, board_data: dict) -> bool:
    """Update the board data for a given user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE boards SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        (json.dumps(board_data), user_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
