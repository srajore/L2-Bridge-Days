# Bridge 1 — L2 Recap & Why LangGraph

## What You'll Learn Today

- Name what changed between last year's L2 (plain LangChain, no LangGraph) and this year's L2/L3 (LangGraph throughout).
- Explain the difference between a workflow (developer controls every transition) and an agent (the model chooses one).
- Explain SDLC vs. ADLC, and identify a step that should stay a plain function rather than become an agent.
- Read a LangGraph StateGraph: state, nodes, edges, START, and END.
- Trace the same request through a hand-written function chain and through an equivalent LangGraph graph.
- Run a two-version example file and predict its output before running it.

## Why This Matters

Last year you built L2 on plain LangChain: chains, prompt templates, and a simple agent, with no shared state object and no visible graph. This year's L2 -- and everything in L3 -- is built on LangGraph instead. Before any new mechanics, this session makes the shift concrete: the same small routing task, first as a hand-written function chain (last year's style), then as an explicit graph of state, nodes, and edges you can point to and trace. Everything else in this bridge assumes you can see that difference.

## Key Concepts

**What changed, and why.** Old L2 called functions directly, one after another, with no shared state object and no way to print what the system looked like mid-flight. New L2 -- and every day of L3 -- assumes LangGraph: state, nodes, edges, START/END, conditional routing, checkpointing, and interrupts. That gap, not any single new API, is what this bridge exists to close. None of the old L2 material is wasted -- GenAI fundamentals, embeddings, and RAG concepts all carry forward -- but the way you assemble them changes.

**Agents vs. workflows.** A workflow follows a fixed path no matter what the input says -- the developer wrote every transition. An agent is a workflow where, at one specific point, the model's own output chooses the next step, from a bounded set of options. Most of what you already built in old L2 was a workflow wearing an agent's name; L3 assumes you can tell the difference on sight, because production boundaries, approvals, and guardrails all depend on knowing exactly where that choice happens.

**SDLC vs. ADLC, and when not to use an agent.** SDLC is the human-run software development lifecycle; ADLC is the same idea applied to an agent's own request-to-resolution lifecycle -- requirements, design, build, verify, release, operate. Not every step in either lifecycle deserves an agent: a fixed check, a lookup, or a deterministic transform is a workflow node, not a model decision. Adding an agent where a plain function would do only adds cost, latency, and unpredictability for no benefit.

**State, nodes, edges, START, and END.** State is the shared data structure that moves through the graph. A node is a plain function that reads state and returns a partial update. An edge wires one node to the next. START and END are markers, not workers -- they don't do business logic. Building a graph is four steps: create a StateGraph, add nodes, add edges, then compile; calling .invoke() sends your starting state into the first node and returns whatever state remains once the path reaches END.

## Code Walkthrough — `Bridge-Day-01-L2-Recap-Why-LangGraph/example.py`

```python
"""Bridge Session 1: same request, two ways -- a fixed Python
chain (last year's L2 style), then the same steps as a graph."""

from langgraph.graph import END, START, StateGraph


def old_l2_style(request):
    cleaned = request.strip().lower()
    if "reset" in cleaned:
        return "Route to: account help"
    return "Route to: general support"


def clean_request(state):
    return {"request": state["request"].strip().lower()}


def classify_request(state):
    topic = "account" if "reset" in state["request"] else "general"
    return {"topic": topic}


def create_response(state):
    return {"message": f"Route to: {state['topic']} help"}


graph_builder = StateGraph(dict)
graph_builder.add_node("clean", clean_request)
graph_builder.add_node("classify", classify_request)
graph_builder.add_node("respond", create_response)
graph_builder.add_edge(START, "clean")
graph_builder.add_edge("clean", "classify")
graph_builder.add_edge("classify", "respond")
graph_builder.add_edge("respond", END)
graph = graph_builder.compile()

print("Old L2 style:", old_l2_style("Please reset my password"))
result = graph.invoke({"request": "  Please RESET my password  "})
print("LangGraph style:", result["message"])

```

1. `old_l2_style` is a plain function chain -- exactly how last year's L2 would have built this: no state object, no visible steps, just nested logic.
2. `clean_request` is the first node. It reads `state["request"]` and returns the cleaned text as an update.
3. `classify_request` is the second node. It reads the cleaned request and returns a `topic` field.
4. `create_response` is the third node. It reads `topic` and builds the final message.
5. `StateGraph(dict)` creates the graph builder; the three `add_node` calls register the functions, and the four `add_edge` calls wire the fixed path `START -> clean -> classify -> respond -> END`.
6. The script runs both versions on the same sample request and prints each result, so you can compare them side by side.

## Hands-On Lab (~30 minutes)

**Goal:** see the same logic two ways, and name the graph's parts.

**Graph to draw:** `START -> clean -> classify -> respond -> END`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-01-L2-Recap-Why-LangGraph\example.py
```

**Walkthrough steps:**

1. Read the `old_l2_style` function first -- this is the shape you already know.
2. Find the three node functions: `clean_request`, `classify_request`, `create_response`.
3. Find `StateGraph` and the three `add_node` registrations.
4. Follow the edges from `START` to `END`.
5. Predict the printed result for both versions before you run the file.

**Control question:** Who controls every transition in the LangGraph version? The developer -- the path is fixed, exactly like the old-L2 version, just now explicit and traceable.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the sample request near the bottom of `example.py`.
2. Predict the current output for both versions without running the file.
3. Run the example from the repository root.
4. Change only the sample request text.
5. Predict the new route before running again.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call -- this session's example is intentionally deterministic.

## Before You Move to Bridge 2

- [ ] The file runs successfully on your machine.
- [ ] You can name the state, all three nodes, and the edges connecting them.
- [ ] You can explain, in one sentence, how old L2 built this same logic differently.
- [ ] You made one small change, predicted the result, then confirmed it by running again.
- [ ] You can explain who controls the next step in the LangGraph version.
