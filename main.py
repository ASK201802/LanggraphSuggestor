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
        "revision_count":0
    }
    for chunk in graph.stream(initial_suggestion_input, config=config):
        print(json.dumps(chunk, indent=2, default=str))

    while True:    
       snapshot = graph.get_state(config=config)
       if not snapshot.tasks or not snapshot.tasks[0].interrupts:
           break    
       pending_interrupt = snapshot.tasks[0].interrupts[0]
       feedback_value = pending_interrupt.value["feedback"]
       print("feedback value::::", feedback_value)
       user_input = input("Approve/Reject/Edit the feedback above:").lower().strip()
       print("User input::::", user_input)

       if user_input== "approve":
           resume_command = Command(resume={"action": "Approve"})
       elif user_input== "reject":
           resume_command = Command(resume={"action": "Reject"})
       elif user_input== "edit":
           user_feedback = input(f"Enter Your Feedback on the Topic {initial_suggestion_input['query']}:")
           resume_command = Command(resume={"action": "Edit","feedback": user_feedback})
       else:
           print("Invalid input, please try again")
           continue
    
       for chunk in graph.stream(resume_command,config=config):
           print(json.dumps(chunk, indent=2, default=str))


if __name__ == "__main__":
    main()
