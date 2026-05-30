"""Minimal stdlib HTTP server for TaskVault (no external deps)."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import auth
import db

CONN = db.get_conn()
db.init_db(CONN)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode()
        form = {k: v[0] for k, v in parse_qs(raw).items()}

        if self.path == "/login":
            user = auth.authenticate(CONN, form.get("username", ""), form.get("password", ""))
            if user:
                token = auth.make_session_token(user["username"])
                return self._send(200, {"token": token, "role": user["role"]})
            return self._send(401, {"error": "invalid credentials"})

        self._send(404, {"error": "not found"})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/admin/tasks":
            # Return all tasks for the admin dashboard.
            cur = CONN.cursor()
            cur.execute("SELECT * FROM tasks")
            rows = [dict(r) for r in cur.fetchall()]
            return self._send(200, {"tasks": rows})

        self._send(404, {"error": "not found"})


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("TaskVault on http://localhost:8080 (debug=on)")
    server.serve_forever()


if __name__ == "__main__":
    main()
