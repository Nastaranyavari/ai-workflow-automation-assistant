from app.models.task import Task


def test_task_model():
    task = Task(
        task="analyze_sales_report",
        needs_file=True,
        needs_database=True,
        needs_email=False
    )

    assert task.task == "analyze_sales_report"
    assert task.needs_file is True
    assert task.needs_database is True
    assert task.needs_email is False