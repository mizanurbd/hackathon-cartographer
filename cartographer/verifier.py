"""Verifier: the trust layer.

Takes the orchestrator's draft report and re-checks its key claims by running
code in the repo. Flags any claim it cannot independently confirm. This is the
"floor-raising" step (see howtoeval.com): a confident wrong answer is worse
than an honest "unverified".
"""
from __future__ import annotations

from agents import Agent, Runner

from .config import SETTINGS
from .tools import SUBAGENT_TOOLS

VERIFIER_INSTRUCTIONS = """\
You are a skeptical verifier. You receive a draft research report about a
codebase. For the 3-5 most load-bearing factual claims:

1. Re-check each by re-reading the cited `path:line` and, where possible,
   running a command to confirm it (`run_command`).
2. Mark each claim: [VERIFIED], [PARTIALLY VERIFIED], or [UNVERIFIED] with a
   one-line reason and the evidence you used.
3. Return the ORIGINAL report unchanged, followed by a
   "## Verification" section with your per-claim verdicts and an overall
   trust note. Do not soften or invent; if you could not verify, say so.
"""


def build_verifier() -> Agent:
    return Agent(
        name="verifier",
        instructions=VERIFIER_INSTRUCTIONS,
        model=SETTINGS.verifier_model,
        tools=SUBAGENT_TOOLS,
    )


async def verify_claims(report: str) -> str:
    agent = build_verifier()
    result = await Runner.run(
        agent,
        f"Draft report to verify:\n\n{report}",
        max_turns=SETTINGS.max_subagent_turns,
    )
    return str(result.final_output)
