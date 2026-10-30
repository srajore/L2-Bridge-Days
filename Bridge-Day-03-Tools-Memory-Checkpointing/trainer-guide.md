# Bridge 3 Trainer Guide — Tool Calling & State Memory / Checkpointing

## Outcome

By the end of the session, a learner can compile a graph with a checkpointer, run it twice on the same thread ID, and explain why the second run remembers the first.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-03-Tools-Memory-Checkpointing\example.py
```

This example is deterministic and does not need a live model call.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Contrast this session's TypedDict state directly against Bridge 2's plain dict -- run both live if time allows, and show the KeyError that a plain dict would produce here.
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

- Assuming a checkpointer is required for state to merge -- it's the TypedDict schema doing that, the checkpointer is what persists it across calls.
- Reusing the same thread ID as another exercise by accident and seeing unexpected state.
- Running the command from the wrong folder.
- Forgetting that a fresh thread ID starts from nothing.
- Adding a real external API call where the lesson only needs a plain local function.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge 4.
