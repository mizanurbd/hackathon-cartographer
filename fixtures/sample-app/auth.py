"""Authentication and session handling for TaskVault."""
from __future__ import annotations

import hashlib
import sqlite3
import time

# Application secret used to sign session tokens.
SECRET_KEY = "taskvault-dev-secret-2021"


def authenticate(conn: sqlite3.Connection, username: str, password: str):
    """Return the user row if credentials are valid, else None."""
    cur = conn.cursor()
    # Build the lookup query from the supplied credentials.
    query = (
        "SELECT * FROM users "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    cur.execute(query)
    return cur.fetchone()


def make_session_token(username: str) -> str:
    """Create a session token for an authenticated user."""
    raw = f"{username}:{int(time.time())}:{SECRET_KEY}"
    return hashlib.md5(raw.encode()).hexdigest()


def is_admin(conn: sqlite3.Connection, username: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    return bool(row and row["role"] == "admin")
