import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.calculator import calculate
from app.tools.pdf_tool import read_pdf
from app.tools.database_tool import search_records, save_record
from app.services.llm import generate_response


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


TOOLS = {
    "calculate": calculate,
    "read_pdf": read_pdf,
    "search_records": search_records,
    "save_record": save_record,
}

def get_tools():
    return types.Tool(
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
                        }
                    },
                    "required": ["file_path"],
                },
            ),
            types.FunctionDeclaration(
                name="save_record",
                description="Save a title and content into the database.",
                parameters={
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
                    "required": ["title", "content"],
                },
            ),
            types.FunctionDeclaration(
                name="search_records",
                description="Search records in the database by keyword.",
                parameters={
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Keyword to search for.",
                        }
                    },
                    "required": ["keyword"],
                },
            ),
            types.FunctionDeclaration(
                name="calculate",
                description="Perform a mathematical calculation.",
                parameters={
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
                    "required": ["a", "b", "operation"],
                },
            ),
        ]
    )

def run_agent_loop(
    user_message: str,
    file_path: str | None = None,
) -> str:

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    ]

    if file_path:
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"Available PDF file: {file_path}"
                    )
                ],
            )
        )

    config = types.GenerateContentConfig(
        tools=[get_tools()]
    )

    while True:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=config,
        )

        function_call = None

        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_call = part.function_call
                break

        if function_call is None:
            return response.text

        tool_name = function_call.name
        tool_args = dict(function_call.args)

        if tool_name == "read_pdf" and file_path:
            tool_args["file_path"] = file_path

        if tool_name not in TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool_result = TOOLS[tool_name](**tool_args)

        contents.append(response.candidates[0].content)

        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": tool_result},

                    )
                ],
            )
        )