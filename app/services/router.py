from app.models.task import Task
from app.services.workflow import summarize_and_save
from app.tools.pdf_tool import read_pdf
from app.tools.database_tool import search_records
from app.services.llm import generate_response


def execute_task(
    task: Task,
    file_path: str | None = None,
    user_request: str | None = None,
):
    if task.task == "general_chat":
        return "This is a general conversation task."

    if task.task == "summarize_document":
        if not file_path:
            raise ValueError("A file is required.")

        text = read_pdf(file_path)

        return generate_response(
            f"""
Summarize the following document concisely.

Document:
{text}
"""
        )

    if task.task == "summarize_and_save":
        if not file_path:
            raise ValueError("A file is required.")

        return summarize_and_save(file_path)

    if task.task == "search_database":
        if not user_request:
            raise ValueError("A search keyword is required.")

        return search_records(user_request)

    raise ValueError(f"Unsupported task: {task.task}")