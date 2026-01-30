import json
import os
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Book
from datetime import datetime
import requests


def carica_json(file_name):
    file_path =  file_name
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def genera_pdf(bilancio, anno):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.drawString(100, 800, f"Bilancio Annuale {anno}")

    y = 780
    for tipo, transazioni in bilancio.items():
        p.drawString(100, y, tipo.upper())
        y -= 20
        for t in transazioni:
            p.drawString(120, y, f"{t['data']} - {t['descrizione']}: €{t['importo']}")
            y -= 15

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def scarica_pdf(request, anno):
    bilancio = carica_json("data/bilancio.json").get(str(anno), {"entrate": [], "uscite": []})
    pdf_buffer = genera_pdf(bilancio, anno)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="bilancio_{anno}.pdf"'
    return response

def salva_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_book_cover(title, author):
    query = f"{title} {author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        for item in data['items']:
            if 'imageLinks' in item['volumeInfo']:
                return item['volumeInfo']['imageLinks']['thumbnail']

    return None


def import_books_from_json(json_path="data/books.json"):
    with open(json_path, "r") as f:
        books = json.load(f)

    for book in books:
        read_date = datetime.strptime(book["read_date"], "%Y-%m-%d").date()
        Book.objects.update_or_create(
            title=book["title"],
            defaults={
                "author": book["author"],
                "read_date": read_date,
                "cover_url": book.get("cover", ""),
            }
        )