from django.contrib import admin

from .models import (
    Category,
    Chapter,
    Clause,
    ClauseEmbedding,
    Document,
    QuestionAnswer,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "category", "lex_url", "created_at")
    list_filter = ("category",)
    search_fields = ("code", "title")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "document", "order")
    list_filter = ("document",)
    search_fields = ("title",)
    ordering = ("document", "order")


@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ("clause_number", "document", "chapter", "order")
    list_filter = ("document", "chapter")
    search_fields = ("clause_number", "text", "html_anchor")
    ordering = ("document", "order")


@admin.register(ClauseEmbedding)
class ClauseEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("clause", "embedding_model", "token_count", "shnq_code")
    search_fields = ("clause__clause_number", "shnq_code", "chapter_title")


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "created_at")
    search_fields = ("question", "answer")
