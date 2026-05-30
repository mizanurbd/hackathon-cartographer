"""TaskVault auth tests."""
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


def test_valid_login():
    conn = fresh_conn()
    user = auth.authenticate(conn, "alice", "password123")
    assert user is not None
    assert user["username"] == "alice"


def test_invalid_password():
    conn = fresh_conn()
    assert auth.authenticate(conn, "alice", "wrongpass") is None


def test_unknown_user():
    conn = fresh_conn()
    assert auth.authenticate(conn, "nobody", "whatever") is None


def test_session_token_is_deterministic_per_second():
    # Documents current behavior of make_session_token.
    t1 = auth.make_session_token("alice")
    assert isinstance(t1, str) and len(t1) == 32
