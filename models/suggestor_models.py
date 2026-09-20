from typing import TypedDict


class SuggestorState(TypedDict):
    query: str
    suggestion: str
    feedback: str
    approved: bool
