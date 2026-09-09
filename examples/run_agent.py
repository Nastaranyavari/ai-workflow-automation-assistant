"""from app.agent.agent import run_agent


result = run_agent(
    user_request="این فایل را خلاصه کن و خلاصه را در دیتابیس ذخیره کن.",
    file_path="data/sample.pdf",
)

print(result)"""

from app.agent.agent import run_agent

result = run_agent(
    user_request="رکورد 23 را پیدا کن",
)

print(result)