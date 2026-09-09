from app.tools.pdf_tool import read_pdf
from app.tools.database_tool import save_record
from app.services.llm import generate_response


def summarize_and_save(
    file_path: str,
) -> str:
    text = read_pdf(file_path)

    summary = generate_response(
        f"""
Summarize the following document in a concise way.

Document:
{text}
"""
    )

    return save_record(
        title="PDF Summary",
        content=summary,
    )