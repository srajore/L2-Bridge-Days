"""Bridge Session 5: estimate token usage per part of a
request, then check it against a simple token budget."""

from langgraph.graph import END, START, StateGraph

BUDGET = 40  # words allowed for this request type -- a stand-in token budget


def count_words(text):
    return len(text.split())


def measure(state):
    counts = {
        "instruction": count_words(state["instruction"]),
        "question": count_words(state["question"]),
        "context": count_words(state["context"]),
    }
    return {"counts": counts, "total": sum(counts.values())}


def check_budget(state):
    over_budget = state["total"] > BUDGET
    verdict = "OVER BUDGET -- trim context or split the request" if over_budget else "within budget"
    return {"counts": state["counts"], "total": state["total"], "verdict": verdict}


graph_builder = StateGraph(dict)
graph_builder.add_node("measure", measure)
graph_builder.add_node("check_budget", check_budget)
graph_builder.add_edge(START, "measure")
graph_builder.add_edge("measure", "check_budget")
graph_builder.add_edge("check_budget", END)
graph = graph_builder.compile()

result = graph.invoke(
    {
        "instruction": "Answer using only the approved context below and cite the source article.",
        "question": "How do I reset my password if I no longer have access to my recovery email?",
        "context": "Reset a password at portal.example/reset. VPN issues: reconnect and re-enter your company password.",
    }
)
print("Word estimate by part:", result["counts"])
print("Total word estimate:", result["total"], "/ budget", BUDGET)
print("Verdict:", result["verdict"])
