from app.services.workflow import summarize_and_save


result = summarize_and_save(
    "data/sample.pdf"
)

print(result)