"""Security characterization tests.

These tests document CURRENT (insecure) behavior so a fix is detectable as a
change. They pass today; they should FAIL once the vulnerabilities are fixed.
Cartographer should flag the underlying issues with citations.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import auth  # noqa: E402
import db    # noqa: E402


def fresh_conn():
    conn = db.get_conn()
    db.init_db(conn)
    return conn


def test_login_is_injectable_today():
    """A classic ' OR '1'='1 payload currently bypasses the password check."""
    conn = fresh_conn()
    user = auth.authenticate(conn, "alice", "' OR '1'='1")
    assert user is not None  # <-- this is the bug, captured as a test


def test_passwords_stored_in_plaintext_today():
    conn = fresh_conn()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = 'alice'")
    assert cur.fetchone()["password"] == "password123"  # not hashed
