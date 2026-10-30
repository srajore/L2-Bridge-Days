# Bridge 2 — LangGraph Core Mechanics: State, Nodes, Edges & Routing

## What You'll Learn Today

- Explain, precisely, how a node's return value updates shared state.
- Explain a gotcha specific to this course's plain dict state: a node's return can replace state instead of merging into it, so any field a later node still needs must be re-included.
- Add a conditional edge with add_conditional_edges and a routing function.
- Trace two different paths through the same graph, driven by state rather than by hand.
- Explain who controls the route in a conditional-edge graph (still the developer, via rules -- not the model).
- Run a routed graph and predict which branch a given input takes before running it.

## Why This Matters

Bridge 1 showed a single fixed path: every request went through the same three nodes in the same order. Real requests don't behave that way -- a one-line question and a detailed incident report shouldn't be handled identically. This session adds the piece that makes that possible: conditional edges, where the state itself -- not the developer, at runtime -- picks which node runs next. It's still entirely rule-based and developer-controlled; nothing here is an agent yet. Along the way, this session also surfaces a small but important gotcha in how this course's plain dict state behaves across nodes, so it stops being a mystery in every session from here on.

## Key Concepts

**State updates: partial merge vs. full replace.** Every node returns a dict, and LangGraph applies it as that node's state update -- but with this course's plain, untyped `dict` schema, a node's return effectively becomes the new state for the keys involved; fields the node doesn't re-mention are not guaranteed to survive into the next node. The practical rule: if a later node needs a value, the node right before it must re-include that value in its own return, even if that node didn't change it. You'll see this pattern -- "just carry the field forward" -- in every remaining example in this bridge and in L3's own labs.

**Conditional edges and routing functions.** `add_conditional_edges(source_node, routing_function, mapping)` replaces a single fixed `add_edge` with a decision point: after `source_node` runs, `routing_function` reads the current state and returns a short label (like `"short"` or `"long"`), and `mapping` says which real node that label points to. The routing function is plain Python -- an `if`/`else` on a state value -- so the decision is fully deterministic and fully explainable.

**Branching and convergence.** Two different node paths can each do their own thing and then converge back to the same place -- in this session's example, `short` and `long` are different nodes but both lead to `END`. A graph can just as easily converge back into a shared node instead of `END`, which is exactly the shape sessions 3 and 4 build on: a shared tool step, or a shared verification step, reached by more than one route.

**Still a workflow, not an agent.** Even though the path now varies by input, the developer wrote every possible route and the rule that picks between them -- the model is not involved in this decision at all. That distinction matters: L3 assumes you can look at any conditional edge and say whether a human wrote the routing rule (a workflow) or a model's own output selected the next node (an agent). This session is entirely the former.

## Code Walkthrough — `Bridge-Day-02-LangGraph-Core-Routing/example.py`

```python
"""Bridge Session 2: state, nodes, and edges, plus a
conditional route the state itself decides between."""

from langgraph.graph import END, START, StateGraph


def clean_request(state):
    return {"request": state["request"].strip()}


def count_words(state):
    return {"request": state["request"], "word_count": len(state["request"].split())}


def choose_route(state):
    return "short" if state["word_count"] <= 3 else "long"


def short_reply(state):
    return {"message": "Quick request -- routed straight to the FAQ bot."}


def long_reply(state):
    return {"message": "Detailed request -- routed to a support engineer."}


graph_builder = StateGraph(dict)
graph_builder.add_node("clean", clean_request)
graph_builder.add_node("count", count_words)
graph_builder.add_node("short", short_reply)
graph_builder.add_node("long", long_reply)
graph_builder.add_edge(START, "clean")
graph_builder.add_edge("clean", "count")
graph_builder.add_conditional_edges("count", choose_route, {"short": "short", "long": "long"})
graph_builder.add_edge("short", END)
graph_builder.add_edge("long", END)
graph = graph_builder.compile()

result = graph.invoke({"request": "VPN is down"})
print(result["message"])

```

1. `clean_request` strips the request text and returns it.
2. `count_words` reads that text, and -- following the carry-forward rule above -- returns both `request` and the new `word_count` field.
3. `choose_route` is the routing function: it reads `word_count` and returns the label `"short"` or `"long"`. It does not return a state update -- only a label.
4. `add_conditional_edges("count", choose_route, {...})` wires that label to a real node name.
5. `short_reply` and `long_reply` are two different endings that both lead to `END`.
6. `graph.invoke(...)` runs one sample request through whichever path its word count selects.

## Hands-On Lab (~30 minutes)

**Goal:** trace a routed graph and predict which branch a given input takes.

**Graph to draw:** `START -> clean -> count -> choose_route -> (short | long) -> END`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-02-LangGraph-Core-Routing\example.py
```

**Walkthrough steps:**

1. Find the two branch nodes, `short_reply` and `long_reply`, and the routing function `choose_route`.
2. Find `add_conditional_edges` and read its three arguments.
3. Count the words in the sample request and predict which branch it takes.
4. Run the file and confirm your prediction.
5. Explain, out loud, why `count_words` returns `request` again even though it didn't change it.

**Control question:** Who decides the route -- the developer or the model? The developer: `choose_route` is a plain Python rule, not a model call.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the sample request near the bottom of `example.py`.
2. Predict the current branch and output without running the file.
3. Run the example from the repository root.
4. Change the sample request so it crosses the word-count threshold into the other branch.
5. Predict the new branch before running again.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call -- this session's example is intentionally deterministic.

## Before You Move to Bridge 3

- [ ] The file runs successfully on your machine.
- [ ] You can name the state, all four nodes, and the routing function.
- [ ] You can explain why `count_words` re-returns `request` even though it is unchanged.
- [ ] You made one small change that crossed the routing threshold, predicted the branch, then confirmed it.
- [ ] You can explain why this graph is still a workflow, not an agent.
