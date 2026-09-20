from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage, SystemMessage
from models.suggestor_models import SuggestorState
from langgraph.types import interrupt
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


def query_node(suggestion_state: SuggestorState) -> SuggestorState:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "You are an expert concise summarizer"
            ),
            HumanMessagePromptTemplate.from_template("Generate a summary for  {topic}"),
        ]
    )
    message = prompt.format_messages(topic=suggestion_state["query"])
    response = llm.invoke(message)
    suggestion_state["suggestion"] = response.content
    return suggestion_state


def validate_node(suggestion_state: SuggestorState) -> SuggestorState:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "You are an expert validator of suggestions"
            ),
            HumanMessagePromptTemplate.from_template(
                "Validate the following suggestion: {suggestion}"
            ),
        ]
    )
    message = prompt.format_messages(suggestion=suggestion_state)
    response = llm.invoke(message)
    suggestion_state["feedback"] = response.content
    return suggestion_state


def approve_node(suggestion_state: SuggestorState) -> SuggestorState:
    print(f"The following suggestion is ")
    human_review = interrupt(
        {
            "message": "Please review,edit and approve the suggestion",
            "suggestion": suggestion_state["suggestion"],
            "feedback": suggestion_state["feedback"],
        }
    )
    action = human_review["action"]
    if action == "Approve":
        suggestion_state["approved"] = True
    elif action == "Reject":
        suggestion_state["approved"] = False
        suggestion_state["feedback"]=""
    elif action == "Edit":
        suggestion_state["feedback"] = human_review["feedback"]
        suggestion_state["approved"] = False
    else:
        raise ValueError(f"Invalid action: {action}")
    return suggestion_state

def refine_node(suggestion_state: SuggestorState) -> SuggestorState:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                 "You are an expert summarizer. Improve the previous summary using the reviewer feedback."
            ),
            HumanMessagePromptTemplate.from_template(
                "Topic: {topic}\n\nPrevious suggestion:\n{suggestion}\n\nReviewer feedback:\n{feedback}\n\nReturn only the improved summary."
            ),
        ]
    )
    message = prompt.format_messages(
        topic=suggestion_state["query"],
        suggestion=suggestion_state["suggestion"],
        feedback=suggestion_state["feedback"]
    )
    response = llm.invoke(message)
    suggestion_state["suggestion"] = response.content
    suggestion_state["revision_count"] += 1
    return suggestion_state    
