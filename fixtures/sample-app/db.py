"""SQLite storage for TaskVault."""
from __future__ import annotations

import sqlite3


def get_conn(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,      -- NOTE: stored as-is
            role TEXT NOT NULL DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            owner TEXT NOT NULL,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()
    seed(conn)


def seed(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM users")
    if cur.fetchone()["n"] > 0:
        return
    cur.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        [
            ("alice", "password123", "user"),
            ("bob", "hunter2", "user"),
            ("admin", "admin", "admin"),
        ],
    )
    cur.executemany(
        "INSERT INTO tasks (owner, title, done) VALUES (?, ?, ?)",
        [("alice", "Write report", 0), ("bob", "Review PR", 1)],
    )
    conn.commit()
