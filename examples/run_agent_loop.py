from app.agent.agent_loop import run_agent_loop


result = run_agent_loop(
    user_message="""
    Read this PDF.
    Summarize it briefly.
    Save the summary to the database with the title
    "Insurance Law Summary".
    """,
    file_path="data/sample.pdf",
)

print()
print("Final result:")
print(result)