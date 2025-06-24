import sqlite3
from pathlib import Path

DB_PATH = Path('data') / 'bot.db'


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                used_tasks INTEGER DEFAULT 0,
                subscribed INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exitpoll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_user(user_id: int) -> tuple[int, int]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT used_tasks, subscribed FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        if row is None:
            conn.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            return 0, 0
        return row


def increment_tasks(user_id: int) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (user_id, used_tasks) VALUES (?, 1) "
            "ON CONFLICT(user_id) DO UPDATE SET used_tasks = used_tasks + 1",
            (user_id,),
        )
        cur = conn.execute(
            "SELECT used_tasks FROM users WHERE user_id = ?",
            (user_id,),
        )
        return cur.fetchone()[0]


def subscribe_user(user_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (user_id, subscribed) VALUES (?, 1) "
            "ON CONFLICT(user_id) DO UPDATE SET subscribed = 1",
            (user_id,),
        )


def record_exitpoll(user_id: int, reason: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO exitpoll (user_id, reason) VALUES (?, ?)",
            (user_id, reason),
        )


def exitpoll_stats() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            SELECT reason, COUNT(*) FROM exitpoll
            WHERE ts >= datetime('now', '-1 day')
            GROUP BY reason
            """
        )
        return dict(cur.fetchall())
