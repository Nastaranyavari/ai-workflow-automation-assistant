from app.tools.database_tool import save_record


result = save_record(
    title="Test Meeting",
    content="This is a test record."
)

print(result)