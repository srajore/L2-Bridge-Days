# Day 5 Trainer Guide - Production Agent Reliability

## Audience note
Mixed room: technical and non-technical. Teach the **idea and the analogy first**, then run the tiny demo. Never open with code. Technical notes in the notebooks are optional reading; do not present them unless someone asks.

## Outcome
Everyone can say, in plain words, how SupportDesk survives a failing tool: it hangs up after a while, retries politely a few times, ends every failure in Plan B or a human handoff, protects the tool from crowds, and rehearses failures. Technical learners can also change the settings and predict the result.

## What went wrong in L2 (say this early, 5 minutes)
In L2 the agent called its tool and hoped. If the tool froze, the customer froze. The L2 retry loop (Day 13) stopped after a few tries, which was good, but it retried instantly, had a single stop rule, and a failure often ended the run or let the model make something up. Today is the "make it production-safe" layer on top. Do not re-teach the L2 loop.

## The SupportDesk thread
Today wraps `lookup_balance` in the bounds Day 19 `agent.py::run_tool` uses: `MCP_ATTEMPTS = 2`, a timeout (`MCP_TIMEOUT_S`), the `fallback` flag and "Service busy, please try again later.". The one difference to mention only if asked: here the retry cycle is drawn as graph boxes so you can see it; Day 19 folds it into a loop inside `run_tool`. Trace lines use the Day 4 format. The pretend card company is replaced by the real MCP server in Days 6-8.

## Files
- `slides.pptx` - interactive deck (section tabs, Agenda button, predict/reveal). Use Slide Show mode so links work.
- `01-timeout.ipynb`, `02-retry-backoff-jitter.ipynb`, `03-fallback-and-escape-path.ipynb`, `04-rate-limit-and-backpressure.ipynb`, `05-fire-drill.ipynb` - one concept each, ~10-20 min
- `README.md` - handout (includes the Concept Corner)
- Quiz: `quizzes/Day-05-quiz.csv`

## Setup (cmd)
```cmd
uv sync
code Day-05-Production-Agent-Reliability
```
Choose the project's `.venv` as the notebook kernel (Jupyter extension). Every notebook begins with a "connect to the AI model" cell using Ollama (`gpt-oss:120b-cloud`). If it prints "not reachable", run `ollama signin` in a terminal and restart the notebook. Check this with the whole room in the first 5 minutes. Each notebook runs in about 10 seconds because some steps pause on purpose.

## 120-Minute Flow
| Minutes | What | How |
| --- | --- | --- |
| 0-10 | Journey slide, L2 problem | Ask: "What would you do if the tool freezes?" Collect answers, then show the L2 vs L3 slide. |
| 10-25 | Concept 1: Timeout | Slide, analogy (the silent phone line), then `01-timeout.ipynb`. Do the "5 seconds" prediction. |
| 25-45 | Concept 2: Retry | Slide with the loop diagram, then `02-retry-backoff-jitter.ipynb`. Stress jitter (5 customers) and the seat belt. |
| 45-60 | Concept 3: Plan B and handoff | Temporary vs permanent table, then `03-fallback-and-escape-path.ipynb`. |
| 60-75 | Concept 4: Crowds | Turnstile vs full club, then `04-rate-limit-and-backpressure.ipynb`. |
| 75-80 | Break | |
| 80-100 | Concept 5: Fire drills | `05-fire-drill.ipynb`: predict each ending, then run. |
| 100-110 | Assignment | Two new failure scenarios; one sentence each. |
| 110-115 | Concept Corner | Managed cloud and Claude names for the same ideas (concept only). |
| 115-120 | Exit check | Quiz slide: answer out loud first. |

## Walkthrough Questions (ask in plain words)
1. If the card company is silent, how long should a customer wait, and who decides?
2. Why is "retry forever" dangerous for the tool? What does the random extra wait (jitter) fix?
3. Why does the wrong id `123` skip the retries? Who chooses the exit, code or the model?
4. Turnstile versus full club: which makes people wait, which turns them away, when do you want each?
5. Why must a fallback be visible (a flag and a different answer) and not silently reuse old data?
6. Concept Corner: which Claude API errors are temporary (retry with a wait), and which kind should never be retried?
7. Concept Corner: what is the managed cousin of our escape path?

## Common Mistakes
- Retrying actions that must happen only once, such as a payment (link to Day 2, idempotency).
- Retrying permanent errors such as bad input: wastes the budget. The notebook shows `flaky` with id `123` using 1 try, not 2.
- Believing the call is cancelled on timeout: the slow call finishes in the background; real systems also set the timeout in the network client.
- Backpressure demo output: which customers get seats can differ per run because they arrive at the same instant. The *count* (3 served, 3 turned away) is stable.
- Treating `recursion_limit` as the retry policy; it is a seat belt, not a design.

## Verified status
All five notebooks were executed end to end with a stand-in for the Ollama model (the model-written sentence is the only part that was not exercised against real Ollama). Run them once with real Ollama before class.
