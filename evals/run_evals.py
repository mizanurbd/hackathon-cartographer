"""Minimal code-aware eval runner.

Runs Cartographer on each golden case and applies cheap string assertions on
the report. Keep it dead simple (per howtoeval.com — a local script beats a
hosted dashboard). With Raindrop Workshop running, every case is also a trace
you can inspect/replay.

Usage:
    python -m evals.run_evals --repo ./fixtures/sample-app
"""
from __future__ import annotations

import argparse
import asyncio

from dotenv import load_dotenv

load_dotenv()

from cartographer.config import set_repo, SETTINGS  # noqa: E402
from cartographer.orchestrator import research        # noqa: E402

# (question, list-of-substrings-that-must-appear, must_not-appear)
CASES: list[tuple[str, list[str], list[str]]] = [
    ("Where is the HTTP server started?", [":L"], []),
    ("How does authentication work end to end?", [":L"], []),
    ("Does the test suite pass? Run it.", ["exit"], []),
    # Negative case: with no payment code, the agent must NOT invent one.
    ("Is there a Stripe payment integration? Only say yes if you can cite it.",
     [], ["definitely", "obviously"]),
]


async def _run(repo: str) -> None:
    set_repo(repo)
    SETTINGS.max_parallel_subagents = 4
    passed = 0
    for i, (q, must, must_not) in enumerate(CASES, 1):
        report = (await research(q, verify=False)).lower()
        ok = all(m.lower() in report for m in must) and all(
            n.lower() not in report for n in must_not
        )
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] case {i}: {q}")
    print(f"\n{passed}/{len(CASES)} golden cases passed")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    args = ap.parse_args()
    asyncio.run(_run(args.repo))


if __name__ == "__main__":
    main()
