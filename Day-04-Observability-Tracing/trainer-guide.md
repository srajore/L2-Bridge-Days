# Day 4 Trainer Guide — Observability and Tracing

## Outcome
A learner can explain why an agent needs traces (not just logs), name the four pillars, add `tr()` lines and node, tool and model spans to the SupportDesk graph, record time, tokens, cost, errors and a correlation ID in a JSON-lines file, find a root cause from the trace and write an incident note. They can also name the common tracing tools and when each fits.

## Files
- `slides.pptx` — interactive (section tabs, Agenda button, predict/reveal slides). Use Slide Show mode so links work.
- `example.ipynb` — traced SupportDesk graph as a flight-recorder story; three requests, injected `lookup_balance` failure, incident note, PII check, four predict-then-run experiments, optional LangSmith peek (skips itself without a key).
- `README.md`, `trainer-guide.md`
- Quiz: `quizzes/Day-04-quiz.csv`

## Setup (cmd)
```cmd
uv sync
code Day-04-Observability-Tracing\example.ipynb
```
Choose the project's `.venv` as the kernel, run cells with Shift + Enter. No `ollama signin` and no account needed for the default run. The notebook creates and deletes `day04_trace.jsonl`. `tr()` and `cid` are copied exactly from Day 19's `agent.py`; later days add lines to the same trace (Day 5 `FALLBACK`, Day 9 `docs=`, Day 12 `check_policy`). Do not re-teach tokens and cost (L2 Day 14).

Optional extras: `USE_OLLAMA = True` after `ollama signin`; the LangSmith peek needs a free LangSmith key in `.env` (`LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT`). `.env` must be in `.gitignore`.

## 120-Minute Flow
1. 0-10 — **The hook.** Tell the Team Orion 3:14 AM story (do not show slides first). Ask the room: "Could your agent answer the CFO's question for any run in the last 30 days?"
2. 10-25 — **Why.** Agents fail quietly; non-determinism; cost, trust, audit, improvement; the gate to production. Predict slide ("Service busy": where is the cause?).
3. 25-40 — **Four pillars.** Traces, logs, metrics, evals with the diary / gauge / flight recorder / investigator analogy. "If you build one first, build traces."
4. 40-60 — **Notebook walkthrough.** `tr`, `emit`, `traced`, `call_tool`, `call_model`; the three kinds of span; `cid`; privacy.
5. 60-70 — **See it run.** Steps 5-7: per-request summary, failing trace, incident note. Symptom versus root cause.
6. 70-75 — Break.
7. 75-95 — **Lab.** Step 8, experiments 1-4 (predict first).
8. 95-105 — **Concept Corner.** Tools landscape (LangSmith, Langfuse, Phoenix, AgentOps, OpenTelemetry, others). Optional LangSmith peek if learners have a key; otherwise show a screenshot or demo from the trainer's laptop.
9. 105-115 — **Assignment.** Partner injects a failure; learner writes the four-line incident note.
10. 115-120 — Exit check.

If time is short, cut Experiment 4 and the LangSmith peek first; keep the hook, the failing trace and the incident note.

## Tips for the Hook
Tell it, do not read it. Keep the three things the team had (app logs, a stray print, the provider dashboard) and the one thing they lacked (the reasoning trail). The story is fictional but typical: refund bots, booking bots and internal copilots given too much tool access. Return to it three times: after the failing trace ("this would have answered the CFO"), after the pillars ("Orion had logs and metrics, no traces"), and in the exit check.

## Walkthrough Questions
1. What was missing at Team Orion: logs, metrics, traces or evals? Why could the other three not answer "why did it decide that"?
2. Why build traces before evals?
3. Where does `cid` come from and where is it used (spans, `tr()` lines, later the audit record)?
4. Why are there two error lines for one failure? Which is the root cause?
5. Why does the failing request have no model span, and what does that tell you?
6. Why does the trace store `state_keys_changed` and not values? Why are `+<ms>ms` values cumulative from `t0`?
7. Concept Corner: where do you find the numbers behind `tokens_in` and `tokens_out` in a Claude API response? What plays the role of `cid` across a boundary?
8. Concept Corner: name one case where you would pick a self-hosted tool (Langfuse, Phoenix) over LangSmith.

## Common Mistakes
- Treating the cost numbers as real prices; they are placeholders.
- Logging full prompts or personal data into the trace (Experiment 2).
- Swallowing the exception without recording it.
- Creating a new correlation ID per node instead of per request (Experiment 3).
- Reading only the final answer and blaming the last node.
- Reading the node span as the cause when the tool span inside it is the cause (Experiment 4).
- Forgetting to load `.env` or to set the tracing variable: nothing appears in the tool. That is itself a good "debug your observability" moment.
- Committing API keys. Ask "who has pushed a key to GitHub?" and then show `.gitignore`.

## Exit Check
"The user says the agent gave a generic answer. What do you open first, and which fields do you look at?" (The trace for that correlation ID; the first span with a non-null `error`, the slowest span, and whether a model span exists.) Then: "If Team Orion had had this on day one, what would the on-call engineer have opened at 3:14 AM?"

## What Was and Was Not Live-Verified
- Verified: the original `example.ipynb` (Steps 0-9) was executed top to bottom with `nbclient` on Windows (offline stub), no errors; output matches the README (IDs and latencies vary). Experiments 1-4 gave the stated results. Before the SupportDesk rebase, `USE_OLLAMA = True` (`gpt-oss:120b-cloud`) recorded 334 tokens and about $0.000415 at illustrative prices; a real answer contained a non-ASCII space that crashed `print` on a Windows console, so encode to ASCII if you switch (not re-tested).
- The new optional LangSmith step (Step 10): the whole notebook was re-run with `nbclient` after adding it; with no key set the cell prints "Skipped" and nothing else changes. The `@traceable` and `langsmith_extra` (tags, metadata) path with a real key was not run.
- The 24-slide deck was rebuilt and the changed slides were checked as rendered images; it was not clicked through in Slide Show mode.
- Not verified: the notebook in the VS Code UI cell by cell, the slides in a live click-through, the assignment, and any real LangSmith upload with a key (none was available). Prices are placeholders. Stub token counts are `len(prompt)//4` and a fixed 9. Spans are plain JSON lines with no parent IDs (nesting is inferred from order and names).
- The tools table (LangSmith, Langfuse, Phoenix, AgentOps, OpenTelemetry, Helicone, Portkey, Datadog) is a concept summary taken from the source material, not demonstrated. Product features and names change; check vendor docs before quoting specifics. Hosted-model names (for example on Groq) change too: look up the current model string instead of copying one from slides.
