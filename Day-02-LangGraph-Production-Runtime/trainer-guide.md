# Day 2 Trainer Guide — LangGraph Production Runtime

## Outcome
A learner can checkpoint the SupportDesk graph to SQLite, run several threads, stream updates, retry a transient failure with a bound, pause with `interrupt`, resume in a "restarted" process, and explain why a database-backed idempotency key stops a retry or duplicate from repeating a side effect.

## Files
- `slides.pptx` — 26 slides, interactive (section tabs, Agenda button, predict/reveal slides). Run it in Slide Show mode so the links work.
- `example.ipynb` — offline SupportDesk `freeze_card` notebook (question "Freeze my card"), told as a bank-counter story: SqliteSaver, two threads, streaming, RetryPolicy, interrupt/resume, SQLite ledger for idempotency, resume boundary, four predict-then-run experiments
- `README.md`, `trainer-guide.md`
- Quiz: `quizzes/Day-02-quiz.csv`

## Setup (cmd)
```cmd
uv sync
code Day-02-LangGraph-Production-Runtime\example.ipynb
```
In VS Code choose the project's `.venv` as the notebook kernel (Jupyter extension), then run cells with Shift + Enter. No `ollama signin`. The notebook creates and deletes `day02_checkpoints.sqlite` next to itself; the setup cell deletes a leftover file, so a half-run notebook is easy to recover. Learners already know checkpointer/thread_id (L2 Day 7) and interrupt/resume (L2 Day 8): do not re-teach them. Thread: this is SupportDesk's `freeze_card` (the `needs_human=True` tool from Day 1's risk list); it becomes `SqliteSaver`, `thread_id` = `user-cid` and the approval gate in Day 19.

## 120-Minute Flow
1. 0-10 — Journey slide, then one question: "What happens to an `InMemorySaver` approval when the server restarts?" (predict slide)
2. 10-30 — Teach durable checkpoints, threads, the "node re-runs from the top on resume" rule, streaming.
3. 30-50 — Teach retries (bounded, named error) and idempotency keys with a double-charge story. Why retries need idempotency.
4. 50-60 — Concept Corner: how managed agent services and Claude handle the same four ideas (concept only).
5. 60-70 — Run notebook Steps 4-6; map each of the ten printed lines to code; point out thread ids `cust-1-c001` are built like Day 19's `ask`.
6. 70-75 — Break.
7. 75-95 — Lab: Step 7 experiments 1-4 (exhaust the retry limit; break the key; side effect above the interrupt; stream modes). Always predict first.
8. 95-115 — Assignment: second (supervisor) interrupt on the freeze flow, with the seven proofs.
9. 115-120 — Exit check.

## Walkthrough Questions
1. Which line saves state, and where does it go?
2. How does the second process know which conversation to continue?
3. What would happen if `run_tool` used a random UUID as its key?
4. Why does the notebook build a new connection and graph before resuming?
5. Why does `fail_first` fail before the ledger write and not after? (A crash after the write but before the result is saved is exactly what the key protects against.)
6. What does `resume_thread` protect against?
7. Concept Corner: which part of a hosted agent service plays the role of our `SqliteSaver`? Of our `ledger` table?
8. Concept Corner: with Claude tool use, who actually runs the tool? Where could a human approval sit?

## Common Mistakes
- Using a different `thread_id` on resume (the graph finds nothing).
- Putting a side effect before `interrupt` in the same node; it runs again on resume (Experiment 3 shows it).
- Generating the idempotency key from time or a random value (Experiment 2 shows two ledger rows).
- Calling `invoke(start, config)` again instead of `Command(resume=...)`.
- Forgetting to close SQLite connections before deleting the file (Windows locks it). If a run stops half-way, run the setup cell again: `reset_world()` removes the old file.
- Retrying a non-idempotent node, or retrying on every exception instead of a named transient one.

## Exit Check
Ask: "A queue delivers the 'freeze cust-1' message twice, and the first attempt timed out once. Which three things keep the card from being frozen (or the customer charged) twice?" (Deterministic key, an atomic check against a stored ledger, a bounded retry on the same node.)

## What Was and Was Not Live-Verified
- Verified: `example.ipynb` was executed top to bottom with `nbclient` on Windows (langgraph with `langgraph-checkpoint-sqlite`), with no errors. Steps 4-6 printed exactly the ten lines in the README. Experiment 1 (`fail_first` = 5) stopped with `ConnectionError` after 3 card-system calls and left the ledger empty. Experiment 2 (changing key) produced two ledger rows (`freeze-cust-1-1`, `freeze-cust-1-2`). Experiment 3 (side effect above `interrupt`) ran once before the pause and twice after the resume. Experiment 4 printed the `updates` and `values` streams. The demo file was removed afterwards.
- Not verified: opening the notebook in the VS Code UI and running it cell by cell by hand; the slide deck in a live Slide Show click-through; the assignment (second interrupt); and what the checkpoint looks like after the retry limit is exhausted (that thread is not resumed).
- The "card system" is a Python stub that fails on its first call; no real card system or network is used. Day 19 does not pause for approval: it denies `freeze_card`; this day shows the pause/resume path that a later approval flow would use. The ledger is a real SQLite table, so the idempotency key does survive the simulated restart, but "restart" here is a new connection and graph object in the same Python process, not a killed process.
- Concurrent writers to one SQLite file are not tested; a real service would use Postgres or another database checkpointer.
- Concept Corner names are generic on purpose (managed session memory, return of control, idempotency token, backoff). Product names change; check vendor docs before naming a specific service in class.
