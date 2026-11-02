# Bridge 4 — Human-in-the-Loop & RAG Re-engineered as a Graph Node

## What You'll Learn Today

- Pause a graph mid-run with interrupt() and resume it with Command(resume=...).
- Explain the maker-checker / approval-gate pattern and where it belongs in a graph.
- Rebuild old L2's RAG pipeline as a LangGraph node instead of a standalone script.
- Attach a citation (source) to a retrieved answer.
- Combine an approval gate with a retrieval step in one graph.
- Predict what happens when approval is denied, before running the file.

## Why This Matters

Old L2 built RAG as a standalone pipeline: retrieve, then generate, run start to finish with nobody checking in between. That's fine for a low-stakes demo, but L3 assumes two things old L2 never covered: that some actions need a human to approve them before they happen, and that retrieval is a node inside an agent's graph, not a separate script bolted on the side. This session rebuilds your existing RAG knowledge around both ideas at once -- the same retrieve-then-generate logic you already know, now with an approval gate in front of it and a citation attached to what comes out.

## Key Concepts

**Interrupts and the maker-checker pattern.** `interrupt(message)` pauses a running graph at exactly that point and returns control to the caller; `Command(resume=value)` continues that same paused run, feeding `value` back in as if the interrupted call had returned it. This is the maker-checker pattern: one step proposes an action (the "maker"), and a human approves or rejects it (the "checker") before anything with real consequences happens. The graph, not a separate script, owns the pause -- that's what makes it resumable exactly where it left off.

**RAG re-engineered as a graph node.** Old L2's RAG was retrieve-then-generate as its own pipeline. Here, `retrieve` is just another LangGraph node: it reads a question, matches it against a small local knowledge source, and returns context plus which source matched. Nothing about the retrieval logic changes -- what changes is that it now lives inside the same graph as everything else, so it can be routed to, checkpointed, and gated by an approval step, exactly like any other node.

**Grounding and citations.** An answer is grounded when the model is instructed to use only the retrieved context, and it's citeable when the response can be traced back to which source produced it. This session's node attaches the matched source keyword to the final answer -- a minimal citation, but the same principle L3's advanced RAG and guardrails sessions build much further: never let an answer stand without a traceable source.

**Why this combination matters for L3.** L3's guardrails and security session assumes you already know how to gate a high-impact action behind human approval; its advanced-RAG and observability sessions assume retrieval is something that happens inside a traceable graph, with a source attached to every answer. This session is the smallest version of both ideas at once, so neither one is new vocabulary when L3 goes deeper.

## Code Walkthrough — `Bridge-Day-04-HITL-RAG-As-Node/example.py`

```python
"""Bridge Session 4: pause for human approval before an
agent action, then retrieve local context and ground the
model's answer in it."""

import sys

import ollama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

sys.stdout.reconfigure(encoding="utf-8")

MODEL = "gpt-oss:120b-cloud"
ARTICLES = {
    "password": "Reset a password at portal.example/reset.",
    "vpn": "For VPN issues, reconnect and enter your company password.",
}


def retrieve(state):
    question = state["question"].lower()
    context, source = "No matching article found.", "none"
    for keyword, article in ARTICLES.items():
        if keyword in question:
            context, source = article, keyword
    return {"question": state["question"], "context": context, "source": source}


def ask_for_approval(state):
    approved = interrupt(f"Send this to the model? Source: [{state['source']}] (yes/no)")
    return {
        "question": state["question"],
        "context": state["context"],
        "source": state["source"],
        "approved": approved,
    }


def answer_with_citation(state):
    if not state["approved"]:
        return {"answer": "Cancelled -- no approved context to answer from."}
    prompt = f"Use only this context: {state['context']}\nQuestion: {state['question']}"
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return {"answer": f"{response['message']['content']} [source: {state['source']}]"}


graph_builder = StateGraph(dict)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("approval", ask_for_approval)
graph_builder.add_node("answer", answer_with_citation)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "approval")
graph_builder.add_edge("approval", "answer")
graph_builder.add_edge("answer", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

settings = {"configurable": {"thread_id": "rag-approval-1"}}
graph.invoke({"question": "How do I reset my password?"}, config=settings)
answer = input("Approve sending the retrieved context to the model? (yes/no): ")
result = graph.invoke(Command(resume=answer.lower() == "yes"), config=settings)
print(result["answer"])

```

1. `retrieve` matches the question against a tiny local `ARTICLES` dictionary and returns `context` plus which `source` matched -- re-threading `question` forward, following the carry-forward rule from Bridge 2.
2. `ask_for_approval` calls `interrupt(...)`, which pauses the graph and surfaces the message to whoever is running it.
3. The first `graph.invoke(...)` call runs up to and including the interrupt, then returns with the run paused.
4. `input(...)` collects a real yes/no answer from the person running the file.
5. The second `graph.invoke(Command(resume=...), ...)` resumes the *same* paused run, feeding the approval back in as `ask_for_approval`'s return value.
6. `answer_with_citation` only calls the model if `approved` is true, and always attaches `[source: ...]` to whatever it returns.

## Hands-On Lab (~30 minutes)

**Goal:** pause a graph for approval, then resume it into a cited, grounded answer.

**Graph to draw:** `START -> retrieve -> approval (interrupt) -> answer -> END`

This lab needs **Ollama running locally** with the `gpt-oss:120b-cloud` model available, since this file makes a real call to it.

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-04-HITL-RAG-As-Node\example.py
```

**Walkthrough steps:**

1. Find `ARTICLES` and the `retrieve` node that searches it.
2. Find `interrupt(...)` inside `ask_for_approval`.
3. Find `Command(resume=...)` and see how it re-invokes the same thread.
4. Run the file, answer `no` at the prompt, and read the cancelled message.
5. Run it again, answer `yes`, and read the cited answer.

**Control question:** What happens if you deny approval? The graph still finishes cleanly -- answer_with_citation returns a cancellation message instead of calling the model at all.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the `ARTICLES` dictionary near the top of `example.py`.
2. Predict what happens for a question that matches neither keyword.
3. Run the example from the repository root and answer `yes`.
4. Add one new keyword/article pair to `ARTICLES`.
5. Run it again with a question that matches your new entry.
6. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.
- Use the Windows Command Prompt commands shown above.
- This lab needs Ollama running locally with gpt-oss:120b-cloud available.

## Before You Move to Bridge 5

- [ ] The file runs without errors (Ollama is running locally with gpt-oss:120b-cloud available).
- [ ] You can name all three nodes and explain what pauses the graph.
- [ ] You ran it once denying approval and once approving it, and can explain both outcomes.
- [ ] You added one new article and confirmed retrieval finds it.
- [ ] You can explain, in one sentence, what a citation is doing in the final answer.
