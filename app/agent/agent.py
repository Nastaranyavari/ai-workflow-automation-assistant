from app.services.llm import analyze_request
from app.services.router import execute_task


def run_agent(
    user_request: str,
    file_path: str | None = None,
):
    task = analyze_request(user_request)

    print("Selected task:", task.task)
    print("Needs file:", task.needs_file)
    print("Needs database:", task.needs_database)
    print("Needs email:", task.needs_email)

    return execute_task(
        task=task,
        file_path=file_path,
        user_request=user_request,
    )