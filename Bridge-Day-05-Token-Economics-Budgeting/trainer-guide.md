# Bridge 5 Trainer Guide — Token Taxonomy, Economics & Budgeting

## Outcome

By the end of the session, a learner can measure the parts of a request, sum them into a total, and check that total against a budget.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-05-Token-Economics-Budgeting\example.py
```

This example is deterministic and does not need a live model call.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Have learners manually add up the word counts before running the file -- the arithmetic is trivial, but doing it by hand is what makes the budget concept concrete.
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

- Treating word count as if it were an exact token count -- it's a deliberate proxy, not the real thing.
- Forgetting to re-thread counts/total through check_budget.
- Running the command from the wrong folder.
- Assuming an over-budget verdict is an error rather than a signal to act on.
- Changing more than one input value at a time in the assignment.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge 6.
