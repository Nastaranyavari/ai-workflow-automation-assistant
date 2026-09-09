from google.genai import types

from app.agent.graph import graph


result = graph.invoke(
    {
        "messages": [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "این PDF را بخوان، خلاصه کوتاهی تهیه کن "
                            "و خلاصه را با عنوان Insurance Law Summary "
                            "در دیتابیس ذخیره کن."
                        )
                    )
                ],
            )
        ],
        "file_path": "data/sample.pdf",
        "status": "started",
    }
)

print("Status:", result["status"])
print()
print("Final answer:")
print(result["messages"][-1])