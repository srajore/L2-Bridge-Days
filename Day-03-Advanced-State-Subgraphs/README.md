# Day 3 — Advanced State and Subgraphs

## What You'll Learn
- Treat typed state as a contract: each key has a type and one owner, and the contract is checked at run time.
- Write a custom reducer (`merge_unique`) as well as the built-in `operator.add`, and know when a write is an update vs a merge.
- Refactor the SupportDesk monolith into a retrieval subgraph and a tool subgraph and prove the behaviour did not change.
- Build reusable graph components (`make_linear_graph`, `call_subgraph`) and orchestrate them with a conditional edge.
- Test each subgraph alone.

## Already Covered in L2 (not repeated)
- Already covered in L2 Day 3: `StateGraph`, `TypedDict` state, nodes, edges.
- Already covered in L2 Day 4: conditional routing with `add_conditional_edges`.
- Already covered in L2 Day 7: state as the data nodes read and write.

Today is only the production delta: contracts, merge rules, ownership, modularity.

## Why This Matters
In a monolith graph (like the first SupportDesk) any node can overwrite any key, so a change in one place silently breaks another, and nobody can say who owns a value. Subgraphs with explicit ownership let teams change one part without breaking another. Reducers decide what happens when two writes meet, which removes silent data loss and duplicates.

## Your Journey
- **Yesterday (Day 2):** one `freeze_card` thread that survives a restart, waits for a human and never freezes twice. The state was a handful of boxes.
- **Today:** the state grows to the full SupportDesk board. We give every box an owner and a merge rule, and split the one big graph into two small subgraphs.
- **Tomorrow (Day 4):** we make the `trace` visible: correlation ids, timing per node and token counts, so you can debug an incident from the trace alone.

