"""Central config: models, quotas, repo path.

Keep tunables here so the orchestrator/subagents stay clean.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    # The repo under investigation. Set per-run from the CLI.
    repo_path: Path = field(default_factory=lambda: Path(".").resolve())

    # Models (override via env). gpt-5 for planning/synthesis, a cheaper
    # model for high-volume grep/read sub-tasks to control spend.
    orchestrator_model: str = os.getenv("ORCHESTRATOR_MODEL", "gpt-5")
    subagent_model: str = os.getenv("SUBAGENT_MODEL", "gpt-5-mini")
    verifier_model: str = os.getenv("VERIFIER_MODEL", "gpt-5")

    # Concurrency / cost guardrails.
    max_parallel_subagents: int = 8       # quota cap on the SubAgentPool
    max_subagent_turns: int = 12          # stop a runaway sub-agent
    command_timeout_s: int = 60           # cap on any run_command

    # Execution backend: "local" (fast iteration) or "modal" (scale demo).
    backend: str = os.getenv("CARTO_BACKEND", "local")

    # Safety: commands containing these are refused outright.
    blocked_command_substrings: tuple[str, ...] = (
        "rm -rf", "sudo", "curl ", "wget ", ":(){", "mkfs", "dd if=",
        "shutdown", "reboot", "git push", "ssh ",
    )


SETTINGS = Settings()


def set_repo(path: str) -> Path:
    SETTINGS.repo_path = Path(path).expanduser().resolve()
    if not SETTINGS.repo_path.is_dir():
        raise SystemExit(f"Repo path is not a directory: {SETTINGS.repo_path}")
    return SETTINGS.repo_path
