from app.services.llm import analyze_request


request = """
یک ایمیل برای مدیر درباره جلسه فردا آماده کن.
"""

result = analyze_request(request)

print(result)
print()
print("Task:", result.task)
print("Needs file:", result.needs_file)
print("Needs database:", result.needs_database)
print("Needs email:", result.needs_email)