# Day 4 — Observability and Tracing

## What You'll Learn
- Say why an agent needs more than logs: a trace of what it did and why.
- Name the four pillars: **traces, logs, metrics, evals**, and say which one to build first.
- Record a trace of **spans** (node, tool, model) with time, tokens, cost and errors.
- Tag every record with one **tracking number** (`cid`), and keep personal data out.
- Open a trace, find the first failing span, and write a short incident note.
- Name the common tracing tools (LangSmith, Langfuse, Phoenix and others) and when each fits.

## Already Covered in L2 (not repeated)
- L2 Day 14: tokens and cost (where tokens come from, why loops multiply them).
- L2 Day 13: the harness loop, and why you need to see each step.
- L2 Day 20: guardrails and a golden set (the quality side; today is "what actually happened").

## The Hook: 3:14 AM
*Team Orion* (a fictional team) launched a support agent on Friday. It triaged tickets, called an `issue_refund` tool and replied to customers with no human in the loop. The demo was great.

At 3:14 AM Saturday, finance calls: **$40,000 of refunds** went out overnight to tickets that were never eligible. The logs say `issue_refund` ran 212 times. Nobody can answer the CFO's real question: **why did it decide that?**

What the team had: logs that say the API call succeeded, one stray `print` from two weeks ago, and a provider dashboard with token counts. What they did not have: the prompt, the context, the tool choice, the reasoning. They could not even reproduce the failure.

*Traditional monitoring asks "did the code run?" Agents need "did the agent reason correctly, and can I prove it?" Today fills that gap.*

## Why This Matters
- **Agents fail quietly.** Every call can return 200 and the answer can still be wrong (wrong tool, misread policy, bad context). A stack trace cannot show a decision; a trace can.
- **Same prompt, different answer.** You cannot reproduce a 2 AM failure from memory. You need the stored record of that exact run.
- **Cost.** Tokens are billed. Without traces you learn which step burned the budget when the invoice arrives.
- **Trust and audit.** Someone will ask "why did it do that?": a CFO, a customer, a regulator. "We don't know" is not an answer.
- **Improvement.** You cannot test or improve what you never captured. Traces are the raw material for evals (Day 14) and CI gates (Day 15).
- **It is a gate for production.** An agent with no observability is a demo. Failure handling (Day 5), the audit trail (Day 8), evaluation (Day 14) and release gates all depend on today.

## Your Journey
- **Yesterday (Day 3):** SupportDesk got a typed `State`, owners, reducers and two subgraphs. The `trace` box exists.
- **Today:** we fill the `trace` box: a tracking number per request, timed spans, tokens, cost, and a check that no personal data leaks.
- **Tomorrow (Day 5):** now that you can see a failure, we harden against it (timeouts, retries, fallback).

## SupportDesk so far
- Before today: a durable thread (Day 2) and a typed `State` with retrieval and tool subgraphs and a `trace` reducer (Day 3).
- Added today: `cid` and `t0` in the state, the `tr()` line helper, and JSON-line spans for every node, tool and model call (`example.ipynb`: `tr`, `traced`, `call_tool`, `call_model`).
- Becomes in Day 19: `agent.py::tr` (identical), `cid` and `t0` set in `agent.py::ask`, one JSON log line per request printed by `app.py`, and `cid` in the audit record.

## The Four Pillars
| Pillar | What it is | Analogy | Answers |
| --- | --- | --- | --- |
| **Traces** | The full tree of one run: input, every model call, every tool call, in order | The flight recorder | "What exactly happened in this run?" |
| **Logs** | Single timestamped events ("retry 2", "tool error") | A diary entry | "Did something happen?" |
| **Metrics** | Numbers over time: latency, tokens per day, cost per request, error rate | A dashboard gauge | "Is it getting worse?" |
| **Evals** | A score for whether the answer was *good*, not just whether it ran | The accident investigator's verdict | "Was it right?" |

**If you can build only one first, build traces.** Evals need traces: you cannot score a run you never captured. Today's lab builds traces (with a little of each other pillar). Evals come on Day 14.

## Key Concepts (the essentials)
**One idea first: the symptom is last, the cause is earlier.** A bad answer shows up in the final step, but the first error span is usually upstream. *Analogy: the flight recorder and the parcel tracking number.*

