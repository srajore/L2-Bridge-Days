from typing import TypedDict

from langgraph.graph import START,END,StateGraph

class MyState(TypedDict):
    a: int
    b: int
    c: int


def input(state: MyState):
    state["a"]=10
    state["b"]=20
    return state


def calculate(state: MyState):
    state["c"]=state["a"]+state["b"]
    return state


graph = StateGraph(MyState)
graph.add_node("mynode1", input)
graph.add_node("mynode2", calculate)


graph.add_edge(START, "mynode1")

graph.add_edge("mynode1", "mynode2")

graph.add_edge("mynode2", END)

mygraph = graph.compile()

print(mygraph)


result = mygraph.invoke({"a":0,"b":0,"c":0})

print(result)







