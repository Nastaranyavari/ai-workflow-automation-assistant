import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.calculator import calculate
from app.tools.pdf_tool import read_pdf
from app.tools.database_tool import search_records


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


TOOLS = {
    "calculate": calculate,
    "read_pdf": read_pdf,
    "search_records": search_records,
}

#-----------------------calculator tool--------------------------------
calculator_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="calculate",
            description="Perform a mathematical calculation.",
            parameters={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number.",
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number.",
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                        ],
                        "description": "Mathematical operation.",
                    },
                },
                "required": ["a", "b", "operation"],
            },
        )
    ]
)

#-------------------------pdf tool----------------------------------
pdf_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="read_pdf",
            description="Read a PDF file and return its extracted text.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the PDF file.",
                    },
                },
                "required": ["file_path"],
            },
        )
    ]
)

#----------------------search database tools----------------------------------
database_search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_records",
            description="Search previously saved records in the database.",
            parameters={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for.",
                    },
                },
                "required": ["keyword"],
            },
        )
    ]
)

def execute_tool(name: str, args: dict):
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")

    return TOOLS[name](**args)


def ask_agent(
    user_message: str,
    file_path: str | None = None
) -> str:
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    ]

    config = types.GenerateContentConfig(
        tools=[
            calculator_tool,
            pdf_tool,
            database_search_tool,
        ]
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=config,
    )

    # Check whether the model requested a tool.
    function_call = None

    for part in response.candidates[0].content.parts:
        if part.function_call:
            function_call = part.function_call
            break

    # If no tool is needed, return the model's normal response.
    if function_call is None:
        return response.text

    if function_call.name == "read_pdf":
        if file_path is None:
            raise ValueError("PDF file path is required.")

        args = {
            "file_path": file_path
        }
    else:
        args = dict(function_call.args)

    # Execute the requested tool.
    tool_result = execute_tool(
        function_call.name,
        args
    )

    # Add the model's tool-call message to the conversation.
    contents.append(response.candidates[0].content)

    # Send the tool result back to Gemini.
    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": tool_result},
                )
            ],
        )
    )

    # Ask Gemini to produce the final answer.
    final_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=config,
    )

    return final_response.text