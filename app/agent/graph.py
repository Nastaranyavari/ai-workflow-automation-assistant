import json
import sqlite3

from typing import TypedDict
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.tools.calculator import calculate
from app.tools.pdf_tool import read_pdf
from app.tools.database_tool import save_record
from app.tools.database_tool import search_records

from app.services.n8n_service import notify_n8n
from app.services.openrouter_provider import OpenRouterProvider



# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------


client = OpenRouterProvider()


# ---------------------------------------------------------
# State
# ---------------------------------------------------------

class AgentState(TypedDict):
    messages: list
    file_path: str | None
    status: str
    session_id: str
    task: str | None
    record_id: int | None
    n8n_result: dict | None


# ---------------------------------------------------------
# Tools
# ---------------------------------------------------------

TOOLS = {
    "calculate": calculate,
    "read_pdf": read_pdf,
    "save_record": save_record,
    "search_records": search_records,
}


# ---------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                    },
                    "b": {
                        "type": "number",
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                        ],
                    },
                },
                "required": [
                    "a",
                    "b",
                    "operation",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_pdf",
            "description": "Read a PDF file and return its extracted text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path of the PDF file.",
                    }
                },
                "required": [
                    "file_path",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_record",
            "description": "Save a title and content into the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the record.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to save.",
                    },
                },
                "required": [
                    "title",
                    "content",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_records",
            "description": "Search records in the database by keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": (
                            "Keyword to search in record titles and contents."
                        ),
                    }
                },
                "required": [
                    "keyword",
                ],
            },
        },
    },
]

# ---------------------------------------------------------
# Agent Node
# ---------------------------------------------------------

def agent_node(state: AgentState):

    messages = list(state["messages"])

    if state.get("file_path"):
        messages.append(
            {
                "role": "user",
                "content": (
                    f"A PDF file is available at: {state['file_path']}. "
                    "The user wants you to process this PDF. "
                    "Use the read_pdf tool to read the file before answering."
                ),
            }
        )


    response = client.chat(
        messages=messages,
        tools=TOOL_DEFINITIONS,
    )

    assistant_message = response.choices[0].message

    message = {
        "role": "assistant",
        "content": assistant_message.content,
    }

    if assistant_message.tool_calls:
        message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in assistant_message.tool_calls
        ]

    return {
        "messages": messages + [message],
        "file_path": state.get("file_path"),
        "status": "running",
        "session_id": state["session_id"],
        "task": state.get("task"),
        "record_id": state.get("record_id"),
        "n8n_result": state.get("n8n_result"),
    }
# ---------------------------------------------------------
# Decide whether Agent needs a Tool
# ---------------------------------------------------------

def should_use_tool(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.get("tool_calls"):
        return "tool"

    return "end"


# ---------------------------------------------------------
# Tool Execution Node
# ---------------------------------------------------------

def tool_node(state: AgentState):
    last_message = state["messages"][-1]

    if not last_message.get("tool_calls"):
        raise ValueError("No supported tool call found.")

    tool_messages = []
    record_id = state.get("record_id")
    current_task = state.get("task")

    for tool_call in last_message["tool_calls"]:

        tool_name = tool_call["function"]["name"]

        tool_args = json.loads(
            tool_call["function"]["arguments"]
        )

        if tool_name == "read_pdf":
            file_path = state.get("file_path")

            if not file_path:
                raise ValueError("No PDF file was provided.")

            tool_args["file_path"] = file_path

        if tool_name not in TOOLS:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        result = TOOLS[tool_name](**tool_args)

        if tool_name == "save_record":
            if isinstance(result, dict):
                record_id = result.get("record_id")

        if tool_name == "read_pdf":
            current_task = (
                current_task or "document_processing"
            )

        elif tool_name == "save_record":
            current_task = "summarize_and_save"

        elif tool_name == "search_records":
            current_task = "search_database"

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": str(result),
            }
        )

    return {
        "messages": state["messages"] + tool_messages,
        "file_path": state.get("file_path"),
        "status": "running",
        "session_id": state["session_id"],
        "task": current_task,
        "record_id": record_id,
        "n8n_result": state.get("n8n_result"),
    }

# ---------------------------------------------------------
# Finish Node
# ---------------------------------------------------------

def finish_node(state: AgentState):

   notify_result = notify_n8n(
        session_id=state["session_id"],
        task=state.get("task", "unknown"),
        status="completed",
        record_id=state.get("record_id"),
    )

   return {
        "messages": state["messages"],
        "file_path": state.get("file_path"),
        "status": "completed",
        "session_id": state["session_id"],
        "task": state.get("task"),
        "record_id": state.get("record_id"),
        "n8n_result": notify_result,
    }


# ---------------------------------------------------------
# Build Graph
# ---------------------------------------------------------

graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tool", tool_node)
graph_builder.add_node("finish", finish_node)

graph_builder.add_edge(
    START,
    "agent",
)

graph_builder.add_conditional_edges(
    "agent",
    should_use_tool,
    {
        "tool": "tool",
        "end": "finish",
    },
)

graph_builder.add_edge(
    "tool",
    "agent",
)

graph_builder.add_edge(
    "finish",
    END,
)


# ---------------------------------------------------------
# Persistent Checkpointer
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DB = PROJECT_ROOT / "data" / "checkpoints.db"

CHECKPOINT_DB.parent.mkdir(
    parents=True,
    exist_ok=True,
)

sqlite_connection = __import__("sqlite3").connect(
    CHECKPOINT_DB,
    check_same_thread=False,
)

checkpointer = SqliteSaver(
    sqlite_connection
)

graph = graph_builder.compile(
    checkpointer=checkpointer
)