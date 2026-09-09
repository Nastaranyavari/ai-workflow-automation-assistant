from app.tools.calculator import calculate


def test_add():
    result = calculate(10, 5, "add")

    assert result == 15


def test_multiply():
    result = calculate(10, 5, "multiply")

    assert result == 50