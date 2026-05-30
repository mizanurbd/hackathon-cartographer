# Planted issues (DO NOT show judges — your demo answer key)

This file is the cheat-sheet of bugs deliberately planted in TaskVault so you
can confirm Cartographer finds them. Delete or git-ignore before pushing if you
don't want it visible.

1. **SQL injection** in `auth.py:authenticate` — query is built with f-string
   concatenation (`auth.py` ~L16-20). Bypass: password `' OR '1'='1`.
   Covered by `tests/test_security.py::test_login_is_injectable_today`.
2. **Plaintext passwords** — `db.py` seeds raw passwords; `auth.py` compares
   them directly. Covered by `test_passwords_stored_in_plaintext_today`.
3. **Hardcoded secret** — `auth.py:SECRET_KEY` (L11) committed in source.
4. **Weak session tokens** — `make_session_token` uses MD5 over a guessable
   `user:timestamp:secret` (`auth.py` ~L24-28); no real signing/expiry.
5. **Broken access control** — `GET /admin/tasks` in `server.py` returns ALL
   tasks with **no authentication/role check** (`server.py` ~L46-52).
6. **Debug mode on** — advertised in `server.py:main` banner.

Good demo question:
> "How does authentication work end-to-end, and what are the top security
>  risks? Verify each by running the tests."

Expected: Cartographer maps login flow, flags ≥4 of the above WITH `file:line`
citations, and runs `pytest` to show the security characterization tests pass.
