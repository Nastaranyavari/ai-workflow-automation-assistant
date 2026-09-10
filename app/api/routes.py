from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from app.agent.graph import graph


router = APIRouter()



@router.post("/assistant")
async def assistant(
    message: str = Form(...),
    session_id: str = Form(...),
    file: UploadFile | None = File(None),
):
    file_path = None

    if file:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = upload_dir / file.filename

        content = await file.read()

        file_path.write_bytes(content)

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
            "thread_id": session_id
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