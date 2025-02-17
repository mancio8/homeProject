import json
import os
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse

DATA_DIR = 'data'

def carica_json(file_name):
    file_path = DATA_DIR + file_name
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
