"""Bridge Session 3: a tool node backed by a plain function,
plus checkpointed memory resumed with the same thread ID."""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class SupportState(TypedDict, total=False):
    customer_id: str
    ticket_count: int
    question: str


def look_up_ticket_count(customer_id):
    """Plain Python function used as a tool -- no ToolNode, no decorator."""
    tickets = {"C100": 2, "C200": 0}
    return tickets.get(customer_id, 0)


def use_tool(state):
    if state.get("customer_id"):
        return {"ticket_count": look_up_ticket_count(state["customer_id"])}
    return {}


graph_builder = StateGraph(SupportState)
graph_builder.add_node("use_tool", use_tool)
graph_builder.add_edge(START, "use_tool")
graph_builder.add_edge("use_tool", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

settings = {"configurable": {"thread_id": "customer-C100"}}
first = graph.invoke({"customer_id": "C100"}, config=settings)
print("First run - ticket count:", first["ticket_count"])

second = graph.invoke({"question": "How many open tickets do I have?"}, config=settings)
print("Second run (no customer_id given) - remembered ticket count:", second["ticket_count"])
