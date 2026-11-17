# Day 1 — L2-to-L3 Bridge: Production Architecture

## What You'll Learn
- Explain, in plain words, why a working agent is not yet a production agent.
- Write NFRs (non-functional requirements) as numbers that can be tested.
- Mark the trust boundaries and the API/service boundary, and say what is checked at each.
- Decide where state lives, who owns the `thread_id`, and how long state is kept.
- List failure domains (each with a timeout and a fallback) and a risk register (risk -> mitigation).
- Run a checker that turns a spec into a gap report, then convert the L2 prototype into a production target.

## Already Covered in L2 (not repeated)
- L2 Days 1-5: what an agent is, `StateGraph`, nodes, edges, conditional routing, tool nodes.
- L2 Days 7-8: checkpointer, `thread_id`, interrupt/resume basics.
- L2 Day 20: an agent with guardrails and a golden set. Today's starting point is the SupportDesk prototype built in that style: one process, no checkpoint, no limits.

Today teaches only the new part: reading SupportDesk as a *service* and writing down what production needs.

## Why This Matters
An agent that works on your laptop can still fail in production. It hangs when the model is slow, loses all state on restart, lets one user read another user's thread, or trusts raw input. These are **design gaps**, not coding bugs, and they are cheapest to find *before* you build. Today you find them on paper (and with a small checker). The next 18 days close them one by one.

## Your Journey
- **Yesterday:** in L2 you built an agent that gives correct answers.
- **Today:** we ask a new question: "Does it keep working, safely and cheaply, when things go wrong?" We write the production target.
- **Tomorrow (Day 2):** we start building it. The first gap we close is state: a checkpoint that survives a restart, and a pause that waits for a human.

## SupportDesk so far
- Before today: the L2-style SupportDesk prototype (answers policy questions, `lookup_balance`, `freeze_card`) in one process, no checkpoint, no limits.
- Added today: the production target architecture, NFRs, trust/API boundaries, failure domains and risk register, written as `PRODUCTION_TARGET` and checked by `example.ipynb`.
- Becomes in Day 19: the `NFR` dict in `agent.py` (`latency_budget_ms` 30000, `token_budget` 200, `mcp_timeout_s` 30, `max_tool_calls` 1), the architecture `server.py` + `agent.py` + `app.py` (`AskRequest`, `/ask`, `/ready`), and the release checklist.

## Key Concepts
**Prototype vs production.** A prototype proves the logic works. Production adds a service wrapper, durable state, limits and an owner. Every later day closes one gap that today's report finds.

**NFR (non-functional requirement).** A target you can measure, such as "answer within 30 seconds". Words like "fast" or "reliable" are not NFRs. SupportDesk's four hard limits are the Day 19 `NFR` dict: `latency_budget_ms` 30000, `token_budget` 200, `mcp_timeout_s` 30, `max_tool_calls` 1. Today we add `availability_pct` 99.5 and `cost_per_request_usd` 0.02. The checker rejects anything that is not a positive number.

