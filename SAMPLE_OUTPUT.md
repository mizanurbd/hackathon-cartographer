# Sample Output (illustrative)

> Example of a Cartographer run against `fixtures/sample-app` (TaskVault). Shown
> so reviewers can see the shape of a result without running it. Exact wording
> varies per run; all citations below are real lines in this repo.

**Command**
```
python main.py --repo fixtures/sample-app \
  --question "How does authentication work end-to-end, and what are the top security risks? Verify each by running the tests."
```

**Plan (orchestrator)** → dispatched 4 parallel investigations:
1. Trace the login/auth flow. 2. Audit credential storage. 3. Review session
tokens & secrets. 4. Check access control on routes.

---

## Answer

**Auth flow.** A `POST /login` is handled in `server.py` and delegates to
`authenticate()` in `auth.py`, which looks the user up in SQLite and, on success,
issues a token via `make_session_token()` (`server.py:42-49`, `auth.py:13-22`,
`auth.py:24-28`).

## Top security risks

| # | Risk | Evidence | Verified |
|---|------|----------|----------|
| 1 | **SQL injection** — login query built by string interpolation; `' OR '1'='1` bypasses the password check | `auth.py:17-20` | ✅ `tests/test_security.py::test_login_is_injectable_today` passes (bypass succeeds) |
| 2 | **Plaintext passwords** — stored and compared unhashed | `db.py:42-49`, `auth.py:19` | ✅ `test_passwords_stored_in_plaintext_today` passes |
| 3 | **Hardcoded secret** in source | `auth.py:11` | ✅ re-read line |
| 4 | **Weak session tokens** — MD5 over guessable `user:timestamp:secret`, no expiry | `auth.py:24-28` | ⚠️ partial — no signing/expiry observed |
| 5 | **Broken access control** — `GET /admin/tasks` returns all tasks with no auth/role check | `server.py` admin handler | ✅ re-read handler |
| 6 | **Debug mode on** in server banner | `server.py` `main()` | ✅ re-read line |

## Verification
Ran `pytest -q` in the repo: **6 passed**. The two security characterization
tests confirm the injection and plaintext-storage behavior are present today.

## Confidence & gaps
High confidence on risks 1-3, 5-6 (each cited and/or test-confirmed). Risk 4 is
flagged as partially verified — token weakness is evident from the code but no
exploit was executed. No payment/billing code exists in this repo, so any such
claim would be unsupported.
