# TaskVault

A tiny task-tracking web service with user accounts. Users can log in and manage
their own tasks; admins can view all tasks.

## Run
```bash
python server.py            # serves on http://localhost:8080
```

## Test
```bash
pytest -q
```

## Layout
- `auth.py`   — user authentication and session tokens
- `db.py`     — SQLite storage and seed data
- `server.py` — HTTP routes
- `tests/`    — test suite

## Seed accounts
- `alice` / `password123` (user)
- `admin` / `admin` (admin)
