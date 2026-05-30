"""Orchestrator: the long-horizon control loop.

The orchestrator plans an investigation, dispatches focused tasks to parallel
sub-agents (via a quota-capped pool), receives only their summaries, and can
re-plan based on findings. It never reads files itself — that keeps its context
lean while the sub-agents do the heavy lifting.
"""
from __future__ import annotations

import asyncio

from agents import Agent, Runner, SQLiteSession, function_tool

from .config import SETTINGS
from .subagent import run_subagent
from .verifier import verify_claims

# A simple semaphore enforces the parallel-subagent quota (cost guardrail).
_quota = asyncio.Semaphore(SETTINGS.max_parallel_subagents)


@function_tool
async def investigate(tasks: list[str]) -> str:
    """Dispatch one or more focused investigation tasks to parallel sub-agents.

    Pass several independent sub-questions at once to investigate in parallel.
    Each returns a summary with `path:line` citations. Re-plan based on results.
    """
    async def _one(t: str) -> str:
        async with _quota:
            try:
                summary = await run_subagent(t)
            except Exception as e:  # noqa: BLE001
                return f"### TASK: {t}\n[sub-agent error] {e}"
        return f"### TASK: {t}\n{summary}"

    results = await asyncio.gather(*(_one(t) for t in tasks))
    return "\n\n".join(results)


ORCHESTRATOR_INSTRUCTIONS = """\
You are Cartographer's lead researcher investigating an unfamiliar codebase.
You coordinate; you do NOT read files yourself.

Loop:
1. PLAN. Decompose the user's question into focused, independent sub-questions.
2. DELEGATE. Call `investigate([...])` with several sub-questions to run them in
   parallel. Prefer one call with many tasks over many sequential calls.
3. RE-PLAN. Read the returned summaries. If there are gaps or contradictions,
   issue another `investigate([...])` round. Iterate until you can answer well.
4. SYNTHESIZE a final report:
   - A direct answer to the question.
   - Architecture / flow as relevant.
   - Risks or gotchas, each with severity.
   - EVERY factual claim must carry a `path:Lstart-Lend` citation propagated
     from the sub-agents. Drop any claim you cannot cite.
   - A short "Confidence & gaps" section. If something is unverified, say so.

Be rigorous. A cited, verified "we couldn't confirm X" beats a confident guess.
"""


def build_orchestrator() -> Agent:
    return Agent(
        name="cartographer",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        model=SETTINGS.orchestrator_model,
        tools=[investigate],
    )


async def research(question: str, *, verify: bool = True) -> str:
    """Top-level entry: investigate `question` over the configured repo."""
    agent = build_orchestrator()
    session = SQLiteSession("cartographer-run")  # memory across turns
    prompt = (
        f"Repo under investigation: {SETTINGS.repo_path}\n\n"
        f"Question: {question}\n\n"
        "Investigate and produce the final cited report."
    )
    result = await Runner.run(agent, prompt, session=session, max_turns=30)
    report = str(result.final_output)

    if verify:
        report = await verify_claims(report)
    return report
