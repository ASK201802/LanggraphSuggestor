from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph_generator.node_descriptor import query_node, validate_node, approve_node
from models.suggestor_models import SuggestorState


def create_graph():
    graph = StateGraph(SuggestorState)
    graph.add_node("query_node", query_node)
    graph.add_node("validate_node", validate_node)
    graph.add_node("approval_node", approve_node)

    graph.set_entry_point("query_node")
    graph.add_edge("query_node", "validate_node")
    graph.add_edge("validate_node", "approval_node")
    graph.add_edge("approval_node", END)

    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)
