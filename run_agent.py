from app.agent.tool_calling import ask_agent


result = ask_agent(
    "در دیتابیس دنبال خلاصه قانون بیمه بگرد و آن را به من نشان بده."
)

print(result)