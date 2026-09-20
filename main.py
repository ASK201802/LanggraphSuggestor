from graph_generator.graph_generator import create_graph
from langgraph.types import Command
import json


def main():
    print("Hello from langgraphsuggestor!")
    graph = create_graph()
    config = {"configurable": {"thread_id": "suggest_session_01"}}
    topic = input("Enter your topic:")
    initial_suggestion_input = {
        "query": topic,
        "suggestion": "",
        "feedback": "",
        "approved": False,
    }
    for chunk in graph.stream(initial_suggestion_input, config=config):
        print(json.dumps(chunk, indent=2, default=str))
    snapshot = graph.get_state(config=config)
    pending_interrupt = snapshot.tasks[0].interrupts[0]
    feedback_value = pending_interrupt.value["feedback"]
    print("feedback value::::", feedback_value)
    user_input = input("Approve/Reject/Edit the feedback above:")
    print("User input::::", user_input)

    if user_input== "Approve":
          resume_command = Command(resume={"action": "Approve"})
    elif user_input== "Reject":
          resume_command = Command(resume={"action": "Reject"})
    else:
          user_feedback = input(f"Enter Your Feedback on the Topic {initial_suggestion_input['query']}:")
          resume_command = Command(resume={"action": "Edit","feedback": user_feedback})
    
    for chunk in graph.stream(resume_command,config=config):
        print(json.dumps(chunk, indent=2, default=str))


if __name__ == "__main__":
    main()
