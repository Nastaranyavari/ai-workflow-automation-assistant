from assistant.models import Record


def save_record(title: str, content: str) -> dict:
    record = Record.objects.create(
        title=title,
        content=content,
    )

    return {
        "success": True,
        "record_id": record.id,
    }


def search_records(keyword: str) -> list[dict]:
    records = Record.objects.filter(
        title__icontains=keyword
    ) | Record.objects.filter(
        content__icontains=keyword
    )

    return [
        {
            "id": record.id,
            "title": record.title,
            "content": record.content,
        }
        for record in records
    ]