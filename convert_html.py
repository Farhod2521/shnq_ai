import os
import re

from bs4 import BeautifulSoup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()  # noqa: E402

from django.db import transaction  # noqa: E402
from app_shnq.models import Category, Chapter, Clause, Document  # noqa: E402


MIN_TEXT_LEN = 30


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_clause_number(text):
    match = re.match(r"^(\d+(\.\d+)+)", text)
    return match.group(1) if match else None


@transaction.atomic
def import_shnq_html(
    file_path,
    category_code="SHNQ",
    doc_code="SHNQ",
    title="SHNQ",
    lex_url=None,
    reset=True,
):
    category, _ = Category.objects.get_or_create(
        code=category_code, defaults={"name": category_code}
    )
    document, _ = Document.objects.get_or_create(
        category=category,
        code=doc_code,
        defaults={"title": title, "lex_url": lex_url},
    )

    if reset:
        Clause.objects.filter(document=document).delete()
        Chapter.objects.filter(document=document).delete()

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    current_chapter = None
    chapter_order = 0
    clause_order = 0

    for elem in soup.find_all(["div", "a"]):
        if elem.name == "div" and "TEXT_HEADER_DEFAULT" in elem.get("class", []):
            header_text = clean_text(elem.get_text())
            if header_text:
                chapter_order += 1
                current_chapter = Chapter.objects.create(
                    document=document,
                    title=header_text,
                    order=chapter_order,
                )
            continue

        if elem.name == "div" and "ACT_TEXT" in elem.get("class", []):
            text = clean_text(elem.get_text())
            if len(text) < MIN_TEXT_LEN:
                continue

            clause_number = extract_clause_number(text)
            clause_order += 1
            Clause.objects.create(
                document=document,
                chapter=current_chapter,
                clause_number=clause_number,
                html_anchor=None,
                text=text,
                order=clause_order,
            )
            continue

        if elem.name == "a" and elem.get("id"):
            anchor = elem.get("id")
            last_clause = Clause.objects.filter(document=document).order_by("-order").first()
            if last_clause and not last_clause.html_anchor:
                last_clause.html_anchor = anchor
                last_clause.save(update_fields=["html_anchor"])


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "shnq.html")
    import_shnq_html(
        file_path=html_path,
        category_code="SHNQ",
        doc_code="SHNQ",
        title="SHNQ",
        lex_url=None,
        reset=True,
    )
    print("Import finished.")
