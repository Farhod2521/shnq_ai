import uuid
from django.db import models


class Category(models.Model):
    """
    Normativ toifa: SHNQ, QMQ, SanQvaN
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.code


class Document(models.Model):
    """
    Hujjat: SHNQ 2.08.02-09 kabi
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="documents")
    title = models.CharField(max_length=500)
    code = models.CharField(max_length=100, db_index=True)
    lex_url = models.URLField(blank=True, null=True)

    original_file = models.FileField(upload_to="docs/original/", blank=True, null=True)
    html_file = models.FileField(upload_to="docs/html/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("category", "code")

    def __str__(self):
        return self.code


class Chapter(models.Model):
    """
    Bob / bolim
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.document.code} - {self.title}"


class Clause(models.Model):
    """
    Norma / band
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="clauses")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, related_name="clauses")

    clause_number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    html_anchor = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    text = models.TextField()

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.document.code} - {self.clause_number}"


class ClauseEmbedding(models.Model):
    """
    Embedding metadata va vector
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clause = models.OneToOneField(Clause, on_delete=models.CASCADE, related_name="embedding")

    embedding_model = models.CharField(max_length=100)
    vector = models.JSONField()
    token_count = models.PositiveIntegerField(default=0)

    shnq_code = models.CharField(max_length=100)
    chapter_title = models.CharField(max_length=500, blank=True, null=True)
    clause_number = models.CharField(max_length=50, blank=True, null=True)
    lex_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)


class QuestionAnswer(models.Model):
    """
    RAG savol-javob logi
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    top_clause_ids = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
