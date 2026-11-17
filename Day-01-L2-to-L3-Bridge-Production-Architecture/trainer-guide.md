# Day 1 Trainer Guide — L2-to-L3 Bridge: Production Architecture

## Outcome
A learner can read the SupportDesk agent (the L2-style bank support prototype that the whole course hardens) as a service and write its production target: NFRs with numbers, API/service boundary, trust boundaries, stateful architecture, failure domains and a risk register. They prove it with a gap report that goes from 26 gaps (prototype) to 0 (target). The target is the Day 19 architecture, so Day 1 is the first page of the SupportDesk thread.

## Files
- `example.ipynb` — offline gap checker as a guided notebook. Every concept has a plain-language analogy (restaurant opening, airport security, hotel front desk, fuse box). LangGraph with seven check/report nodes, no model, run on a SupportDesk prototype spec and a target spec that uses Day 19's names and `NFR` numbers. Outputs are saved in the file, so learners can read it even before running it.
- `slides.pptx` — 27 slides, built to be read without a trainer. Present it in **Slide Show** mode so the links work: agenda cards and the section tabs (top right) jump to a section, the **Agenda** button (bottom right) returns to the agenda, numbered badges on the map open each concept, and "predict" slides reveal the answer on click (use the "Back" button to return). Every content slide has a "Key idea" line and trainer notes.
- `README.md` — handout (includes the Journey and Concept Corner sections)
- `trainer-guide.md` — this file

## Setup (cmd)
```cmd
uv sync
code Day-01-L2-to-L3-Bridge-Production-Architecture\example.ipynb
```
In VS Code choose the project `.venv` as the kernel (needs the Jupyter extension), then run the cells top to bottom. If `code` is not on the PATH, open the folder in VS Code and double-click the notebook.
No `ollama signin` needed. Do not re-teach L2 (graphs, checkpointer, interrupts); learners did that in L2 Days 1-8 and built an agent with guardrails on L2 Day 20. Introduce the thread: one agent, SupportDesk (`lookup_balance`, `freeze_card`, policy docs P1-P4), grows each day into the Day 19 capstone. See `curriculum/agent-thread.md`.

## 120-Minute Flow
1. 0-15 — Course overview; what "production" means. Ask: "What would page you at 3 a.m. for an agent?" Show the Journey block: yesterday (L2 agent), today (production target), tomorrow (durable state).
2. 15-40 — Teach the production delta with SupportDesk: NFRs, API/service boundary, trust boundaries (including model output -> tool), stateful architecture (store, thread_id owner, retention), failure domains, risk register. Draw the target sketch from the README and tell learners it is the Day 19 architecture: every later day builds one box of it.
3. 40-50 — Concept Corner (concept only): workflow vs agent, "build the runtime or rent it", and how today's vocabulary maps to managed-cloud and Claude terms. Keep it to the table; do not demo any cloud service.
4. 50-60 — Run the notebook Steps 4-5; read the 26 prototype gaps, grouped by prefix; show the bar chart and the target at 0 gaps.
5. 60-65 — Break.
6. 65-85 — Lab steps 2-4 (edit the target spec, predict gap counts, re-run).
7. 85-110 — Assignment work: learners sketch and encode the SupportDesk prototype and target (or their own L2 Day 20 agent).
8. 110-120 — Share-outs and exit check.

## Walkthrough Questions
1. Which section produced the most gaps, and why?
2. Is a missing timeout an NFR gap or a failure-domain gap? (Failure domain; the NFR is the latency target.)
3. Where is the trust boundary between a user and the agent? Between the model and a tool?
4. Why must `thread_id` come from the authenticated session and not from the request body? (Otherwise any user can resume or read another user's thread.)
5. Why is `checkpoint_store = "memory"` a gap?
6. Pick one risk in the register. Which later day closes it? (Prompt injection -> Day 13; model outage -> Day 5; duplicate `freeze_card` -> Day 2; card number in the answer -> Day 13 `redact`.)
7. Concept Corner: is SupportDesk's graph a workflow or an agent? Which parts, if any, let the model choose the next step? (Mostly a workflow; the model only writes the answer. Freedom is added only where it pays off.)
8. Concept Corner: what would you gain, and what would you give up, by renting a hosted agent runtime instead of building the loop yourself? (Faster start vs less control and a new dependency.)

## Common Mistakes
- Writing NFRs as adjectives ("fast", "reliable") instead of numbers.
- Treating model output as trusted because "we wrote the prompt".
- Putting only the happy path in the architecture diagram.
- Editing the check functions instead of the spec.
- Listing a risk with a vague mitigation ("be careful") instead of a mechanism.
- Turning the Concept Corner into a product tour. It is vocabulary only; the lab stays on Ollama + LangGraph.

## Exit Check
Ask each learner to name one NFR, one trust boundary, one failure domain (with its timeout and fallback) and one risk with its mitigation for their own agent.

## What Was and Was Not Live-Verified
- Verified: `example.ipynb` was executed top to bottom with the project environment and finished with no errors. It printed the README output (26 gaps, then 0 gaps), the per-check counts 6/5/3/3/4/5, Experiment 1 = 1 gap, Experiment 2 = 2 gaps, and Experiment 3 = 1 gap, then 0 after the fix. The specs and check functions are the same as the earlier `example.py`; a copy of that file is in `_pre-notebook-backup/`.
- Not tested: opening the notebook interactively in VS Code (kernel picker, the click-to-reveal answers). Do one quick run-through before class.
- Consistency with Day 19: the `nfr` numbers and names (`mcp_timeout_s`, `max_tool_calls`, ...) were copied from `agent.py`'s `NFR` by hand, not checked by code.
- Not verified: the assignment itself (learner-authored specs). The checklist is a teaching checklist, not an audited standard.
- The Concept Corner is conceptual and was written from public product documentation; no cloud service or Claude API was called. Check product names against current vendor docs before delivery, because they change.
- Slides: the deck was rendered to images in PowerPoint and every slide was checked visually; the link targets were checked in the file. Clicking through in a live Slide Show was not tested, so do one quick click-through before class.
- Containers are only mentioned (Podman on Day 16); nothing here builds or runs a container.
