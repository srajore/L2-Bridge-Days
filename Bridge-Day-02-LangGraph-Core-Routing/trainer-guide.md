# Bridge 2 Trainer Guide — LangGraph Core Mechanics: State, Nodes, Edges & Routing

## Outcome

By the end of the session, a learner can add a conditional edge, predict which branch a given input takes, and explain the plain-dict carry-forward rule in their own words.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-02-LangGraph-Core-Routing\example.py
```

This example is deterministic and does not need a live model call.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Explain conditional edges and the state carry-forward gotcha before touching the code -- both are easy to demonstrate live by removing the re-threaded `request` field and showing the resulting KeyError.
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

- Forgetting to re-thread a field a later node still needs, then being confused by a KeyError.
- Assuming the routing function itself changes state -- it only returns a label.
- Running the command from the wrong folder.
- Changing the graph and the input at the same time.
- Confusing a rule-based route with a model decision.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge 3.
