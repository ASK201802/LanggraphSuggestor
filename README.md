# LangGraph Suggestor

A human-in-the-loop suggestion generator built with [LangGraph](https://langchain-ai.github.io/langgraph/) and OpenAI's `gpt-4o-mini`.

Given a topic, the graph:
1. **Generates** a concise summary (`query_node`).
2. **Validates** the summary with an LLM critic (`validate_node`).
3. **Pauses** for human review via a LangGraph `interrupt` (`approval_node`).
4. On **Edit**, refines the suggestion using the user's feedback (`refine_node`) and re-validates — up to **3 revision cycles**.

## Project Structure

```
langgraphsuggestor/
├── graph_generator/
│   ├── graph_generator.py    # Builds the StateGraph and wires nodes/edges
│   └── node_descriptor.py    # query / validate / approve / refine nodes
├── models/
│   └── suggestor_models.py   # SuggestorState TypedDict
├── main.py                   # CLI entry point
├── pyproject.toml
└── .env                      # OPENAI_API_KEY (not committed)
```

## Setup

Requires Python `>=3.11`. This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

```powershell
uv sync
```

Create a `.env` file at the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

## Run

```powershell
uv run python main.py
```

You will be prompted for:
- **Topic** — what to summarize.
- **Approve / Reject / Edit** — decide the fate of each generated suggestion.
- **Feedback** (on Edit) — text the refiner uses to improve the next suggestion.

The graph exits when the suggestion is approved, rejected, or the 3-revision limit is reached.

## State

```python
class SuggestorState(TypedDict):
    query: str
    suggestion: str
    feedback: str
    approved: bool
    revision_count: int
```

## Graph Flow

```
query_node → validate_node → approval_node ──► END (approved / max revisions)
                     ▲                │
                     └── refine_node ◄┘ (on Edit, up to 3x)
```

## Tech Stack

- `langgraph` — state machine + interrupts + checkpointing (`MemorySaver`)
- `langchain-openai` — `ChatOpenAI` wrapper
- `python-dotenv` — loads `OPENAI_API_KEY`
