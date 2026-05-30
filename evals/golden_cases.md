# Golden Cases

A *small* set of high-signal checks on a FIXED target repo. Per howtoeval.com:
20 high-signal cases beat 200 low-signal ones. Pick one repo you control as the
fixture so answers are stable, then fill in known-correct expectations.

Fixture repo: `TODO set a path, e.g. ./fixtures/sample-app`

| # | Question | Expected (must appear) | Must cite | Pass? |
|---|----------|------------------------|-----------|-------|
| 1 | Where is the HTTP server started? | the entrypoint file + port | `file:line` of `listen`/`run` | ☐ |
| 2 | How does authentication work? | the auth middleware/flow | auth module `file:line` | ☐ |
| 3 | Does the test suite pass? | actual pass/fail from running it | quoted test output | ☐ |
| 4 | What DB does it use and where configured? | engine + config location | config `file:line` | ☐ |
| 5 | Name one security risk. | a real, specific risk | `file:line` of the risky code | ☐ |
| 6 (negative) | Is there a payment integration? | "INSUFFICIENT EVIDENCE" if none | — | ☐ |

**Rule:** case #6 (the negative) is the most important — it proves the agent
says "I don't know" instead of hallucinating. Protect that behavior.
