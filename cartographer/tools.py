"""Citation-aware tools given to sub-agents.

Every tool returns results tagged with `path:Lstart-Lend` so the agent can
cite exactly where a claim comes from. Tools operate ONLY inside the repo
under investigation (path traversal is rejected).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from agents import function_tool

from .config import SETTINGS


# ----------------------------- helpers --------------------------------------

def _resolve_in_repo(rel_path: str) -> Path:
    """Resolve a path and ensure it stays inside the target repo."""
    repo = SETTINGS.repo_path.resolve()
    target = (repo / rel_path).resolve()
    if repo not in target.parents and target != repo:
        raise ValueError(f"Refusing to access path outside repo: {rel_path}")
    return target


def _is_blocked(command: str) -> bool:
    low = command.lower()
    return any(b in low for b in SETTINGS.blocked_command_substrings)


# ----------------------------- tools ----------------------------------------

@function_tool
def list_tree(subdir: str = ".", max_entries: int = 200) -> str:
    """List files/dirs under a repo subdirectory (recursive, capped).

    Use this first to orient yourself in an unfamiliar repo.
    """
    base = _resolve_in_repo(subdir)
    if not base.exists():
        return f"[not found] {subdir}"
    out: list[str] = []
    for p in sorted(base.rglob("*")):
        # skip noise
        parts = set(p.parts)
        if parts & {".git", "node_modules", ".venv", "__pycache__", "dist", "build"}:
            continue
        out.append(str(p.relative_to(SETTINGS.repo_path)))
        if len(out) >= max_entries:
            out.append(f"... (truncated at {max_entries})")
            break
    return "\n".join(out) or "[empty]"


@function_tool
def read_file(path: str, start_line: int = 1, end_line: int = 400) -> str:
    """Read a file with line numbers so you can cite `path:Lstart-Lend`.

    Always cite the exact lines you rely on in your findings.
    """
    target = _resolve_in_repo(path)
    if not target.is_file():
        return f"[not a file] {path}"
    try:
        lines = target.read_text(errors="replace").splitlines()
    except Exception as e:  # noqa: BLE001
        return f"[read error] {path}: {e}"
    start = max(1, start_line)
    end = min(len(lines), end_line)
    body = "\n".join(f"{i:>5}: {lines[i-1]}" for i in range(start, end + 1))
    header = f"# {path}:L{start}-L{end} (of {len(lines)} lines)\n"
    return header + body


@function_tool
def grep(pattern: str, glob: str = "*", max_results: int = 60) -> str:
    """Search the repo for a regex pattern. Returns `path:line: match` rows.

    Great for locating where a symbol/route/config is defined or used.
    """
    cmd = ["grep", "-rniE", "--include", glob, pattern, str(SETTINGS.repo_path)]
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=SETTINGS.command_timeout_s
        )
    except subprocess.TimeoutExpired:
        return "[grep timed out]"
    rows = res.stdout.splitlines()[:max_results]
    repo = str(SETTINGS.repo_path) + "/"
    rows = [r.replace(repo, "") for r in rows]
    return "\n".join(rows) or f"[no matches for /{pattern}/]"


@function_tool
def run_command(command: str) -> str:
    """Run a shell command INSIDE the repo to verify a hypothesis.

    Use to run tests, reproduce a bug, check versions, trace behavior, etc.
    Destructive/networked commands are blocked. Output is truncated.
    """
    if _is_blocked(command):
        return f"[blocked command] refused: {command!r}"
    try:
        res = subprocess.run(
            command,
            shell=True,
            cwd=str(SETTINGS.repo_path),
            capture_output=True,
            text=True,
            timeout=SETTINGS.command_timeout_s,
        )
    except subprocess.TimeoutExpired:
        return f"[timeout after {SETTINGS.command_timeout_s}s] {command}"
    out = (res.stdout or "") + (("\n[stderr]\n" + res.stderr) if res.stderr else "")
    out = out.strip()
    if len(out) > 6000:
        out = out[:6000] + "\n... (truncated)"
    return f"$ {command}\n[exit {res.returncode}]\n{out or '[no output]'}"


# Tools every investigation sub-agent gets.
SUBAGENT_TOOLS = [list_tree, read_file, grep, run_command]
