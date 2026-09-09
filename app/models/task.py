from typing import Literal

from pydantic import BaseModel


class Task(BaseModel):
    task: Literal[
        "general_chat",
        "summarize_document",
        "summarize_and_save",
    ]

    needs_file: bool
    needs_database: bool
    needs_email: bool