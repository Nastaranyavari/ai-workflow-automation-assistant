import os

from dotenv import load_dotenv
from google import genai

from app.models.task import Task


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


def generate_response(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    return response.text


def analyze_request(user_request: str) -> Task:
    prompt = f"""
You are the task analysis component of an AI workflow automation assistant.

Analyze the user's request and select the best task.

Allowed tasks:
- general_chat: normal conversation or questions.
- summarize_document: read a document and summarize it.
- summarize_and_save: read a document, summarize it, and save the summary to a database.

Determine which external resources are required.

User request:
{user_request}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Task,
        },
    )

    return Task.model_validate_json(response.text)