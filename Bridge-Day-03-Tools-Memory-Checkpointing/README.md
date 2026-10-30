# Bridge 3 — Tool Calling & State Memory / Checkpointing

## What You'll Learn Today

- Call a plain Python function as a tool from inside a graph node -- no ToolNode, no decorator.
- Explain why a typed state schema (TypedDict) merges per-key, unlike this bridge's earlier plain-dict examples.
- Compile a graph with a checkpointer and a thread ID.
- Run the same thread across two separate .invoke() calls and observe what persists.
- Explain the difference between state carried within one run and state persisted across runs.
- Predict what a second invocation on the same thread will remember, before running it.

## Why This Matters

So far every example has run start-to-finish in one `.invoke()` call, with nothing surviving afterward. Real agents need two more things: a way to call out to something outside the model (a lookup, a calculation, an API) and a way to remember facts across separate turns of a conversation, not just within one run. This session adds both, using the simplest form of each: a plain Python function used as a tool, and a checkpointer keyed by a thread ID. It also switches from this bridge's earlier plain `dict` state to a `TypedDict` schema -- the difference matters, and this session shows exactly why.

## Key Concepts

**A tool is just a plain function, called from a node.** This course does not use LangChain's `ToolNode`, decorators, or tool-calling message classes -- a "tool" is simply a plain Python function that a node calls directly, the same way any function call works. `look_up_ticket_count` takes a customer ID and returns a count; the node `use_tool` calls it and returns the result as a state update. Keeping tools this plain matters for L3's later MCP sessions: MCP standardizes exactly this idea -- calling a function with validated arguments and getting a structured result back -- and it's far easier to reason about MCP once you've called a tool the plain way first.

**TypedDict state merges per key -- unlike plain dict.** Bridge sessions 1 and 2 used a plain, untyped `dict` schema, where you had to manually carry a field forward if a later node needed it. A `TypedDict` schema behaves differently: LangGraph tracks each declared field as its own channel, and a node's partial return merges into the existing state instead of replacing it wholesale. That's why this session's state is declared as a small `TypedDict` -- it's what makes real persistence across separate `.invoke()` calls possible in the first place.

**Checkpointing and thread IDs.** `graph.compile(checkpointer=InMemorySaver())` gives the graph a place to save its state after each run. `config={"configurable": {"thread_id": "..."}}` tells it which saved conversation to use -- the same thread ID on a later `.invoke()` call picks up exactly where that thread left off, merging new input on top of what was already saved, instead of starting from nothing.

**Bounded retry and failure recovery, as a concept.** This session's example doesn't force a failure, but the same mechanism -- a checkpointer plus a thread ID -- is what lets a graph resume after a crash or a deliberate pause: whatever state was last saved for that thread is still there. L3's production reliability sessions build directly on this: retries, resumption, and bounded loops all lean on the checkpointer you just used here.

## Code Walkthrough — `Bridge-Day-03-Tools-Memory-Checkpointing/example.py`

```python
"""Bridge Session 3: a tool node backed by a plain function,
plus checkpointed memory resumed with the same thread ID."""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class SupportState(TypedDict, total=False):
    customer_id: str
    ticket_count: int
    question: str


def look_up_ticket_count(customer_id):
    """Plain Python function used as a tool -- no ToolNode, no decorator."""
    tickets = {"C100": 2, "C200": 0}
    return tickets.get(customer_id, 0)


def use_tool(state):
    if state.get("customer_id"):
        return {"ticket_count": look_up_ticket_count(state["customer_id"])}
    return {}


graph_builder = StateGraph(SupportState)
graph_builder.add_node("use_tool", use_tool)
graph_builder.add_edge(START, "use_tool")
graph_builder.add_edge("use_tool", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

settings = {"configurable": {"thread_id": "customer-C100"}}
first = graph.invoke({"customer_id": "C100"}, config=settings)
print("First run - ticket count:", first["ticket_count"])

second = graph.invoke({"question": "How many open tickets do I have?"}, config=settings)
print("Second run (no customer_id given) - remembered ticket count:", second["ticket_count"])

```

1. `SupportState` is a `TypedDict` -- this is what makes per-field merging (not full replacement) apply.
2. `look_up_ticket_count` is the tool: a plain function with no framework wrapper around it.
3. `use_tool` is the only node -- it calls the tool when a `customer_id` is present in state.
4. The graph is compiled with `checkpointer=InMemorySaver()`, and `thread_id: "customer-C100"` names the saved conversation.
5. The first `.invoke()` provides `customer_id` and gets back a `ticket_count`.
6. The second `.invoke()` provides only a `question` -- no `customer_id` -- yet `ticket_count` is still there, because the checkpointer merged this call's input on top of what the first call had already saved for this thread.

## Hands-On Lab (~30 minutes)

**Goal:** see memory persist across two separate invocations of the same thread.

**Graph to draw:** `START -> use_tool -> END  (invoked twice, same thread_id)`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-03-Tools-Memory-Checkpointing\example.py
```

**Walkthrough steps:**

1. Find `SupportState` and note it's a `TypedDict`, not a plain `dict`.
2. Find the tool function `look_up_ticket_count` and the node that calls it.
3. Find `checkpointer=InMemorySaver()` and the `thread_id` in `settings`.
4. Predict what the second `.invoke()` call will print, given it never passes `customer_id`.
5. Run the file and confirm your prediction.

**Control question:** Why does the second call still know the ticket count? Because the checkpointer saved the first call's state under that thread ID, and TypedDict state merges the new input on top of it instead of replacing it.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the two sample `.invoke()` calls near the bottom of `example.py`.
2. Predict both printed lines without running the file.
3. Run the example from the repository root.
4. Change the `thread_id` on the second call to a brand-new value.
5. Predict what happens now -- and why.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call -- this session's example is intentionally deterministic.

## Before You Move to Bridge 4

- [ ] The file runs successfully on your machine.
- [ ] You can name the tool function and the node that calls it.
- [ ] You can explain why `SupportState` is a `TypedDict` and not a plain `dict`.
- [ ] You changed the `thread_id` on the second call, predicted the effect, then confirmed it.
- [ ] You can explain what a checkpointer and a thread ID actually do, in one sentence each.
