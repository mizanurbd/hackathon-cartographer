# Cartographer 🗺️

**Autoresearch for codebases.** Point it at an unfamiliar or legacy repo and ask a hard question. Cartographer plans an investigation, fans out parallel sub-agents that **read *and run*** the code in sandboxes, and returns a **verified report with every claim cited to `file:line`**.

Built for the Autoresearch Systems Hackathon — on the **OpenAI Agents SDK**, executed on **Modal**, evaluated with **Raindrop Workshop**.

---

## Why it's different
- **Reads *and* runs code.** Sub-agents execute commands/tests in a sandbox to *verify* findings — not just RAG over source.
- **Long-horizon control loop.** A lean orchestrator plans → delegates → verifies → re-plans; sub-agents do the heavy work in isolated contexts and return only summaries (no context rot).
- **Grounded output.** Every claim cites `path/to/file:Lstart-Lend`. Unsupported claims get an explicit "needs human" flag.

## Architecture
```
Repo + Question
      │
      ▼
ORCHESTRATOR (OpenAI Agents SDK)  ──plans, re-plans, holds memory
      │ invoke_subagent  (async, parallel, quota-capped)
   ┌──┴───┬──────┬──────┐
   ▼      ▼      ▼      ▼
 SubAgent SubAgent ...        (isolated context; read + grep + RUN code)
   │      │
   └─ summary + file:line citations ─┘
      │
      ▼
VERIFIER  ──re-runs key claims in sandbox
      │
      ▼
Cited report   (traced end-to-end in Raindrop)
```

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add OPENAI_API_KEY

# Run against any local repo:
python main.py --repo /path/to/target/repo \
  --question "How does authentication work end-to-end and where are the security risks?"
```

### Optional: scale on Modal (parallel sandboxed sub-agents)
```bash
modal token new               # after redeeming Modal credits
modal run modal_app.py        # smoke-test the sandbox fan-out
python main.py --repo <path> --question "..." --backend modal
```

### Optional: Raindrop tracing
```bash
curl -fsSL https://raindrop.sh/install | bash
raindrop workshop             # opens local trace UI; traces stream as the agent runs
```

## Layout
| File | What it is |
|---|---|
| `main.py` | CLI entry point |
| `cartographer/orchestrator.py` | Planner/orchestrator + parallel SubAgentPool |
| `cartographer/subagent.py` | Investigation sub-agent (fresh context) |
| `cartographer/tools.py` | `read_file`, `grep`, `run_command` — all citation-aware |
| `cartographer/verifier.py` | Re-runs key claims to confirm them |
| `cartographer/config.py` | Models, quotas, paths |
| `modal_app.py` | Modal sandbox execution backend (scale story) |
| `evals/` | Golden cases + runner (Raindrop-friendly) |

## Demo tips (read BATTLE_PLAN.md)
- **Cache** the impressive run; never demo live-only.
- Film the **≤60s** video early.
- Keep one Raindrop trace open during judging.
