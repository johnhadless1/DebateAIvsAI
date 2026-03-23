import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import os


class ConversationMemory:
    """Stores all messages in a SQLite database."""

    def __init__(self, db_path: str = "./database/conversation.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create the database and messages table if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id        INTEGER PRIMARY KEY,
                    author    TEXT,
                    content   TEXT,
                    timestamp TEXT,
                    is_ai     INTEGER
                )
            ''')
            conn.commit()

    def add_message(self, author: str, content: str, is_ai: bool = False):
        """Persist a message to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO messages (author, content, timestamp, is_ai) VALUES (?, ?, ?, ?)',
                (author, content, datetime.now().isoformat(), int(is_ai))
            )
            conn.commit()

    def get_recent_messages(self, limit: int = 20) -> List[Dict]:
        """Return the last *limit* messages in chronological order."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                'SELECT author, content, timestamp, is_ai FROM messages ORDER BY id DESC LIMIT ?',
                (limit,)
            ).fetchall()

        return [
            {"author": author, "content": content, "timestamp": ts, "is_ai": bool(is_ai)}
            for author, content, ts, is_ai in reversed(rows)
        ]

    def save_to_file(self, filename: str):
        """Export the full conversation history to a JSON file."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                'SELECT author, content, timestamp, is_ai FROM messages'
            ).fetchall()

        messages = [
            {"author": a, "content": c, "timestamp": ts, "is_ai": bool(ai)}
            for a, c, ts, ai in rows
        ]

        with open(filename, "w") as f:
            json.dump(messages, f, indent=2)

        print(f"✅ Saved {len(messages)} messages to {filename}")

    def clear(self):
        """Delete all messages from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM messages')
            conn.commit()
        print("🗑️  Conversation history cleared.")
