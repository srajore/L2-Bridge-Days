# Day 2 — LangGraph Production Runtime

## What You'll Learn
- Make persistence durable: a SQLite checkpoint file that a "restarted" process can reopen.
- Run many threads side by side and resume only the one you mean to.
- Stream per-step updates with `stream_mode="updates"`.
- Retry a transient failure with a bounded `RetryPolicy`.
- Make side effects idempotent with a key stored in a database, so it survives restarts.
- Set operational boundaries: only resume work that is really paused, and keep the ledger and checkpoints in one known place.

## Already Covered in L2 (not repeated)
- L2 Day 7: checkpointer, `thread_id`, state across calls (with `InMemorySaver`).
- L2 Day 8: `interrupt`, `Command(resume=...)`, approve/reject paths.
- L2 Day 5: tool call from a fixed node; L2 Day 13: bounded loops and retries as concepts.

Today is only the production delta: durable, concurrent, retried, streamed and idempotent.

## Why This Matters
Real agents wait for humans, crash, and get retried by queues. In memory, a restart loses every pending approval. A node with a side effect (here SupportDesk's `freeze_card`) can run twice (a retry, a redelivered message, a second click). Durable checkpoints, bounded retries and idempotency keys make "pause, crash, resume, retry" safe.

## Your Journey
- **Yesterday (Day 1):** we wrote the production target and the checker found 26 gaps. Two of them were "state is lost on restart" and "duplicate `freeze_card`".
- **Today:** we close those two. State goes into a SQLite file, a human approves before the card is frozen, and the freeze can never happen twice.
- **Tomorrow (Day 3):** the case file grows. We make state typed and safe to share, with reducers and subgraphs.

## SupportDesk so far
- Before today: the Day 1 target architecture (SupportDesk with `lookup_balance` and `freeze_card`, state in a durable store, `thread_id` owned by the server).
- Added today: a checkpointed thread per request, a human-approval `interrupt` before `freeze_card`, a bounded retry and an idempotent side effect (`approve_freeze` and `run_tool` in `example.ipynb`).
- Becomes in Day 19: `agent.py::make_agent` (`SqliteSaver` on `DB_FILE`), `agent.py::ask` (`thread_id` = `user-cid`), `agent.py::run_tool` (retry loop; the idempotency idea carries to any write tool) and `agent.py::check_policy` / `TOOL_POLICY["freeze_card"]["needs_human"]` (the approval boundary; Day 19 denies `freeze_card` instead of pausing, Day 2 shows the approve-and-resume path).

## Key Concepts (production depth only)
**One idea first: any step can run twice.** A retry, a message delivered again, a second click. So every step with a side effect must be safe to repeat. Everything below serves that idea.

**Persistence/checkpointing.** `SqliteSaver` writes state after every step to a file. A new process opens the same file and sees `get_state(config).next` = the node that is still waiting. *Analogy: a bookmark in a locked drawer. A new clerk picks up where the last one stopped.*

**Threads.** Each `thread_id` is an independent conversation inside the same database. Resuming `cust-1-c001` must not touch `cust-2-c002` (line 7 of the output proves it). The id is `user` + `-` + `cid`, built on the server, exactly as Day 19's `ask` does. *Analogy: one labelled folder per customer.*

**Interrupts.** The interrupted node starts again from its top on resume, so nothing with a side effect may sit above `interrupt(...)` in that node. Here `approve_freeze` contains only the `interrupt`. Experiment 3 in the notebook shows the bug on purpose.

**Streaming.** `app.stream(input, config, stream_mode="updates")` yields one event per step (`choose_tool`, then `__interrupt__`). Use it to show progress to a user or to log step boundaries. *Analogy: a parcel tracking page.*

**Retries.** `add_node(..., retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.1, retry_on=ConnectionError))` re-runs only that node, only for the named transient error, at most 3 times, with a growing wait. After the limit the error is raised and the checkpoint still points at the failed node. Retries are only safe because the node is idempotent. *Analogy: redial three times, then stop.*

**Idempotency.** The key is built from the business request (`freeze-cust-1`: one freeze per customer), never from a random value or time. It is stored in a database table (`INSERT OR IGNORE`, atomic): if the row already exists, the side effect is skipped. In production the same key is also sent to the card system. *Analogy: a PAID stamp on the receipt.*

**Operational boundaries.** `resume_thread` refuses to resume a thread that has no pending work (a double click, a stale link, a wrong id). Also decide who owns the checkpoint database, who may call resume, and when old threads are deleted.

## L2 vs L3 (what changed)
| L2 | L3 |
| --- | --- |
| `InMemorySaver`, one thread | SQLite file, many threads, reopened after "restart" |
| Approve once in one process | Resume in a new process; reject double/unknown resumes |
| Node runs once | Node may run twice: retries and duplicates are expected |
| Print the final result | Stream step events |
| Key check in a Python dict | Key in a database table (survives restart) |

## Concept Corner: the same ideas in other places
*Concept only. Nothing here changes today's lab; it shows that the vocabulary you learn today is shared across the industry.*

**The idea.** A production agent must survive pauses, crashes and repeats. That needs saved state, a safe way to ask a human, bounded retries and "do it once" keys.

**In a managed cloud.** Hosted agent services handle part of this for you. They keep *session memory* between calls (often with an expiry time), they can *hand control back to your application* when an action needs a person's approval, and cloud APIs commonly accept a *client token* so that the same create-request sent twice makes only one resource. Cloud SDKs also retry throttled or timed-out calls with *exponential backoff* (wait longer each time, usually with a little randomness). These are the same four ideas you build today: checkpoint, interrupt, idempotency key, bounded retry.

**In Claude's world.** When Claude uses a tool, the model only *asks* for the call. **Your code** runs the tool and sends back the result. That gap is a natural place to pause for a human, exactly like our `interrupt`. The Claude Agent SDK adds permission checks (allow, deny or ask) before a tool runs. Responses can be streamed as they are produced, and the official client libraries retry temporary errors with backoff. The lesson is the same: keep the risky step behind a checkpoint you control, and make it safe to repeat.

**How we do it locally.** `SqliteSaver` is the session memory, `interrupt` is the approval gate, `RetryPolicy` is the backoff, and the `ledger` table is the idempotency token. Same ideas, no cloud account needed.

| Idea | Today's file | Managed / Claude name (concept only) |
| --- | --- | --- |
| State that survives a restart | `SqliteSaver` file | managed session memory |
| Ask a human before a risky tool | `interrupt` + `Command(resume=...)` | return of control; Agent SDK permission check |
| Redial a flaky call a few times | `RetryPolicy` | retry with exponential backoff |
| Do it only once | `ledger` table key | idempotency (client request) token |
| Show progress | `stream_mode="updates"` | streaming responses |

## Code Walkthrough — `Day-02-LangGraph-Production-Runtime/example.ipynb`
The notebook tells the story of a **bank counter with a very good clerk** (bookmark, folders, manager's signature, tracking page, redial rule, PAID stamp) before each piece of code. Its steps: setup, the case file (`State`), the four jobs (nodes), the graph with the retry rule, two customers pausing, the restart, the duplicate delivery, four predict-then-run experiments, and the assignment.

Question: "Freeze my card". Graph: `START -> choose_tool -> approve_freeze -> (approved?) run_tool -> END`, conditional edge to `END` when the human says no.

- `choose_tool` picks `freeze_card` (the `needs_human=True` tool of SupportDesk).
- `approve_freeze` holds only the `interrupt(...)`: the human decides.
- `run_tool` calls a fake card system (`CARD_SYSTEM`) whose first call raises `ConnectionError`. The `RetryPolicy` retries it, then the node writes `freeze-cust-1` to the `ledger` table (helper `stamp`) in the same SQLite file.
- `resume_thread` checks `get_state(config).next` first, then streams the resume.
- `open_app()` builds a new connection, saver and graph each time: this is the "restart".
- Two customers (`cust-1`, `cust-2`) are started with `cid` `c001` and `c002`, so threads are `cust-1-c001` and `cust-2-c002`; only the first is resumed first.
- The file `day02_checkpoints.sqlite` is created next to the notebook by `reset_world()` and deleted in the last cell. If the notebook stops half-way, run the setup cell again: it deletes the old file for you.

Real output (Steps 4 to 6):

```text
1. cust-1-c001 streamed updates: ['choose_tool', '__interrupt__']
1. cust-2-c002 streamed updates: ['choose_tool', '__interrupt__']
2. After restart, cust-1-c001 waits at: ('approve_freeze',)
3. Human approves cust-1-c001: steps ['approve_freeze', 'run_tool'] -> card for cust-1 frozen (freeze-cust-1)
4. Card system calls (1 timeout + 1 retry): 2
5. Second click on the same approval: REJECTED: no paused work for thread cust-1-c001
6. Unknown thread: REJECTED: no paused work for thread cust-9-c999
7. cust-2-c002 untouched, still waits at: ('approve_freeze',)
8. Human rejects cust-2-c002: steps ['approve_freeze'] -> freeze rejected by the human
9. Duplicate delivery: skipped: freeze-cust-1 already done (idempotent)
10. Ledger: [('freeze-cust-1', 'cust-1')]
```

## Lab Steps
Open the notebook in VS Code (Jupyter extension), choose the project's `.venv` as the kernel, then run the cells from top to bottom with Shift + Enter.
```cmd
uv sync
code Day-02-LangGraph-Production-Runtime\example.ipynb
```
1. Run Steps 0-6 and match each printed line (1 to 10) to the code.
2. Step 7, Experiment 1: the card system fails 5 times but `max_attempts` is 3. Predict: the run stops with `ConnectionError` after 3 calls and the ledger stays empty.
3. Experiment 2: use a key that changes between attempts. Predict: two ledger rows (the duplicate effect idempotency prevents).
4. Experiment 3: put a side effect above `interrupt()`. Predict: it runs twice (once before the pause, once after the resume).
5. Experiment 4: compare `stream_mode="updates"` with `"values"`.

## Assignment (workbook lab): Harden a workflow for interruption/retry and demonstrate safe resumption
Harden the SupportDesk `freeze_card` flow: add a second interrupt, a supervisor approval, after the first one (for example when the question mentions a business account). Run it and show with printed output: (1) pause at the first approval, (2) resume in a new connection, (3) pause at the second approval, (4) resume it, (5) one injected card-system timeout that is retried, (6) a duplicate delivery that does not freeze the card twice, (7) a resume of a thread that is not paused and is rejected. Submit the output.

## Production Checklist (reuse as release-checklist lines on Day 19)
- The checkpointer is a durable store (SQLite file or database) and a test resumes a paused thread from a new connection/process.
- Every request has an explicit `thread_id`, and resuming a thread with no pending work is rejected.
- Every side-effect node (`freeze_card`) uses a deterministic idempotency key stored in a database, and a duplicate-delivery test shows no second effect.
- Retries use `RetryPolicy` with `max_attempts` and a named transient error type; a test with more failures than attempts ends in a clear error.
- No side effect runs before `interrupt(...)` in the same node.
