# Architecture

Cartographer is a **long-horizon control loop**: a lean orchestrator that plans and re-plans, delegating heavy work to isolated sub-agents that read and execute code, finished by a verification pass. The design goal is to investigate large codebases without the orchestrator's context rotting.

## System diagram

```mermaid
flowchart TD
    U[Repo + Question] --> O

    subgraph Control Loop
      O["🧠 Orchestrator<br/>(OpenAI Agents SDK)<br/>plan → delegate → re-plan → synthesize<br/>SQLite session memory"]
    end

    O -->|investigate&#40;[tasks]&#41; · parallel · quota-capped| P{{SubAgent Pool}}

    P --> S1["Sub-agent<br/>read · grep · RUN"]
    P --> S2["Sub-agent<br/>read · grep · RUN"]
    P --> S3["Sub-agent<br/>read · grep · RUN"]

    S1 -->|summary + file:line| O
    S2 -->|summary + file:line| O
    S3 -->|summary + file:line| O

    S1 -.executes.-> SB[(Sandbox<br/>local or Modal)]
    S2 -.executes.-> SB
    S3 -.executes.-> SB

    O --> V["✅ Verifier<br/>re-runs key claims<br/>VERIFIED / UNVERIFIED"]
    V --> R[Cited, verified report]

    O -. traces .-> RD[(Raindrop Workshop)]
    S1 -. traces .-> RD
    V -. traces .-> RD
```

## Key design decisions

### 1. Orchestrator never touches files
The orchestrator only calls one tool — `investigate([tasks])`. It holds the plan and the accumulated findings, but never reads source or stdout directly. This keeps its context small and coherent across a long investigation. All token-heavy work happens in sub-agents whose contexts are discarded after each task.

### 2. Sub-agents read **and run** code
Each sub-agent gets `list_tree`, `read_file` (line-numbered for citations), `grep`, and `run_command`. The instruction is explicit: when a claim is checkable, *run something* to verify it (execute a test, reproduce behavior, check a version). This is what separates Cartographer from read-only RAG.

### 3. Parallelism with a quota
`investigate([...])` dispatches tasks concurrently via `asyncio.gather`, gated by a semaphore (`max_parallel_subagents`). The agent can fan out widely while spend stays bounded — and on the Modal backend each sub-agent's execution runs in its own sandbox, so fan-out is elastic.

### 4. Citations are first-class
`read_file` returns content prefixed with `# path:Lstart-Lend`, and every agent is told to propagate `file:line` citations into findings. Any claim that can't be cited is dropped or flagged.

### 5. Verification as a trust layer
After synthesis, a skeptical verifier re-checks the 3–5 most load-bearing claims by re-reading the cited lines and re-running commands, labeling each `VERIFIED` / `PARTIALLY VERIFIED` / `UNVERIFIED`. Per [howtoeval.com](https://www.howtoeval.com), an honest "unverified" beats a confident wrong answer.

### 6. Safety guards
`run_command` refuses a blocklist of destructive/networked commands, enforces a timeout, and all file tools reject paths outside the target repo. For untrusted code, switch `--backend modal` so execution is fully sandboxed off your machine.

## Data flow (one investigation)
1. CLI sets the repo and question → `orchestrator.research()`.
2. Orchestrator plans sub-questions → `investigate([...])`.
3. Sub-agents run in parallel, each reading/executing in the repo, returning summaries + citations.
4. Orchestrator inspects results, optionally issues more rounds (**re-plan**).
5. Orchestrator synthesizes the cited report.
6. Verifier re-runs key claims and appends a verification section.
7. Every step streams to Raindrop Workshop for inspection/replay.

## Scaling path (Modal)
The local backend runs commands via subprocess for fast iteration. The Modal backend (`modal_app.py`) runs each execution in an isolated sandbox; `run_in_sandbox.map(...)` fans out across many at once, and filesystem snapshots let fresh sub-agents start warm (deps installed) instead of repeating setup — the pattern from Modal's OpenAI Agents SDK guide.
