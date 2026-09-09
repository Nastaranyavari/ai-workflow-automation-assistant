from app.services.n8n_service import notify_n8n


result = notify_n8n(
    session_id="demo-python",
    task="summarize_and_save",
    status="completed",
    record_id=123,
)

print(result)