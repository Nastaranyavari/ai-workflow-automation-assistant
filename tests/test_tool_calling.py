from app.agent.tool_calling import ask_agent


def test_calculator_tool_call():
    response = ask_agent("What is 125 multiplied by 37?")

    print(response)

    assert response is not None