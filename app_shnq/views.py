from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .embeddings import cosine_similarity, embed_text
from .models import Clause, ClauseEmbedding, QuestionAnswer


def _ensure_embeddings():
    missing = Clause.objects.filter(embedding__isnull=True).select_related("document", "chapter")
    for clause in missing:
        vector = embed_text(clause.text)
        ClauseEmbedding.objects.create(
            clause=clause,
            embedding_model="hashing-v1",
            vector=vector,
            token_count=len(clause.text.split()),
            shnq_code=clause.document.code,
            chapter_title=clause.chapter.title if clause.chapter else None,
            clause_number=clause.clause_number,
            lex_url=clause.document.lex_url,
        )


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ChatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        _ensure_embeddings()

        query_vec = embed_text(message)
        embeddings = (
            ClauseEmbedding.objects.select_related("clause", "clause__document", "clause__chapter")
            .all()
        )

        scored = []
        for emb in embeddings:
            score = cosine_similarity(query_vec, emb.vector)
            scored.append((score, emb))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [item[1] for item in scored[:5]]

        if not top:
            return Response({"answer": "Mos band topilmadi.", "sources": []})

        best = top[0]
        answer = best.clause.text
        sources = []
        for emb in top:
            clause = emb.clause
            sources.append(
                {
                    "shnq_code": emb.shnq_code,
                    "chapter": emb.chapter_title,
                    "clause_number": emb.clause_number,
                    "html_anchor": clause.html_anchor,
                    "lex_url": emb.lex_url,
                }
            )

        QuestionAnswer.objects.create(
            question=message,
            answer=answer,
            top_clause_ids=[str(emb.clause_id) for emb in top],
        )

        return Response({"answer": answer, "sources": sources})
