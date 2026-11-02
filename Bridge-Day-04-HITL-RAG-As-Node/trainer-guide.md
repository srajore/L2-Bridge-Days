# Bridge 4 Trainer Guide — Human-in-the-Loop & RAG Re-engineered as a Graph Node

## Outcome

By the end of the session, a learner can pause a graph with interrupt(), resume it with Command(resume=...), and explain how that combines with a retrieval node to produce a cited, approved answer.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this session.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Bridge-Day-04-HITL-RAG-As-Node\example.py
```

This example calls ollama.chat with the fixed model gpt-oss:120b-cloud. Keep that model name unchanged. Ollama must be running locally.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Run the denial path live first (fast, no model call needed) before the approval path (which does call the model) -- it makes the branch obvious.
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

- Forgetting Ollama needs to be running locally before this session.
- Assuming interrupt() ends the run -- it only pauses it; Command(resume=...) is required to continue.
- Losing track of which fields must be re-threaded through the approval node.
- Running the command from the wrong folder.
- Treating the citation as optional -- it is the point of the exercise.

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result, and explain in one sentence how this session's concept feeds into Bridge 5.
