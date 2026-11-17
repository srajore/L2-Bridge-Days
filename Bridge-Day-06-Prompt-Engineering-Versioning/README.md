# Bridge 6 — Prompt Engineering, Contracts & Versioning

## What You'll Learn Today

- Name the parts of a well-formed prompt: role, objective, constraints, context instructions, output contract.
- Render a prompt template by filling in a runtime variable.
- Select between two named versions of a prompt (v1 and v2) before calling the model.
- Explain what promotion and rollback mean for a prompt, the same way they do for code.
- Explain why a stable prompt identifier and a version label are two different things.
- Predict which version produces the better answer, before running the file.

## Why This Matters

Old L2 wrote prompts as short strings sitting right next to the model call -- fine for a first attempt, but impossible to compare or improve once behavior starts to matter. This session treats a prompt as something worth managing on its own: named, versioned, tested, and switchable, the same way you'd manage a piece of code. This is also the foundation L3's PromptOps session builds on directly -- a prompt registry, approvals, and dev/test/prod promotion are all bigger versions of the one idea this session introduces: pick a named version before you call the model, and know exactly which one ran.

## Key Concepts

**The parts of a prompt.** The role names the assistant's function and constrains what it's allowed to talk about. The objective describes one measurable outcome, not a vague goal. Constraints rule out bad behavior directly -- don't invent facts, abstain when there's no approved context. Context instructions tell the model how to use whatever context and source ID it's given. An output contract defines a machine-checkable format for the answer. This session's two versions don't go that far -- `v2` adds two plain constraints (one short sentence, don't guess) -- but a stricter version could add a real output contract on top.

**Templates and runtime variables.** A prompt template has runtime variables -- here, the `request` text -- filled in when the template is rendered. Rendering is purely a text-assembly step, inspectable before anything is sent; it does not call the model by itself. Validating that a template contains exactly the variables you expect catches wiring mistakes early, before a real test case ever runs against it.

**Naming, versions, and evidence.** A stable identifier (like `service-resolution`) names what a prompt is *for*; separate version labels (`v1`, `v2`, ...) describe specific revisions of its wording -- the identifier stays the same even as the content changes. A registry mapping versions to their content, and a changelog recording what actually changed in behavior, make both the current choice and its history visible. This session's `PROMPTS` dictionary is the simplest possible registry, and the `version` value passed into the graph is the only record of which one ran.

**Promotion, testing, and rollback.** In a fuller setup, you'd freeze a fixed set of test requests, run them against both versions, check each with a deterministic rule, and only then promote a version to active. Rollback matters just as much as promotion -- being able to switch back to a previously retained version without deleting the newer one, when something needs to be re-checked. This session doesn't build that test harness; it shows the smallest piece those systems rely on: picking a named version before the model is ever called, which is what makes switching between versions possible at all.

## Code Walkthrough — `Bridge-Day-06-Prompt-Engineering-Versioning/example.py`

```python
"""Bridge Session 6: select a named, versioned prompt
template before calling the model -- the same idea as
versioning code."""

import sys

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")

MODEL = "gpt-oss:120b-cloud"
PROMPTS = {
    "v1": "Answer the support request.",
    "v2": "Answer the support request in one short sentence. "
          "If the approved context does not cover it, say so instead of guessing.",
}


def render_prompt(state):
    instruction = PROMPTS[state["version"]]
    return {"prompt": f"{instruction}\nRequest: {state['request']}"}


def ask_model(state):
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": state["prompt"]}])
    return {"answer": response["message"]["content"]}


graph_builder = StateGraph(dict)
graph_builder.add_node("render_prompt", render_prompt)
graph_builder.add_node("ask_model", ask_model)
graph_builder.add_edge(START, "render_prompt")
graph_builder.add_edge("render_prompt", "ask_model")
graph_builder.add_edge("ask_model", END)
graph = graph_builder.compile()

result = graph.invoke({"version": "v2", "request": "The VPN keeps disconnecting every few minutes."})
print("Prompt version:", "v2")
print(result["answer"])

```

1. `MODEL` is fixed to `"gpt-oss:120b-cloud"` -- keep this unchanged.
2. `PROMPTS` is the registry: a small dictionary holding both named versions.
3. `render_prompt` looks up the instruction for whichever `version` was requested, and renders it together with the actual `request` text into one `prompt` string.
4. `ask_model` sends that rendered `prompt` to `ollama.chat` and returns the model's `answer`.
5. The graph wires `START -> render_prompt -> ask_model -> END` -- the prompt is always fully assembled before the model is called.
6. The script runs the graph with `version: "v2"` and prints which version was used alongside the model's answer.

## Hands-On Lab (~30 minutes)

**Goal:** select a prompt version before calling the model, and compare the two versions.

**Graph to draw:** `START -> render_prompt -> ask_model -> END`

This lab needs **Ollama running locally** with the `gpt-oss:120b-cloud` model available, since this file makes a real call to it.

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Bridge-Day-06-Prompt-Engineering-Versioning\example.py
```

**Walkthrough steps:**

1. Read `PROMPTS` and compare what `v1` and `v2` each instruct.
2. Find `render_prompt` and see how it selects and fills the template.
3. Predict how `v1`'s answer might differ from `v2`'s before running either.
4. Run the file with `version` set to `"v1"`, then again with `"v2"`, using the same request.
5. Compare the two answers side by side.

**Control question:** The graph selects an approved prompt version -- the choice is explicit in the state, not hidden inside the model call.

## Assignment

**Goal:** Make one small change to example.py and explain how the result changes.

**Steps:**

1. Read the sample `version` and `request` near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run it from the repository root.
4. Change only the `version` value from `"v2"` to `"v1"`.
5. Predict the new answer's style before running again.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.

## Before You Move to Bridge 7

- [ ] The file runs without errors (Ollama is running locally with gpt-oss:120b-cloud available).
- [ ] You can name the state, the nodes, and the edges in this graph.
- [ ] You can explain which prompt version was actually used, and how you know.
- [ ] You ran both v1 and v2 on the same request and compared the answers.
- [ ] You can explain what promotion and rollback would mean for these two versions.
