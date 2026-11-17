"""Bridge Session 7: a router pattern chooses a specialist,
then a bounded act-and-verify loop (the harness idea) checks
the result before finishing."""

from langgraph.graph import END, START, StateGraph

MAX_ATTEMPTS = 3  # harness-style bounded loop -- never spin forever


def router(state):
    route = "network" if "vpn" in state["request"].lower() else "account"
    return {"request": state["request"], "route": route, "attempt": state.get("attempt", 0)}


def select_specialist(state):
    return state["route"]


def network_specialist(state):
    attempt = state["attempt"] + 1
    draft = "VPN." if attempt < 2 else "Reconnect the VPN client, then sign in again."
    return {"request": state["request"], "route": state["route"], "attempt": attempt, "draft": draft}


def account_specialist(state):
    attempt = state["attempt"] + 1
    draft = "Reset." if attempt < 2 else "Reset the account password from the portal."
    return {"request": state["request"], "route": state["route"], "attempt": attempt, "draft": draft}


def verify(state):
    passed = len(state["draft"].split()) >= 3  # simple, deterministic check
    return {
        "request": state["request"],
        "route": state["route"],
        "attempt": state["attempt"],
        "draft": state["draft"],
        "passed": passed,
    }


def choose_next_step(state):
    if state["passed"] or state["attempt"] >= MAX_ATTEMPTS:
        return "done"
    return "retry"


graph_builder = StateGraph(dict)
graph_builder.add_node("router", router)
graph_builder.add_node("network", network_specialist)
graph_builder.add_node("account", account_specialist)
graph_builder.add_node("verify", verify)
graph_builder.add_edge(START, "router")
graph_builder.add_conditional_edges("router", select_specialist, {"network": "network", "account": "account"})
graph_builder.add_edge("network", "verify")
graph_builder.add_edge("account", "verify")
graph_builder.add_conditional_edges("verify", choose_next_step, {"retry": "router", "done": END})
graph = graph_builder.compile()

result = graph.invoke({"request": "My VPN is disconnected"})
print("Route used:", result["route"])
print("Attempts:", result["attempt"])
print("Final draft:", result["draft"], "-- passed:", result["passed"])