- **Span.** One JSON line per step: `cid`, `kind` (`node`, `tool` or `model`), `name`, `latency_ms`, `error`. A run is the set of spans of one `cid`.
- **`tr()` line.** A short human-readable line in the state: `cid=<id> <node> +<ms>ms <detail>`. The `+<ms>ms` is time since `t0`, the start of the request.
- **Tool span inside a node span.** Tells you whether time went to the tool or to the node's own code.
- **Tokens and cost.** Model spans store `tokens_in`, `tokens_out`, `cost_usd`. With Ollama they come from `prompt_eval_count` and `eval_count`. The price table is a placeholder; use your provider's prices.
- **Tracking number (`cid`).** One per request, made at the front door, carried in state. Never one per node (Experiment 3).
- **Errors are data.** The wrapper records the error and returns a degraded result so the graph continues. The trace is how you learn it happened.
- **Privacy.** Spans store sizes, counts and names, never the question or answer. A test proves it.
- **Incident note.** Four lines: symptom, root cause, evidence, impact.

## L2 vs L3 (what changed)
| L2 | L3 |
| --- | --- |
| Token counts for one call by hand | Tokens and cost on every model span, totalled per request |
| `print` statements | Structured JSON spans |
| Wrong answer, no clue why | The trace shows the first failing span |
| One mixed log | One `cid` per request |

## Concept Corner: tools you can use, and the same ideas elsewhere
*Concept only. The lab stays on Ollama + LangGraph + plain JSON lines. Nothing here needs an account.*

**The idea.** Every request leaves a trail with an id, timings, token counts and errors, without personal data. Tools just store, show and search that trail for you.

**Hosted tracing tools (what your JSON lines turn into).**
| Tool | In one line | Best fit |
| --- | --- | --- |
| LangSmith | Made for LangChain/LangGraph; set environment variables and every call is traced | Teams already on LangGraph |
| Langfuse | Open source, can be self-hosted | Data must stay in your own network |
| Arize Phoenix | Open source, OpenTelemetry-based, strong on retrieval and evals | RAG-heavy pipelines |
| AgentOps | Built for multi-agent frameworks | CrewAI, AutoGen style systems |
| OpenTelemetry (+ OpenLLMetry) | Vendor-neutral standard; exports to Datadog, Grafana and others | Companies with an existing monitoring stack |
| Helicone, Portkey | Proxy or gateway that logs every call (Portkey adds retries and caching) | Quick cost and latency view |
| Datadog LLM Observability | Plugs into existing Datadog monitoring | Companies already on Datadog |

**The rule that matters more than the tool:** every agent that reaches production emits traces *somewhere*. Which vendor is the smaller decision.

**What LangSmith looks like (optional, 5 minutes).** With the environment variables `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY=...` and `LANGCHAIN_PROJECT=...`, LangGraph and any chat model are traced with no code change. Add `@traceable` to a plain Python function (like an eligibility check) and it shows up as its own span, as our `call_tool` does. `tags` and `metadata` in the run config let you filter traces later. The notebook's last step does this in a few lines and skips itself when no key is set. Keep the key in `.env`, and keep `.env` in `.gitignore`.

**In a managed cloud.** Ready-made metrics, logs with request ids, distributed traces and optional model-call logging, with alarms on top.

**In Claude's world.** Every API response has a **usage** block (input and output tokens: our `tokens_in`, `tokens_out`) and a **request id** you can quote for support (our `cid`, across a boundary). Agent SDK hooks run around tool calls, the natural place to write a tool span.

| Idea | Today's file | Tool or Claude name (concept) |
| --- | --- | --- |
| One id per request | `cid` | trace id, request id |
| One record per step | span (JSON line) | trace span / run |
| Token counts | `tokens_in`, `tokens_out` | the `usage` block |
| Time per step | `latency_ms` | latency metrics |
| Wrap a function | `traced`, `call_tool` | `@traceable`, hooks |
| Filter runs | `cid` | tags, metadata |

## Code Walkthrough — `Day-04-Observability-Tracing/example.ipynb`
The notebook tells the **flight recorder and parcel tracking number** story. Steps: setup, state and `tr()`, the recorder helpers, the workers and tool, the traced graph, three requests, reading the black box, investigating the failing request, four predict-then-run experiments, tidy up, the assignment, and an optional LangSmith peek.

