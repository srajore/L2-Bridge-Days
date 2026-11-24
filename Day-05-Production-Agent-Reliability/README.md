# Day 5 — Production Agent Reliability

> **In one sentence:** today we teach SupportDesk to fail *safely*: no endless waiting, no endless retrying, no crashes in front of the customer.

## What You'll Learn
- Stop waiting after a while (**timeout**).
- Try again politely, a few times only (**retry with backoff and jitter**).
- End every failure in a safe place (**fallback** or **human handoff**).
- Protect the tool from crowds (**rate limit** and **backpressure**).
- Practise failures on purpose (**fire drills**) so recovery is proven, not hoped for.

## What Went Wrong in L2, and What We Do Today
| In L2 | Today (L3) |
| --- | --- |
| The agent called its tool and hoped it answered | Every call has a time limit |
| A retry loop existed, but it retried instantly and had one stop rule | Retries wait longer each time, with a little randomness, and have two stop rules |
| A failure ended the run, or the model improvised an answer | Code picks a safe ending: Plan B or a human |
| One request at a time | A turnstile and a "club capacity" protect the tool |
| Failures only happened by accident | Failures are rehearsed like fire drills |

**Production risk removed:** a slow tool hanging the agent, a retry storm making an outage worse, a loop that never ends, or a flood of requests knocking over a tool.

## Your Journey
- **Yesterday (Day 4):** we made SupportDesk *visible*: every request leaves a trail.
- **Today:** now that we can see a failure, we make the agent *survive* it.
- **Tomorrow (Day 6):** the pretend tool is replaced by a real MCP server, and today's safety rules apply to every call.

## SupportDesk so far
- **Before today:** a checkpointed SupportDesk graph with typed state and trace lines `cid=<id> <node> +<ms>ms <detail>` (Days 2-4); its tool call is assumed to work.
- **Added today:** a timeout, bounded retry (`MCP_ATTEMPTS`), a `fallback` flag with the degraded answer, an escape path, a rate limit and backpressure around `lookup_balance` (see `05-fire-drill.ipynb`).
- **Becomes in Day 19:** `agent.py::run_tool` (the same `MCP_ATTEMPTS = 2` loop, `asyncio.wait_for(..., MCP_TIMEOUT_S)`, state field `fallback`, and `write_answer` saying "Service busy, please try again later.").

## The Notebooks (one small notebook per concept)
Each notebook has the same shape: the idea in plain words, what went wrong in L2, a tiny working LangGraph demo, a predict-then-run exercise, and a "Remember" box. No notebook depends on another, but doing them in order tells the story.

| # | Notebook | The idea | Time |
| --- | --- | --- | --- |
| 1 | `01-timeout.ipynb` | Never wait forever | 10 min |
| 2 | `02-retry-backoff-jitter.ipynb` | Try again, politely, a few times; two stop rules | 15 min |
| 3 | `03-fallback-and-escape-path.ipynb` | Plan B for temporary trouble, a human for permanent trouble | 15 min |
| 4 | `04-rate-limit-and-backpressure.ipynb` | A turnstile (wait) versus a full club (turn away) | 15 min |
| 5 | `05-fire-drill.ipynb` | Everything together; rehearse failures; assignment; Concept Corner | 20 min |

**Setup:** every notebook starts with a "connect to the AI model" cell (Ollama, model `gpt-oss:120b-cloud`). If it says the model is not reachable, run `ollama signin` in a terminal and restart the notebook.

## Key Concepts (plain words)
**One idea first: fail in a planned, bounded, visible way.** *Like phoning the card company with a set of rules for a bad line.*

- **Timeout:** the longest we wait for one call. *Hang up after a while.*
- **Retry with backoff and jitter:** redial a few times, wait longer after each failure, add a little random wait so everyone does not redial at the same second. *Redial later, not at the same moment as the crowd.*
- **Two stop rules:** our own limit (`MCP_ATTEMPTS`) and LangGraph's `recursion_limit` as a seat belt if our code has a bug.
- **Fallback (Plan B):** a safe, honest, visible answer for *temporary* trouble: the `fallback` flag is set and the customer sees "Service busy, please try again later."
- **Escape path (human handoff):** for *permanent* trouble (a wrong customer id) we skip the retries and hand off. Code decides, never the model. *Transfer to a colleague.*
- **Failure injection:** a table that says what each pretend call does, so failures are repeatable. *A fire drill.*
- **Rate limit versus backpressure:** the rate limit makes callers *wait*; backpressure *turns extra work away* ("503 busy"). *A turnstile versus a full club.*

## Concept Corner: the same ideas in other places
*Concept only. Nothing here changes today's lab; it shows that the vocabulary is shared across the industry.*

**The idea.** Every outside call can be slow, can fail, or can be told "too many requests". A production agent decides in advance what to do in each case.

**In a managed cloud.** Services publish *quotas and throttling limits* and answer "too many requests" when you exceed them. Their client libraries retry with *exponential backoff and jitter* and let you set *timeouts*. Larger systems add *circuit breakers* (stop calling a broken service for a while) and a *dead-letter queue* (park work that keeps failing for a person to look at), the managed cousin of our escape path.

**In Claude's world.** The Claude API answers with a *rate-limit error* when you send too much and an *overloaded error* when it is busy; both are **temporary**, so retry with a wait. The official client libraries already retry some of these automatically and let you set a timeout. The Agent SDK lets you cap how many turns an agent may take, the same idea as our bounded loop. A malformed request will fail every time, so do not retry it.

**How we do it locally.** Same ideas, no cloud account needed:

| Idea | Today's name | Managed / Claude name (concept only) |
| --- | --- | --- |
| Hang up after a while | `MCP_TIMEOUT_S` | client timeout |
| Redial with growing waits | backoff | exponential backoff with jitter |
| Callers wait their turn | rate limiter | quotas and throttling |
| Turn extra work away | bounded club | load shedding, overloaded or 503 |
| Park what keeps failing | escalate | dead-letter queue, human review |
| Stop calling a broken service | fallback | circuit breaker |
| Cap the loop | `MCP_ATTEMPTS`, `recursion_limit` | maximum turns for an agent |

## Lab Steps
Open each notebook in VS Code (Jupyter extension), choose the project's `.venv` as the kernel, and run the cells from top to bottom with Shift + Enter.
```cmd
uv sync
code Day-05-Production-Agent-Reliability
```
1. Run notebooks 1 to 4. In each, answer the **Your turn** question *before* running the cell.
2. In notebook 5, run the five fire drills and say each ending out loud first.
3. Add your own drill (the assignment below).

## Assignment (inject failures, implement bounded recovery, no infinite loop)
In `05-fire-drill.ipynb`, add two new failure scenarios to `FAULTS`. Run them and write one sentence for each saying which safety net saved the run (timeout, retry, fallback, escape path, rate limit, backpressure). Prove none can loop: each trace must end in a normal answer, `FALLBACK` or `escape path`.

## Production Checklist (reused as release-checklist lines on Day 19)
- Every external call has a timeout, and a test injects a slow call and sees `TimeoutError` in the trace.
- Retries are bounded, use backoff with jitter, and only retry temporary errors.
- Every graph cycle has an attempt cap in its route AND a `recursion_limit` in the run config.
- Every failure ends in a fallback marked "degraded" or an escape path to a human; none ends in a hang.
- Load is bounded: a rate limit on each dependency and a limit that rejects excess work.
- A failure-injection test (temporary, permanent, slow, down) passes before release.
