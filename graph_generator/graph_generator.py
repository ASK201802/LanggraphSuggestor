from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph_generator.node_descriptor import query_node, validate_node, approve_node,refine_node
from models.suggestor_models import SuggestorState

MAX_REVISION=3
def route_after_approval(state: SuggestorState):
    if state["approved"]:
        return END
    elif state["revision_count"] ==MAX_REVISION:
        return END
    elif not state["feedback"]:
        return END    
    return "refine_node"

def create_graph():
    graph = StateGraph(SuggestorState)
    graph.add_node("query_node", query_node)
    graph.add_node("validate_node", validate_node)
    graph.add_node("approval_node", approve_node)
    graph.add_node("refine_node",refine_node)

    graph.set_entry_point("query_node")
    graph.add_edge("query_node", "validate_node")
    graph.add_edge("validate_node", "approval_node")
    graph.add_conditional_edges("approval_node",route_after_approval,
    {"refine_node":"refine_node",END:END})
    graph.add_edge("refine_node", "validate_node")

    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)