- `tr()` is Day 19's trace-line function, copied exactly. `emit(...)` is the only place that writes `day04_trace.jsonl`.
- `traced(name, node)` wraps each node: times it, catches errors, records `state_keys_changed`. Nodes contain no span code.
- `call_tool` and `call_model` write the tool and model spans. With `USE_OLLAMA = False` (default) the model call is an offline stub with Ollama-shaped counts; set `USE_OLLAMA = True` after `ollama signin` for a real call.
- Three requests share one file: the lost-card question, the card-number balance question, and the same balance question with the tool timing out (so `write_answer` returns "Service busy" with no model call).

Real output (IDs and latencies differ per run):

```text
User saw (e13f6cc8): Here is what I found.
User saw (f1015db0): Here is what I found.
User saw (1fdccca5): Service busy, please try again later.

Per-request summary
  e13f6cc8 ok       total    0.7 ms tokens 51 cost $0.000035 path ['decide_route', 'retrieve', 'choose_tool', 'run_tool', 'write_answer']
  f1015db0 ok       total   55.6 ms tokens 41 cost $0.000029 path ['decide_route', 'choose_tool', 'run_tool', 'write_answer']
  1fdccca5 DEGRADED total   52.5 ms tokens 0 cost $0.000000 path ['decide_route', 'choose_tool', 'run_tool', 'write_answer']

Spans of failing request 1fdccca5
  node  decide_route       0.0 ms ok
  node  choose_tool        0.0 ms ok
  tool  lookup_balance    50.3 ms ERROR TimeoutError: mcp server did not answer in 0.05s
  node  run_tool          52.5 ms ERROR TimeoutError: mcp server did not answer in 0.05s
  node  write_answer       0.0 ms ok

Trace lines in state (same request, tr() format):
  cid=1fdccca5 decide_route +1ms route=tool
  cid=1fdccca5 choose_tool +4ms tool=lookup_balance
  cid=1fdccca5 run_tool +59ms ERROR TimeoutError
  cid=1fdccca5 write_answer +64ms degraded

Incident note
  Symptom   : answer was 'Service busy' (fallback=True)
  Root cause: first error is the tool 'lookup_balance' -> TimeoutError: mcp server did not answer in 0.05s
  Evidence  : slowest span run_tool 52.5 ms; model spans in this request: 0
  PII check : card number in trace file? False | in state trace? False
```

Key lesson: the symptom is in `write_answer`, the root cause is the `lookup_balance` span upstream. Requests 2 and 3 have the same path; only the spans tell them apart. This is what Team Orion was missing.

## Lab Steps
Open the notebook in VS Code (Jupyter extension), choose the project's `.venv` as the kernel, run cells with Shift + Enter.
```cmd
uv sync
code Day-04-Observability-Tracing\example.ipynb
```
1. Run Steps 0-7. For the failing request: which span failed first, and which is slowest?
2. Experiment 1: tool takes 1 second, no fault. Predict: no error, but the tool and node spans dominate latency.
3. Experiment 2: a careless span logs the question. Predict whether the privacy check catches it (it prints `True`).
4. Experiment 3: a new `cid` in every step. Predict how many tracking numbers one request gets (5).
5. Experiment 4: split `run_tool` time into tool time and the node's own time.
6. Optional: `USE_OLLAMA = True` after `ollama signin`; or the LangSmith peek if you have a free key.

## Assignment (workbook lab): Instrument the agent and diagnose a deliberately introduced failure
1. Instrument your own graph (the Day 3 SupportDesk refactor or your L2 agent) with `traced`, `tr()` lines, a tool span and a model span.
2. A partner changes one line to inject a failure (slow tool, exception or empty context) without telling you.
3. From the trace only, write a four-line incident note: symptom, root-cause span, evidence (the JSON line), impact (how many requests, how much extra time or cost).
4. Show the trace file and `trace` lines contain no personal data (use "My card is 4111111111111111, what is my balance?").

## Production Checklist (reuse as release-checklist lines on Day 19)
- Every node, tool call and model call emits a span with `cid`, `latency_ms` and `error`; a test counts the spans of one request.
- Model spans carry `tokens_in`, `tokens_out`, `cost_usd`; per-request totals are computed.
- One `cid` per request at the API edge, on every span and every `tr()` line (later in the audit log too).
- A test greps the trace for the card number used in the request and finds nothing.
- Someone other than the author can name the first failing span from the trace alone.
- Traces go to a store you can search (a file today, a tracing tool in production); an agent with no traces does not ship.