## SupportDesk so far
- Before today: SupportDesk with a durable checkpointed thread, an approval interrupt for `freeze_card` and an idempotent write (Day 2).
- Added today: the typed `State` (Day 19's field names) with reducers on `trace` and `context`, ownership checks, and two reusable subgraphs: a retrieval path (`retrieve`, `retrieve_by_topic`) and a tool path (`choose_tool`, `run_tool`), orchestrated by a parent (`example.ipynb`: `State`, `OWNS`, `retrieval_app`, `tool_app`, `parent`).
- Becomes in Day 19: `agent.py::State` (the same `TypedDict`, with `trace: Annotated[list, operator.add]`), the node split `retrieve` / `choose_tool` / `run_tool` and the explicit conditional edges (`after_route`, `after_policy`) in `agent.py::build_agent`. Day 19 keeps one retriever, so its `context` is a plain overwrite key; `merge_unique` is what you add when two nodes write it.

## Key Concepts (production depth only)
**One idea first: a shared value needs an owner and a merge rule.** Everything below serves that idea. *Analogy: a shared whiteboard with a sticker on every box saying who may write there.*

**Typed state contracts.** Each graph has its own `TypedDict`: the parent `State` has the SupportDesk fields (`user, team, question, cid, t0, route, context, tool, result, answer, tokens, blocked, fallback, trace`), `RetrievalState` and `ToolState` have only what their subgraph needs. `TypedDict` is only a hint, so the notebook adds a run-time check, `enforce_contract(owner, update)`: an owner may write only the keys in `OWNS`, and each value must have the type in `TYPES`. A component that writes a foreign key or the wrong type fails loudly (see the last two output lines).

**Reducers and updates.** Without a reducer a node's return value *replaces* the key (an update). With `Annotated[list, reducer]` the returned value is *merged* into the old one. `operator.add` (on `trace`) appends lists; `merge_unique` (on `context`) is a custom reducer that appends but skips items already present. In the run, `retrieve` and `retrieve_by_topic` both find `P1` for the lost-card question, and `context` still holds `['P1']` once. Choose the reducer from the business rule, not by habit. *Analogy: erase and replace, add below, or add only if new.*

**Subgraphs and reusable components.** A subgraph is a compiled graph with its own state class. `make_linear_graph(state_class, nodes)` builds any chain of nodes into a subgraph, so the same factory makes `retrieval_app` and `tool_app`. `call_subgraph(...)` is the one wrapper both use. The standalone run of `tool_app` shows a subgraph can be tested alone. *Analogy: a department with its own small whiteboard.*

**Modular orchestration.** The parent only decides *order and routing*. `after_route_parent` sends policy questions through retrieval first and balance/freeze questions straight to the tool path. In the monolith the same decision is `after_route`. *Analogy: the receptionist.*

**State ownership.** `context` is written only by `retrieval`; `tool` and `result` only by `tool_path`; `answer` only by `write_answer`; every component may append to `trace`. The parent decides what to pass in and what to take out.

**Pitfall to remember.** If a subgraph shares a reducer key with the parent and is added directly as a node, its output includes the parent's old items and the reducer applies them again. The run prints it: a parent `trace` with one earlier line gets 4 lines instead of 3. The wrapper passes in fresh empty reducer keys and returns only the owner's keys. LangGraph also supports other ways (distinct state keys, schema transforms); only the wrapper is used and tested here.

## L2 vs L3 (what changed)
| L2 | L3 |
| --- | --- |
| One flat state, any node writes any key | Per-graph typed state, one owner per key, checked at run time |
| Overwrite on every write | Reducers (built-in and custom) define how writes merge |
| One graph | Parent plus reusable subgraphs, tested alone |
| Refactor by eye | Refactor proven by comparing monolith and subgraph results |

## Concept Corner: the same ideas in other places
*Concept only. Nothing here changes today's lab; it shows that the vocabulary you learn today is shared across the industry.*

**The idea.** When an agent grows, split it into small parts with clear inputs, clear outputs and limited rights. Then each part can be tested, replaced and trusted on its own.

**In a managed cloud.** Hosted agent services let you define *tools with a declared input shape* (a schema), keep *session data* that several steps read and write, and sometimes let one agent *hand work to a collaborator agent*. The same questions appear: who may write the shared session data, what shape must it have, and how do concurrent writes combine?

**In Claude's world.** Every tool you give Claude is described with a **JSON Schema** for its input, which is a typed contract that is checked before the tool runs. The Claude Agent SDK supports **subagents**: a separate agent with its own context, its own instructions and only the tools you allow. That is the same idea as a subgraph with its own state class and ownership table. Giving each subagent only the tools it needs is *least privilege*, the same rule as `OWNS`.

**How we do it locally.** `TypedDict` plus `enforce_contract` is the contract, reducers are the merge rules, and subgraphs built by `make_linear_graph` are the small parts. Same ideas, no cloud account needed.

| Idea | Today's file | Managed / Claude name (concept only) |
| --- | --- | --- |
| Typed state contract | `State`, `TYPES` | tool input schema (JSON Schema) |
| Small part with its own state | subgraph (`retrieval_app`) | subagent with its own context |
| Who may write what | `OWNS`, `enforce_contract` | least-privilege tool permissions |
| How concurrent writes combine | reducers | rules for shared session data |
| Test one part alone | `tool_app.invoke(...)` | evaluating a single agent or tool |

## Code Walkthrough — `Day-03-Advanced-State-Subgraphs/example.ipynb`
The notebook tells the story of **a shared whiteboard in an office** (labelled boxes, a sticker saying who may write, erase/add/add-if-new rules, departments and a receptionist) before each piece of code. Its steps: setup, the document library, reducers and the three state classes, the ownership contract (with a small who-may-write-what grid), the six workers, the monolith, the two subgraphs and the parent, the proof that nothing changed, four predict-then-run experiments, and the assignment.

- `State`, `RetrievalState`, `ToolState` and the reducers (`merge_unique`, `operator.add`).
- `OWNS`, `TYPES`, `enforce_contract`: the ownership and type contract.
- Node functions: `decide_route`, `retrieve`, `retrieve_by_topic`, `choose_tool`, `run_tool`, `write_answer`. They are the *same functions* in the monolith and in the refactored graph. `run_tool` is a local stand-in for the MCP call (built on Days 6-8). Trace lines here are `cid=<id> <node> <detail>`; Day 4 adds the `+<ms>ms` part, which is left out so the two graphs can be compared exactly.
- `make_monolith`: all nodes in one graph with a conditional edge `after_route` (the "before").
- `retrieval_app` and `tool_app`: subgraphs built by `make_linear_graph`; `run_retrieval` / `run_tool_path` / `run_write_answer` are the parent's nodes, all passing through `enforce_contract`.
- `make_parent`: `START -> decide_route -> (policy question?) retrieval -> tool_path -> write_answer -> END`, or `decide_route -> tool_path` for a balance question.
- The notebook runs two standard questions through both graphs and compares the full final state, runs `tool_app` alone, shows the direct-subgraph pitfall, and triggers two contract violations on purpose.

Real output (Step 7):

```text
Question: What happens if my card is lost?
  monolith : ['P1'] none | context=['P1'] result=no tool needed
  subgraphs: ['P1'] none | context=['P1'] result=no tool needed
  trace    : 6 lines; refactor keeps behaviour: True
Question: What is my balance?
  monolith : [] lookup_balance | context=[] result=Balance for cust-1 is 1,250 INR
  subgraphs: [] lookup_balance | context=[] result=Balance for cust-1 is 1,250 INR
  trace    : 4 lines; refactor keeps behaviour: True
Tool subgraph alone: freeze_card
Subgraph added directly, trace lines (3 is correct): 4
Contract violation caught: tool_path may not write 'answer'
Contract violation caught: retrieval wrote 'context' as str
```

## Lab Steps
Open the notebook in VS Code (Jupyter extension), choose the project's `.venv` as the kernel, then run the cells from top to bottom with Shift + Enter.
```cmd
uv sync
code Day-03-Advanced-State-Subgraphs\example.ipynb
```
1. Run Steps 0-7. Verify that the monolith and subgraph lines match for both questions, and that the lost-card question has 6 trace lines (decide_route, 2 retrieval, choose_tool, run_tool, write_answer).
2. Step 8, Experiment 1: make `trace` a plain list. Predict: both graphs keep only 1 line (the last writer wins) and the equality check still says `True`. Equality alone does not prove nothing was lost.
3. Experiment 2: change the `context` rule to `operator.add`. Predict: `context` becomes `['P1', 'P1']`.
4. Experiment 3: make `retrieve_by_topic` return `[]`. Predict: `context` is still `['P1']`.
5. Experiment 4: make `write_answer` write `tool`. Predict the error and its message.
6. Bonus: add a third node to the retrieval subgraph and the monolith, and confirm `write_answer` needs no change.

## Assignment (workbook lab): Refactor a monolithic graph into reusable subgraphs
Take the single-graph SupportDesk agent (six or more nodes; your L2 Day 20 agent also works). Split it into two subgraphs plus a parent, built with a reusable factory like `make_linear_graph`. Deliver: (1) a table listing every state key, its type, its owner, its reducer (or "overwrite") and which graphs read it; (2) a printed run proving the refactor gives the same result as the monolith; (3) one standalone run of each subgraph; (4) one deliberate contract violation that is caught.

## Production Checklist (reuse as release-checklist lines on Day 19)
- Every state key has a type, one named owner and an explicit merge rule (reducer or "overwrite") in a table.
- A run-time contract check rejects a write to a key the component does not own, and a test proves it.
- Subgraphs receive only the input they need and return only what they produced (no old parent items re-merged).
- Each subgraph has a standalone run/test, and a before/after comparison shows the refactor did not change results.
- Routing between components lives in the parent graph as visible edges, not inside a subgraph.
