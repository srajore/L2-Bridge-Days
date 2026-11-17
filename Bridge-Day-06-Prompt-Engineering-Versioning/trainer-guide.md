# Bridge 6 Trainer Guide — Prompt Engineering, Contracts & Versioning

## Outcome

By the end of the session, a learner can select a named prompt version, render it, and explain how that maps onto versioning, promotion, and rollback for code.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-06-Prompt-Engineering-Versioning\example.py
```

This example calls ollama.chat with the fixed model gpt-oss:120b-cloud. Keep that model name unchanged. Ollama must be running locally.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Run both v1 and v2 live back to back on the same request -- the contrast is the whole lesson.
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

- Treating the two prompt versions as interchangeable rather than deliberately different.
- Forgetting Ollama needs to be running locally before this session.
- Running the command from the wrong folder.
- Changing the request text and the version at the same time during the lab.
- Assuming the PROMPTS dictionary is a real registry -- it's the smallest possible stand-in for one.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge 7.
