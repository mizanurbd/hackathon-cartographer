"""Investigation sub-agent.

Each sub-agent runs in a FRESH context, does heavy reading/execution via the
citation-aware tools, and returns ONLY a compact summary + citations. This is
what keeps the orchestrator lean over a long-horizon investigation.
"""
from __future__ import annotations

from agents import Agent, Runner

from .config import SETTINGS
from .tools import SUBAGENT_TOOLS

SUBAGENT_INSTRUCTIONS = """\
You are a code investigation sub-agent. You are given ONE focused task about a
specific codebase. Your job:

1. Orient with `list_tree` / `grep`, then `read_file` the relevant parts.
2. When a claim is checkable, VERIFY it by running code with `run_command`
   (run a test, reproduce behavior, check a version). Reading is not enough.
3. Return a TIGHT summary (≤ ~250 words). For every factual claim, cite the
   exact source as `path:Lstart-Lend`. If you ran something, quote the key
   output line.
4. If the evidence is insufficient, say so explicitly: "INSUFFICIENT EVIDENCE:
   <what's missing>". Do not guess.

Never dump whole files back. Summaries + citations only.
"""


def build_subagent() -> Agent:
    return Agent(
        name="investigator",
        instructions=SUBAGENT_INSTRUCTIONS,
        model=SETTINGS.subagent_model,
        tools=SUBAGENT_TOOLS,
    )


async def run_subagent(task: str) -> str:
    """Run one investigation task to completion; return its summary string."""
    agent = build_subagent()
    result = await Runner.run(
        agent, task, max_turns=SETTINGS.max_subagent_turns
    )
    return str(result.final_output)
