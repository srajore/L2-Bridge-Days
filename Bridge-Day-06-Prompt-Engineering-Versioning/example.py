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
