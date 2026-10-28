"""Bridge Session 1: same request, two ways -- a fixed Python
chain (last year's L2 style), then the same steps as a graph."""

from langgraph.graph import END, START, StateGraph


def old_l2_style(request):
    cleaned = request.strip().lower()
    if "reset" in cleaned:
        return "Route to: account help"
    return "Route to: general support"


def clean_request(state):
    return {"request": state["request"].strip().lower()}


def classify_request(state):
    topic = "account" if "reset" in state["request"] else "general"
    return {"topic": topic}


def create_response(state):
    return {"message": f"Route to: {state['topic']} help"}


graph_builder = StateGraph(dict)
graph_builder.add_node("clean", clean_request)
graph_builder.add_node("classify", classify_request)
graph_builder.add_node("respond", create_response)
graph_builder.add_edge(START, "clean")
graph_builder.add_edge("clean", "classify")
graph_builder.add_edge("classify", "respond")
graph_builder.add_edge("respond", END)
graph = graph_builder.compile()

print("Old L2 style:", old_l2_style("Please reset my password"))
result = graph.invoke({"request": "  Please RESET my password  "})
print("LangGraph style:", result["message"])
