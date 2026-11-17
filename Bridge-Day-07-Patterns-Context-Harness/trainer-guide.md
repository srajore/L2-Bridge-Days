# Bridge 7 Trainer Guide — Agentic Patterns, Context Engineering & Harness Preview

## Outcome

By the end of the session, a learner can trace a bounded router-plus-verify loop, explain why the retry limit exists, and connect this session's three ideas to their corresponding full L3 sessions.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-07-Patterns-Context-Harness\example.py
```

This example is deterministic and does not need a live model call.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Close by mapping each of this session's three ideas to its L3 counterpart by name (agentic patterns, context engineering, harness engineering) -- this is the last bridge session before L3 begins.
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

- Assuming the retry loop could run forever without MAX_ATTEMPTS -- make the bound explicit and testable.
- Confusing the router pattern with the earlier conditional-edge routing from Bridge 2 -- point out they're the same mechanism, applied differently.
- Running the command from the wrong folder.
- Treating this session as the end of the bridge rather than the handoff into L3 Session 1.
- Skipping the discussion of context engineering because the code doesn't have a dedicated node for it.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge (L3 Session 1).
