from django.db import models


class Document(models.Model):
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class Record(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="records",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title