**API/service boundary.** The edge where outside callers reach your agent. SupportDesk is called over `POST /ask` (plus `/health`, `/ready`, `/version`; this is Day 19's `app.py`). The boundary needs:
- authentication (`x-api-key`, and refuse when the key is missing: "fail closed"),
- a request schema (`AskRequest`),
- a size limit (500 characters),
- a rate limit,

so bad input is refused *before* any graph node runs. On Day 16 it is packaged as a container (Containerfile, `podman build`/`podman run`). Today you only specify the boundary.

**Trust boundary.** A line where data moves from something you do not control (user text, retrieved web pages, model output) to something you do (tools, database). Check the data at every crossing, including *model output -> tool call*. For SupportDesk:
- user text -> `guard_input`,
- tool choice -> `ROLE_TOOLS` (only `lookup_balance`; `freeze_card` needs a human),
- answer -> user via `redact` (a card number must never leave).

**Stateful agent architecture.** State is more than "a checkpointer". Decide three things: the store (durable SQLite, not memory), who issues the `thread_id` (the server builds it from user + correlation id, never from the request body), and how long state is kept (retention).

**Failure domain.** A part of the system that fails as one unit (the MCP server, the model API, process memory). Each one needs a timeout, a fallback, and a known place where state survives.

**Production risk register.** A short list: "what can go wrong -> what stops it". A risk with no mitigation is a gap.

## L2 vs L3 (what changed)
| L2 | L3 |
| --- | --- |
| "Does it give the right answer?" | "Does it keep working, safely and cheaply, when things go wrong?" |
| A function you call | A service with auth, schema and size limits |
| State in memory | Durable store, owned thread ids, retention |
| A model call may hang | Every call has a timeout and a fallback |
| Risks are in your head | Risks are written down with a mitigation |

## Concept Corner: the same ideas in other places
*Concept only. Nothing here changes today's lab; it shows that the vocabulary you learn today is shared across the industry.*

**The idea.** Before building an agent, decide *how much agent you need* and write down the limits it must live within.

**In a managed cloud.** Cloud providers publish architecture guidance for AI workloads (for example the AWS Well-Architected framework and its generative-AI guidance). The questions are the same as today's: what is the reliability target, who may call the service, where does data live, what does one request cost? They also offer a hosted *agent runtime* (for example Amazon Bedrock AgentCore) that gives you ready-made session state, tool access, identity and tracing. The trade-off is "build it yourself and control everything" versus "rent the runtime and ship faster". Today's gap report is the checklist you would use to judge either choice.

**In Claude's world.** Anthropic's guidance on building agents separates two things:
- a **workflow**: code decides the steps (SupportDesk's fixed graph is mostly this), and
- an **agent**: the model decides the next step in a loop.

The advice is to start with the simplest option that works and add agent freedom only where it pays off. The Claude Agent SDK packages the agent loop, tools and permissions so you do not rebuild them. This course builds the loop with LangGraph so you can see every part.

**How we do it locally.** Ollama is the model, LangGraph is the loop and state, and `PRODUCTION_TARGET` is the written design. Same ideas, no cloud account needed.

| Idea | Today's file | Managed / Claude name (concept only) |
| --- | --- | --- |
| Measurable limits | `nfr` section | service quotas, latency and availability targets |
| Who may call us | `api_boundary` | API gateway, identity and access control |
| Fixed steps vs model-chosen steps | the graph | workflow vs agent |
| State that survives a restart | `state` section | managed session memory |

## Code Walkthrough — `Day-01-L2-to-L3-Bridge-Production-Architecture/example.ipynb`
The notebook explains every idea with a short story (an analogy) *before* the code, so you can read it like a guided tour: a restaurant opening for the public, airport security, a hotel front desk, a fuse box. It has seven steps: setup, the two forms, the six checks, the conveyor belt, the inspection run, a gap chart, and your experiments.

Two plain dictionaries describe the same SupportDesk agent: `L2_PROTOTYPE` (many `None` values, meaning "not decided yet") and `PRODUCTION_TARGET` (every field filled, using the Day 19 names and numbers). Each spec has six sections: `nfr`, `api_boundary`, `trust_boundaries`, `state`, `failure_domains`, `risks`.

The graph is a straight line of seven nodes: `check_nfrs`, `check_api_boundary`, `check_trust_boundaries`, `check_state_architecture`, `check_failure_domains`, `check_risk_register`, `write_report`. Each check adds strings to `gaps`; `write_report` numbers them and prints a verdict. The same graph runs twice, once per spec, so you see the prototype become the target. No model is called, so the notebook runs offline.

Target architecture the second spec describes (this is the Day 19 architecture; later days build each box):

```text
client --(x-api-key, AskRequest, 500 chars, 30/min)--> app.py /ask --> agent.py graph --> server.py MCP (30 s, fallback)
                                                                          | guard_input -> decide_route -> retrieve (P1-P4)
                                                                          | -> choose_tool -> check_policy -> run_tool
                                                                          | -> write_answer -> guard_output -> audit
                                                                          +--> model API (optional, 20 s, fallback)
                                                                          +--> SQLite checkpoints (thread_id = user + cid, 30 days)
```

Real output:

```text
Gap report for SupportDesk (L2 prototype)
Gaps found: 26
1. NFR: 'latency_budget_ms' is not a positive number
2. NFR: 'token_budget' is not a positive number
3. NFR: 'mcp_timeout_s' is not a positive number
4. NFR: 'max_tool_calls' is not a positive number
5. NFR: 'availability_pct' is not a positive number
6. NFR: 'cost_per_request_usd' is not a positive number
7. API: 'endpoint' is not defined
8. API: 'auth' is not defined
9. API: 'request_schema' is not defined
10. API: 'max_request_chars' is not defined
11. API: 'rate_limit_per_min' is not defined
12. TRUST: user input crosses into the agent without validation
13. TRUST: model output reaches tools or users without validation
14. TRUST: no tool allowlist
15. STATE: checkpoints live in memory and are lost on restart
16. STATE: nobody decides where thread_id comes from (users could read each other's threads)
17. STATE: no retention period for saved state
18. FAILURE: mcp_server call has no timeout
19. FAILURE: mcp_server has no fallback
20. FAILURE: model_api call has no timeout
21. FAILURE: model_api has no fallback
22. RISK: 'model outage' has no mitigation
23. RISK: 'prompt injection' has no mitigation
24. RISK: 'freeze_card without approval' has no mitigation
25. RISK: 'duplicate freeze_card' has no mitigation
26. RISK: 'card number in answer' has no mitigation
Verdict: NOT READY for production

Gap report for SupportDesk (production target = Day 19 architecture)
Gaps found: 0
Verdict: READY for review
```

## Lab Steps
Open the notebook in VS Code (Jupyter extension), choose the project's `.venv` as the kernel, then run the cells from top to bottom with Shift + Enter.
```cmd
uv sync
code Day-01-L2-to-L3-Bridge-Production-Architecture\example.ipynb
```
1. Run Steps 0-5 and read the 26 gaps of the prototype. The bar chart in Step 5 shows which group (NFR, API, TRUST, STATE, FAILURE, RISK) has the most.
2. Step 6, Experiment 1: set `availability_pct` to `None` on a copy of the target. Predict the gap count (1) before you run.
3. Experiment 2: also set `checkpoint_store` to `"memory"`. Predict again (2).
4. Experiment 3 (bonus): add a new risk with no mitigation, then fix it and watch the report return to zero.

## Assignment (workbook lab): Convert an L2 solution into a production target architecture
The L2 solution you assess is the SupportDesk prototype (policy answers, `lookup_balance`, `freeze_card`; one process, no checkpoint, no limits). Deliver:
1. A one-page target architecture sketch like the one above (service boundary, model, MCP tools, state store).
2. Three NFRs with numbers (use the Day 19 `NFR` names), a trust-boundary list with the check at each, a failure-domain table (timeout, fallback, where state lives) and a risk register of at least three risks.
3. Both specs encoded as dictionaries in a new notebook cell (prototype and target) and the two gap reports from the checker. The target must end at zero gaps. Keep the target spec: it is the Day 19 capstone target, and each later day closes one of its gaps. If you prefer, assess your own L2 Day 20 agent instead, with the same structure.

## Production Checklist (reuse as release-checklist lines on Day 19)
- NFRs: latency, availability and cost-per-request each have a number (the checker reports 0 NFR gaps).
- API boundary: endpoint, auth, request schema and max request size are defined, and oversized/invalid requests are refused before the graph runs.
- State: checkpoints are in a durable store, `thread_id` comes from the authenticated session, retention is set.
- Every external dependency (model, each tool system) has a timeout and a fallback in the failure-domain table.
- Risk register: every listed risk has a mitigation and the gap report prints `READY for review`.
