"""Bridge Session 4: pause for human approval before an
agent action, then retrieve local context and ground the
model's answer in it."""

import sys
from typing import TypedDict

import ollama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

sys.stdout.reconfigure(encoding="utf-8")

MODEL = "gpt-oss:120b-cloud"
ARTICLES = {
    "password": "Reset a password at portal.example/reset.",
    "vpn": "For VPN issues, reconnect and enter your company password.",
}


class State(TypedDict):
    """The shared state: every node reads from it and writes back to it."""

    # State variables
    question: str  # input: the user's question (set when we invoke the graph)
    context: str  # retrieved: the matching local article, or "No matching article found."
    source: str  # retrieved: the keyword of the matching article, or "none"
    approved: bool  # human decision: True if the human approved sending context to the model
    answer: str  # output: the final reply, with its source citation


def retrieve(state: State):
    question = state["question"].lower()
    context, source = "No matching article found.", "none"
    for keyword, article in ARTICLES.items():
        if keyword in question:
            context, source = article, keyword
    return {"question": state["question"], "context": context, "source": source}


def ask_for_approval(state: State):
    approved = interrupt(f"Send this to the model? Source: [{state['source']}] (yes/no)")
    return {
        "question": state["question"],
        "context": state["context"],
        "source": state["source"],
        "approved": approved,
    }


def answer_with_citation(state: State):
    if not state["approved"]:
        return {"answer": "Cancelled -- no approved context to answer from."}
    prompt = f"Use only this context: {state['context']}\nQuestion: {state['question']}"
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return {"answer": f"{response['message']['content']} [source: {state['source']}]"}


graph_builder = StateGraph(State)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("approval", ask_for_approval)
graph_builder.add_node("answer", answer_with_citation)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "approval")
graph_builder.add_edge("approval", "answer")
graph_builder.add_edge("answer", END)


graph = graph_builder.compile(checkpointer=InMemorySaver())

settings = {"configurable": {"thread_id": "rag-approval-1"}}

graph.invoke({"question": "I am not able to connect to VPN?"}, config=settings)
answer = input("Approve sending the retrieved context to the model? (yes/no): ")
result = graph.invoke(Command(resume=answer.lower() == "yes"), config=settings)
print(result["answer"])
