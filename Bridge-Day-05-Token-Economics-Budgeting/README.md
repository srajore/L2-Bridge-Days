# Bridge 5 — Token Taxonomy, Economics & Budgeting

## What You'll Learn Today

- Name the parts of a model request: instruction, question, context, and (later) tool-call and cached content.
- Estimate the size of each part using a simple, deterministic proxy (word count).
- Explain why token drivers in RAG and agent loops compound -- retries and long context both add up.
- Set and check a token budget for a request.
- Explain the cost/latency relationship in plain terms.
- Predict whether a modified request stays within budget, before running the file.

## Why This Matters

Every graph in this bridge so far has been free to build without thinking about what a request actually costs. Old L2 never had to either -- GenAI tools and APIs were introduced, but never measured. In production, every part of a request -- the instruction, the user's question, the retrieved context, tool results -- has a size, and that size drives cost, latency, and how much context-window room is left for anything else. This session builds the smallest possible version of that discipline: measure each part, add them up, and check the total against a budget, deterministically, before anything is sent anywhere.

## Key Concepts

**Token taxonomy: what makes up a request.** A request to a model isn't one blob of text -- it's made of distinguishable parts: the instruction (what you're telling the model to do), the user's question, retrieved or supplied context, and in agent loops, tool-call arguments and results, plus anything reused from a cache. This session measures three of those parts directly; L3 and real token-aware systems measure all of them, because each one can grow independently and each one counts against the same context window.

**Word count as a token proxy.** This session estimates size with a plain word count instead of a real tokenizer -- it's not exact (a real tokenizer would split some words into multiple tokens, and count punctuation differently), but it's close enough to teach the discipline without adding a new dependency. The lesson is the shape of the practice, not the exact number: measure before you ship, always, using whatever tokenizer your actual model provides.

**Why this compounds in RAG and agent loops.** A single question-answer exchange is cheap. A RAG pipeline adds retrieved context on every call; an agent loop can call the model, a tool, and the model again, several times, for one user request; a retry after a failure doubles the cost of whatever attempt failed. None of this is visible unless you're measuring -- which is exactly why Bridge 3's checkpointing and Bridge 4's approval gate both matter for cost control too, not just correctness.

**Budgets, and what to do when you're over.** A token budget is just a number you decide in advance is the most a given request type should cost, and a check that compares the actual total against it. Being over budget isn't a crash -- it's a signal to trim context, split the request, or reconsider the approach, exactly the kind of decision L3's Performance, Cost & Scalability session asks you to make deliberately rather than by accident.

## Code Walkthrough — `Bridge-Day-05-Token-Economics-Budgeting/example.py`

```python
"""Bridge Session 5: estimate token usage per part of a
request, then check it against a simple token budget."""

from langgraph.graph import END, START, StateGraph

BUDGET = 40  # words allowed for this request type -- a stand-in token budget


def count_words(text):
    return len(text.split())


def measure(state):
    counts = {
        "instruction": count_words(state["instruction"]),
        "question": count_words(state["question"]),
        "context": count_words(state["context"]),
    }
    return {"counts": counts, "total": sum(counts.values())}


def check_budget(state):
    over_budget = state["total"] > BUDGET
    verdict = "OVER BUDGET -- trim context or split the request" if over_budget else "within budget"
    return {"counts": state["counts"], "total": state["total"], "verdict": verdict}


graph_builder = StateGraph(dict)
graph_builder.add_node("measure", measure)
graph_builder.add_node("check_budget", check_budget)
graph_builder.add_edge(START, "measure")
graph_builder.add_edge("measure", "check_budget")
graph_builder.add_edge("check_budget", END)
graph = graph_builder.compile()

result = graph.invoke(
    {
        "instruction": "Answer using only the approved context below and cite the source article.",
        "question": "How do I reset my password if I no longer have access to my recovery email?",
        "context": "Reset a password at portal.example/reset. VPN issues: reconnect and re-enter your company password.",
    }
)
print("Word estimate by part:", result["counts"])
print("Total word estimate:", result["total"], "/ budget", BUDGET)
print("Verdict:", result["verdict"])

```

1. `BUDGET` is a fixed number, standing in for a real token budget.
2. `count_words` is the simple size proxy used throughout this file.
3. `measure` reads all three parts of the request and returns both the per-part `counts` and their `total`.
4. `check_budget` reads `total`, compares it to `BUDGET`, and re-threads `counts` and `total` forward alongside the new `verdict` field.
5. The sample request is deliberately sized so you can watch it land on one side of the budget or the other.
6. The script prints the per-part breakdown, the total against the budget, and the verdict.

## Hands-On Lab (~30 minutes)

**Goal:** measure a request's parts and check them against a budget.

**Graph to draw:** `START -> measure -> check_budget -> END`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-05-Token-Economics-Budgeting\example.py
```

**Walkthrough steps:**

1. Find `count_words` and the three parts it measures in `measure`.
2. Find `BUDGET` and the comparison inside `check_budget`.
3. Add up the three counts yourself and predict the verdict before running the file.
4. Run the file and confirm your prediction.
5. Explain why `check_budget` re-returns `counts` and `total` even though it didn't change them.

**Control question:** What happens when the total exceeds the budget? Nothing crashes -- check_budget just reports OVER BUDGET, leaving the decision of what to do about it to whoever reads the verdict.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the sample `instruction`, `question`, and `context` near the bottom of `example.py`.
2. Predict the current per-part counts and the verdict without running the file.
3. Run the example from the repository root.
4. Shorten or lengthen the `context` string so the verdict flips.
5. Predict the new verdict before running again.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call -- this session's example is intentionally deterministic.

## Before You Move to Bridge 6

- [ ] The file runs successfully on your machine.
- [ ] You can name the three parts of the request being measured.
- [ ] You can explain why word count is used here instead of a real tokenizer.
- [ ] You changed the context length, predicted the verdict, then confirmed it.
- [ ] You can explain, in one sentence, why token cost compounds in RAG and agent loops.
