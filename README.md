# 🗺️ Cartographer — Autoresearch for Codebases

> Point it at an unfamiliar or legacy codebase, ask a hard question, and get back a **verified report where every claim is cited to `file:line`** — produced by a swarm of agents that don't just *read* the code, they *run* it.

Built at the **Autoresearch Systems Hackathon** (Modal · OpenAI · Raindrop · Antler) on the **OpenAI Agents SDK**, executed on **Modal**, evaluated with **Raindrop Workshop**.

---

## The problem

Every software team — especially a services company — burns days or weeks getting an engineer productive on an unfamiliar or legacy codebase: tracing how things work, finding the landmines, judging what's safe to change. That work is *research*: plan, search, read, run, verify, synthesize.

## What Cartographer does

Given a repo and a question, Cartographer:

1. **Plans** an investigation and decomposes it into focused sub-questions.
2. **Fans out** parallel sub-agents — each in an isolated context — that read, `grep`, and **execute** the code in a sandbox to *verify* what they find.
3. **Re-plans** based on what comes back, until it can answer with evidence.
4. **Synthesizes** a report where every factual claim carries a `path:Lstart-Lend` citation, plus a verifier pass that re-runs the load-bearing claims and labels them `VERIFIED` / `UNVERIFIED`.

If it can't prove something, it says so instead of guessing.

## Why it's different

| Most code Q&A tools | Cartographer |
|---|---|
| RAG over source (read-only) | **Reads *and runs*** code to verify |
| One big context that rots | Lean orchestrator + isolated sub-agents returning summaries only |
| Confident, uncited answers | Every claim cited to `file:line`; unverifiable claims flagged |
| One-shot | Iterative plan → delegate → verify → **re-plan** |

---

## Quickstart

```bash
cd cartographer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add OPENAI_API_KEY

# Investigate the bundled demo app (TaskVault — has planted bugs):
python main.py --repo fixtures/sample-app \
  --question "How does authentication work end-to-end, and what are the top security risks? Verify each by running the tests."
```

### Scale on Modal (parallel sandboxed sub-agents)
```bash
modal token new
modal run modal_app.py        # smoke-test the fan-out
python main.py --repo <path> --question "..." --backend modal
```

### Trace & eval with Raindrop Workshop
```bash
curl -fsSL https://raindrop.sh/install | bash
raindrop workshop             # live traces as the agent runs
python -m evals.run_evals --repo fixtures/sample-app
```

---

## Repository layout

```
cartographer/
├── main.py                 # CLI entry point
├── modal_app.py            # Modal sandbox execution backend (scale)
├── cartographer/
│   ├── orchestrator.py     # planner + parallel SubAgentPool + re-plan loop
│   ├── subagent.py         # investigation agent (fresh context)
│   ├── tools.py            # read_file / grep / run_command — citation-aware
│   ├── verifier.py         # re-runs key claims to confirm them
│   └── config.py           # models, quotas, safety guards
├── evals/                  # golden cases + runner (Raindrop-friendly)
└── fixtures/sample-app/    # TaskVault — demo repo with planted bugs
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full design.

## Tech stack
**OpenAI Agents SDK** (orchestrator + sub-agents + sessions) · **Modal** (sandboxed parallel execution) · **Raindrop Workshop** (tracing + code-aware evals).


## License
MIT
