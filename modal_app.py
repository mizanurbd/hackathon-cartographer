"""Modal execution backend — the scale story.

This shows the pattern from modal.com/blog/building-with-modal-and-the-openai-agent-sdk:
each investigation sub-agent's code execution runs in its own Modal Sandbox, so
the orchestrator can fan out to many in parallel. For the hackathon, the local
backend (cartographer/tools.run_command) is fine for fast iteration; switch to
this for the "watch it scale" demo moment.

Smoke test:
    modal run modal_app.py

Wiring into the agent (TODO during the build):
    - mount the target repo into the sandbox via a modal.Volume or image.add_local_dir
    - replace tools.run_command's local subprocess with sandbox.exec(...)
    - take a filesystem snapshot after deps install so fresh sub-agents start warm
"""
from __future__ import annotations

import modal

app = modal.App("cartographer")

# Base image for sub-agent sandboxes. Add language toolchains the target repo needs.
agent_image = (
    modal.Image.debian_slim()
    .apt_install("git", "ripgrep")
    .pip_install("pytest")
)


@app.function(image=agent_image, timeout=120)
def run_in_sandbox(command: str, repo_url: str | None = None) -> dict:
    """Run a command in an isolated sandbox. Returns {exit_code, stdout, stderr}.

    Fan out by calling `.map()` / `.spawn()` over many commands to investigate
    in parallel — that's the elastic-scale demo.
    """
    import subprocess

    workdir = "/work"
    subprocess.run(["mkdir", "-p", workdir], check=False)
    if repo_url:
        subprocess.run(["git", "clone", "--depth", "1", repo_url, workdir], check=False)

    res = subprocess.run(
        command, shell=True, cwd=workdir, capture_output=True, text=True, timeout=110
    )
    return {
        "exit_code": res.returncode,
        "stdout": res.stdout[-6000:],
        "stderr": res.stderr[-2000:],
    }


@app.local_entrypoint()
def main():
    # Smoke test: fan out three trivial commands in parallel sandboxes.
    cmds = ["echo hello from sandbox", "python -c 'print(2**10)'", "pytest --version"]
    for cmd, out in zip(cmds, run_in_sandbox.map(cmds)):
        print(f"$ {cmd}\n{out}\n{'-'*40}")
