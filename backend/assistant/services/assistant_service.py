from pathlib import Path

from app.agent.graph import graph


class AssistantService:

    @staticmethod
    def save_uploaded_file(file):
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = upload_dir / file.name

        with file_path.open("wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return file_path

    @staticmethod
    def run(
        message: str,
        session_id: str,
        file=None,
    ):

        file_path = None

        if file:
            file_path = AssistantService.save_uploaded_file(file)

        input_state = {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "status": "started",
            "session_id": session_id,
            "task": None,
            "record_id": None,
            "n8n_result": None,
        }

        if file_path:
            input_state["file_path"] = str(file_path)

        config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

        result = graph.invoke(
            input_state,
            config=config,
        )

        return {
            "status": result["status"],
            "response": result["messages"][-1]["content"],
        }