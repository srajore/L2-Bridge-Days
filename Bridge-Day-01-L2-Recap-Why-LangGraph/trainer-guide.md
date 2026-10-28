# Bridge 1 Trainer Guide — L2 Recap & Why LangGraph

## Outcome

By the end of the session, a learner can run one file and explain, in their own words, how old L2's function chains map onto a LangGraph StateGraph.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-01-L2-Recap-Why-LangGraph\example.py
```

This example is deterministic and does not need a live model call. It still teaches the core LangGraph building block, contrasted directly with last year's style.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Explain what changed between old L2 and new L2/L3, and why LangGraph is the foundation for everything that follows in this bridge.
3. **30 minutes — Read:** Walk through `example.py` from top to bottom.
4. **25 minutes — Run:** Execute the file in Windows Command Prompt and trace the state.
5. **20 minutes — Change:** Let learners change one sample input near the bottom of the file.
6. **10 minutes — Explain:** Ask learners to describe the input, nodes, route, and output.

## Code Walkthrough Questions

1. What value enters the graph?
2. What does each node return — and what does it re-thread forward?
3. Is the next step fixed, rule-based, or model-selected?
4. What value is printed at the end?
5. What one safe input change can we try?

## Common Mistakes

- Assuming old L2 knowledge (GenAI basics, embeddings, RAG) is being discarded -- it isn't; only the orchestration layer changes.
- Running the command from the wrong folder.
- Reading every line at once instead of following the graph order.
- Confusing `old_l2_style` (plain function) with the graph version.
- Adding framework helpers that are not used in `example.py`.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge 2.
