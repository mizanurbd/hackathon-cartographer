"""Modal execution backend — run commands in an isolated sandbox.

When `--backend modal`, `tools.run_command` routes here so sub-agents execute
code off your machine, in parallel-capable Modal sandboxes. The target repo is
baked into the sandbox image so the agent's commands (tests, repros) run against
the real code.

Requires: `modal token new` (after redeeming credits). Smoke-test first:
    modal run modal_app.py
"""
from __future__ import annotations

from .config import SETTINGS

_sandbox = None  # reused across calls in one process


def _get_sandbox():
    global _sandbox
    if _sandbox is not None:
        return _sandbox

    import modal

    app = modal.App.lookup("cartographer", create_if_missing=True)
    image = (
        modal.Image.debian_slim()
        .apt_install("git", "ripgrep")
        .pip_install("pytest")
        # Bake the repo under investigation into the sandbox at /work.
        .add_local_dir(str(SETTINGS.repo_path), remote_path="/work", copy=True)
    )
    _sandbox = modal.Sandbox.create(app=app, image=image, timeout=600)
    return _sandbox


def run_command_modal(command: str) -> str:
    """Execute `command` inside the Modal sandbox (cwd = repo root)."""
    sb = _get_sandbox()
    proc = sb.exec("bash", "-c", f"cd /work && {command}")
    code = proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    body = out + (("\n[stderr]\n" + err) if err else "")
    body = body.strip()
    if len(body) > 6000:
        body = body[:6000] + "\n... (truncated)"
    return f"$ {command}  [modal sandbox]\n[exit {code}]\n{body or '[no output]'}"


def shutdown() -> None:
    global _sandbox
    if _sandbox is not None:
        try:
            _sandbox.terminate()
        except Exception:  # noqa: BLE001
            pass
        _sandbox = None
