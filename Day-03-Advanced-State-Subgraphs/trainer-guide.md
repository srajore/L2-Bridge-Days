# Day 3 Trainer Guide — Advanced State and Subgraphs

## Outcome
A learner can state a typed contract for the SupportDesk `State` with an owner and a merge rule for every state key, write a custom reducer, refactor a monolith into reusable subgraphs, and prove the refactor kept behaviour.

## Files
- `slides.pptx` — 26 slides, interactive (section tabs, Agenda button, predict/reveal slides). Run it in Slide Show mode so the links work.
- `example.ipynb` — offline notebook told as a shared-whiteboard story: the SupportDesk monolith graph, the same nodes refactored into a retrieval subgraph and a tool subgraph plus a parent, a run-time ownership/type contract, and four predict-then-run experiments
- `README.md`, `trainer-guide.md`
- Quiz: `quizzes/Day-03-quiz.csv`

## Setup (cmd)
```cmd
uv sync
code Day-03-Advanced-State-Subgraphs\example.ipynb
```
In VS Code choose the project's `.venv` as the notebook kernel (Jupyter extension), then run cells with Shift + Enter. No `ollama signin`. Learners know StateGraph, TypedDict state and conditional edges from L2 Days 3-4; skip those basics. Thread: this day gives SupportDesk its typed `State` (Day 19's field names, `trace` reducer) and the node split `retrieve` / `choose_tool` / `run_tool`. Say that Day 19's `context` has no reducer because only one node writes it.

## 120-Minute Flow
1. 0-10 — Journey slide, then show a node accidentally overwriting a key (Experiment 1 live on `trace`).
2. 10-30 — Typed contracts, ownership table, reducers (built-in vs custom `merge_unique`); overwrite vs merge demo.
3. 30-50 — Subgraphs, reusable factory, wrapper that returns only new items; draw the parent and two children.
4. 50-60 — Concept Corner: tool schemas, subagents and least privilege in managed and Claude terms (concept only).
5. 60-75 — Run notebook Steps 4-7; trace the six trace lines of the lost-card question and the equality check.
6. 75-80 — Break.
7. 80-95 — Lab: Step 8 experiments 1-4 (predict first).
8. 95-115 — Assignment: ownership table and refactor of their own agent.
9. 115-120 — Exit check.

## Walkthrough Questions
1. Which keys have reducers (`trace`, `context`) and why those reducers?
2. Who owns `answer`? Who owns `tool`? Who may write it, and what stops anyone else?
3. Why do the wrapper nodes start the subgraph with empty reducer keys and return only the owner's keys?
4. What would a reducer on `answer` mean, and would you want it?
5. What does the "Refactor keeps behaviour" check give you that reading the code does not?
6. Concept Corner: which Claude feature matches a subgraph with its own state and limited rights?
7. Concept Corner: what plays the role of `TYPES` when you define a Claude tool?

## Common Mistakes
- Adding a subgraph directly as a node when it shares a reducer key: old items are appended twice (the notebook prints it: 4 trace lines instead of 3).
- Forgetting the reducer and losing a parallel branch's output.
- Giving subgraphs the whole parent state "to be safe".
- Mutating a list in place instead of returning a new value.
- Assuming `TypedDict` enforces types at run time (it does not; `enforce_contract` does).
- Using `operator.add` when duplicates must not appear (Experiment 2 shows it).
- Trusting the equality check alone (Experiment 1 shows it can be `True` while history is lost).

## Exit Check
"Two nodes both return `context`. What decides whether you get one list or both, and how do you stop a third component from writing `answer`?" (The reducer; the ownership contract.)

## What Was and Was Not Live-Verified
- Verified: `example.ipynb` was executed top to bottom with `nbclient` on Windows with no errors. Step 7 printed exactly the output in the README. Experiment 1 (`trace` as a plain list) gave 1 trace line in both graphs and equality still `True`. Experiment 2 (`operator.add` on `context`) gave `['P1', 'P1']`. Experiment 3 (`retrieve_by_topic` returns `[]`) kept `['P1']`. Experiment 4 raised `PermissionError: write_answer may not write 'tool'`.
- Not verified: opening the notebook in the VS Code UI cell by cell, the slides in a live Slide Show click-through, the bonus (third node in the retrieval subgraph) and the assignment. The experiments subclass `State` to change one reducer; that works in the notebook but is a teaching shortcut. The wrapper-node pattern is one valid way to enforce ownership; LangGraph's other mechanisms (distinct state keys, schema transforms, `input_schema`/`output_schema`) were not tried. `enforce_contract` is a teaching helper inside the notebook, not a LangGraph feature.
- Concept Corner names are generic on purpose (tool input schema, subagent, least privilege). Product names change; check vendor docs before naming a specific service in class.
