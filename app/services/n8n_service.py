import os

import requests
from dotenv import load_dotenv


load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


def notify_n8n(
    session_id: str,
    task: str,
    status: str,
    record_id: int | None = None,
):
    if not N8N_WEBHOOK_URL:
        raise ValueError("N8N_WEBHOOK_URL is not set.")

    payload = {
        "session_id": session_id,
        "task": task,
        "status": status,
        "record_id": record_id,
    }

    response = requests.post(
        N8N_WEBHOOK_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()