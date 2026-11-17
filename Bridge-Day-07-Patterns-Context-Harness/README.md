# Bridge 7 — Agentic Patterns, Context Engineering & Harness Preview

## What You'll Learn Today

- Explain the router/specialist agentic pattern and when to use it.
- Explain the act-and-verify (evaluator-optimizer-style) pattern and why it needs a bounded retry limit.
- Combine both patterns in one graph: route, act, verify, and retry if needed.
- Explain context engineering as a concept: what's in state versus what a node actually needs.
- Describe, at a preview level, what a harness adds around an agent: policies, validation, telemetry.
- Predict how many attempts a run will take before it passes verification.

## Why This Matters

Every session so far has been a single fixed shape. Real agent design means choosing between several recurring shapes -- and knowing when a bounded loop, not just a straight line, is the right one. This closing bridge session previews three ideas at once, deliberately lightly, because L3 gives each of them a full session of its own: picking a pattern deliberately (router/specialist here), building in verification with a hard retry limit (the harness idea), and being conscious of exactly what context a node actually needs rather than passing everything to everyone. None of this is new mechanics -- it's everything from Bridges 1 through 6, recombined and named.

## Key Concepts

**The router/specialist pattern.** A router node looks at the request and decides which specialist node should handle it -- structurally identical to Bridge 2's conditional routing, just applied to picking a whole handler rather than a short branch. This is one of several recurring agentic patterns; others include planner/executor (plan the steps, then execute them) and reflection/verifier (produce a draft, then critique it). Picking a pattern deliberately, and being able to name which one you picked, is what L3 assumes.

**Act-and-verify, with a bounded retry.** A specialist produces a draft; a `verify` node checks it against a simple, deterministic rule; if it fails, the graph loops back and tries again -- but only up to `MAX_ATTEMPTS`. That bound is not optional: an unbounded retry loop is exactly the kind of thing that turns a small bug into an unlimited bill. This is the harness idea in miniature -- a policy (the attempt limit) wrapped around an otherwise unsupervised loop.

**Context engineering: what a node actually needs.** Every node in this bridge has had to decide exactly what to read from state and what to carry forward -- that's context engineering in its smallest form: task context (what this node is being asked to do), state/memory context (what's been carried forward), and tool context (what a called function needs). A node that receives more state than it needs isn't wrong, but a system that never asks the question tends to leak irrelevant or stale context into places it doesn't belong -- exactly what L3's Production Context Engineering session spends a full day on.

**A harness, previewed.** A harness is the wrapper around an agent that isn't the agent's core logic: policies (like the attempt limit here), validation (the `verify` node), and -- in a real system -- telemetry recording what happened on every run. This session's `MAX_ATTEMPTS` and `verify` node are a harness in miniature. L3's Production Harness Engineering session is this same idea, generalized into something reusable across many agents rather than hard-coded into one.

## Code Walkthrough — `Bridge-Day-07-Patterns-Context-Harness/example.py`

```python
"""Bridge Session 7: a router pattern chooses a specialist,
then a bounded act-and-verify loop (the harness idea) checks
the result before finishing."""

from langgraph.graph import END, START, StateGraph

MAX_ATTEMPTS = 3  # harness-style bounded loop -- never spin forever


def router(state):
    route = "network" if "vpn" in state["request"].lower() else "account"
    return {"request": state["request"], "route": route, "attempt": state.get("attempt", 0)}


def select_specialist(state):
    return state["route"]


def network_specialist(state):
    attempt = state["attempt"] + 1
    draft = "VPN." if attempt < 2 else "Reconnect the VPN client, then sign in again."
    return {"request": state["request"], "route": state["route"], "attempt": attempt, "draft": draft}


def account_specialist(state):
    attempt = state["attempt"] + 1
    draft = "Reset." if attempt < 2 else "Reset the account password from the portal."
    return {"request": state["request"], "route": state["route"], "attempt": attempt, "draft": draft}


def verify(state):
    passed = len(state["draft"].split()) >= 3  # simple, deterministic check
    return {
        "request": state["request"],
        "route": state["route"],
        "attempt": state["attempt"],
        "draft": state["draft"],
        "passed": passed,
    }


def choose_next_step(state):
    if state["passed"] or state["attempt"] >= MAX_ATTEMPTS:
        return "done"
    return "retry"


graph_builder = StateGraph(dict)
graph_builder.add_node("router", router)
graph_builder.add_node("network", network_specialist)
graph_builder.add_node("account", account_specialist)
graph_builder.add_node("verify", verify)
graph_builder.add_edge(START, "router")
graph_builder.add_conditional_edges("router", select_specialist, {"network": "network", "account": "account"})
graph_builder.add_edge("network", "verify")
graph_builder.add_edge("account", "verify")
graph_builder.add_conditional_edges("verify", choose_next_step, {"retry": "router", "done": END})
graph = graph_builder.compile()

result = graph.invoke({"request": "My VPN is disconnected"})
print("Route used:", result["route"])
print("Attempts:", result["attempt"])
print("Final draft:", result["draft"], "-- passed:", result["passed"])

```

1. `router` decides `network` or `account`, re-threading `request` and `attempt` forward.
2. `network_specialist` and `account_specialist` each produce a `draft` -- deliberately too short on the first attempt, so you can see the retry actually happen.
3. `verify` checks the draft with a simple word-count rule and re-threads everything forward alongside the new `passed` field.
4. `choose_next_step` reads `passed` and `attempt`: retry (back through `router`) if it failed and the limit isn't reached, otherwise `done`.
5. `MAX_ATTEMPTS` is the harness policy -- the bound that keeps this loop from running forever.
6. The sample request takes two attempts: the first draft is too short, the second passes.

## Hands-On Lab (~30 minutes)

**Goal:** trace a bounded retry loop and predict how many attempts it takes.

**Graph to draw:** `START -> router -> (network|account) -> verify -> (retry: router | done: END)`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-07-Patterns-Context-Harness\example.py
```

**Walkthrough steps:**

1. Find `MAX_ATTEMPTS` and explain, out loud, what it prevents.
2. Find `verify` and the rule it checks.
3. Predict how many attempts the sample request needs before it passes.
4. Run the file and confirm your prediction.
5. Explain which of this session's three ideas (pattern, harness, context) each part of the file represents.

**Control question:** What stops this loop from running forever? MAX_ATTEMPTS -- once attempt reaches that bound, choose_next_step returns "done" regardless of whether verify passed.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the sample request near the bottom of `example.py`.
2. Predict the route, the number of attempts, and the final draft without running the file.
3. Run the example from the repository root.
4. Change `MAX_ATTEMPTS` to `1` and predict what the final `passed` value will be.
5. Run the same command again.
6. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call -- this session's example is intentionally deterministic.

## Before You Move to L3 Session 1

- [ ] The file runs successfully on your machine.
- [ ] You can name the router pattern and the act-and-verify pattern used here.
- [ ] You can explain what MAX_ATTEMPTS prevents, and what happened when you set it to 1.
- [ ] You can point to the one line in this file that represents "the harness."
- [ ] You can explain, in your own words, how Bridges 1 through 7 connect to L3's first day.
