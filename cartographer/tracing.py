"""Raindrop Workshop tracing — optional, defensive, matches the real SDK.

Uses the Raindrop Python SDK (`import raindrop.analytics as raindrop`):
  - raindrop.init(write_key, tracing_enabled=True)  → auto-instruments OpenAI
  - raindrop.begin(...) / interaction.finish(...)    → wraps a run as a trace

If `raindrop-ai` isn't installed or no key/debugger env is set, every call here
degrades to a safe no-op so a run never breaks.

Enable:
    pip install raindrop-ai
    export RAINDROP_LOCAL_DEBUGGER=1
    export RAINDROP_WRITE_KEY=local
    raindrop workshop      # separate terminal — live trace UI
Docs: https://raindrop.ai/docs/sdk/python
"""
from __future__ import annotations

import os

_ENABLED = False
_rd = None

try:
    if os.getenv("RAINDROP_WRITE_KEY") or os.getenv("RAINDROP_LOCAL_DEBUGGER"):
        import raindrop.analytics as _rd  # type: ignore

        _rd.init(os.getenv("RAINDROP_WRITE_KEY") or "local", tracing_enabled=True)
        _ENABLED = True
except Exception:  # noqa: BLE001 — never let tracing break a run
    _ENABLED = False
    _rd = None


def begin_run(question: str):
    """Start a traced interaction for one research run. Returns a handle or None."""
    if not (_ENABLED and _rd is not None):
        return None
    try:
        return _rd.begin(
            user_id=os.getenv("CARTO_USER", "cartographer"),
            event="codebase_research",
            input=question,
        )
    except Exception:  # noqa: BLE001
        return None


def end_run(handle, output: str) -> None:
    """Finish the traced interaction and flush so spans reach Workshop."""
    if handle is not None:
        try:
            handle.finish(output=output[:4000])
        except Exception:  # noqa: BLE001
            pass
    if _ENABLED and _rd is not None:
        try:
            _rd.flush()
        except Exception:  # noqa: BLE001
            pass


def status() -> str:
    return "Raindrop tracing: ON" if _ENABLED else "Raindrop tracing: off"
