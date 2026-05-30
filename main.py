"""Cartographer CLI.

Usage:
    python main.py --repo /path/to/repo --question "How does auth work?"
    python main.py --repo . --question "..." --no-verify --backend local
"""
from __future__ import annotations

import argparse
import asyncio

from dotenv import load_dotenv

load_dotenv()

from cartographer.config import SETTINGS, set_repo  # noqa: E402
from cartographer.orchestrator import research        # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cartographer — autoresearch for codebases")
    p.add_argument("--repo", required=True, help="Path to the repo to investigate")
    p.add_argument("--question", required=True, help="Research question")
    p.add_argument("--backend", choices=["local", "modal"], default=SETTINGS.backend)
    p.add_argument("--max-parallel", type=int, default=SETTINGS.max_parallel_subagents)
    p.add_argument("--no-verify", action="store_true", help="Skip the verifier pass")
    return p.parse_args()


async def _main() -> None:
    args = parse_args()
    set_repo(args.repo)
    SETTINGS.backend = args.backend
    SETTINGS.max_parallel_subagents = args.max_parallel

    print(f"🗺️  Cartographer investigating: {SETTINGS.repo_path}")
    print(f"❓ {args.question}\n{'─'*60}")

    report = await research(args.question, verify=not args.no_verify)

    print("\n" + "═" * 60 + "\nFINAL REPORT\n" + "═" * 60)
    print(report)


if __name__ == "__main__":
    asyncio.run(_main())
