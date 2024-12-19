from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.conf import settings
from django.utils import timezone
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import csv
from django import forms
from .forms import AggiungiOreForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Percorso al file JSON
JSON_FILE_PATH = 'data/preferiti.json'

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def aggiungi_preferito(request):
    if request.method == 'POST':
        titolo = request.POST.get('titolo')
        immagine = request.POST.get('immagine')
        url = request.POST.get('url')

        nuovo_preferito = {
            "titolo": titolo,
            "immagine": immagine,
            "url": url
        }

        # Carica il file JSON
        try:
            with open(JSON_FILE_PATH, 'r') as file:
                preferiti = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            preferiti = []

        # Aggiungi il nuovo preferito
        preferiti.append(nuovo_preferito)

        # Salva nel file JSON
        try:
            with open(JSON_FILE_PATH, 'w') as file:
                json.dump(preferiti, file, indent=4)
        except IOError as e:
            return render(request, 'aggiungi_preferito.html', {
                'error': f"Errore nel salvataggio del file: {e}"
            })

        return redirect('aggiungi_preferito')

    # Carica i preferiti esistenti
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            preferiti = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        preferiti = []

    return render(request, 'aggiungi_preferito.html', {'preferiti': preferiti})








def calendario(request):
    # Carica il file JSON delle partite
    with open('data/matches.json', 'r') as f:
        matches_data = json.load(f)  # Supponiamo che i match siano sotto la chiave 'matches'

    # Carica il file JSON dei loghi
    with open('data/team_logos.json', 'r') as f:
        logos_data = json.load(f)

    # Crea un dizionario per velocizzare la ricerca del logo
    logos_dict = {logo['team']: logo['logo'] for logo in logos_data}

    # Aggiungi i loghi alle partite
    for match in matches_data:
        match['team1_logo'] = logos_dict.get(match['team1'], '')
        match['team2_logo'] = logos_dict.get(match['team2'], '')

    # Trova il prossimo match
    next_match = None
    today = datetime.now()
    for match in matches_data:
        match_date = datetime.strptime(match['data'], "%d/%m/%y %H:%M")
        if match_date > today:
            next_match = match
            break

    # Recupera il meteo solo per il prossimo match
    if next_match:
        api_key = "2008820b2a714db95f5dce0ff41e52bc"  # Inserisci la tua chiave API meteo
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        try:
            params = {
                'lat': next_match['lat'],  # Assumendo che latitudine e longitudine siano nel file JSON
                'lon': next_match['lon'],
                'appid': api_key,
                'units': 'metric',  # Usa unità metriche (Celsius)
                'lang': 'it'  # Per ottenere la descrizione in italiano
            }
            response = requests.get(weather_url, params=params)
            if response.status_code == 200:
                weather_data = response.json()
                next_match['weather'] = {
                    'temperature': weather_data['main']['temp'],
                    'description': weather_data['weather'][0]['description'],
                    'icon': f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}.png"
                }
            else:
                next_match['weather'] = {'error': 'Dati meteo non disponibili'}
        except Exception as e:
            next_match['weather'] = {'error': str(e)}

    # Passa i dati al template
    return render(request, 'calendar.html', {
        'matches': matches_data,  # Tutti i match
        'next_match': next_match  # Il prossimo match
    })




def table_view(request):
    # URL della pagina da cui effettuare il web scraping
    url = "https://benevento.iamcalcio.it/classifiche/188/3a-categoria-girone-b/"
    
    # Recupera il contenuto della pagina
    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({"error": f"Errore durante il caricamento della pagina: {response.status_code}"}, status=500)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Trova la tabella con le classifiche
    table = soup.find("table", {"class": "table"})
    if not table:
        return JsonResponse({"error": "Tabella non trovata nella pagina"}, status=404)
    
    # Estrai i dati della tabella
    headers = [header.text.strip() for header in table.find_all("th")]
    rows = []
    posizione = []  # Posizione in classifica
    squadra = []    # Nome della squadra
    punti = []      # Punti della squadra
    partite = []    # Partite giocate

    for row in table.find_all("tr")[1:]:  # Salta l'intestazione
        cells = [cell.text.strip() for cell in row.find_all("td")]
        if len(cells) >= 4:  # Assicurati che ci siano abbastanza celle
            posizione.append(cells[0])  # Posizione
            squadra.append(cells[1])    # Nome squadra
            punti.append(cells[2])      # Punti
            partite.append(cells[3])    # Partite giocate

    # Combina i dati in un'unica lista di tuple
    classifiche = list(zip(posizione, squadra, punti, partite))
    
    # Controllo del formato richiesto (HTML o CSV)
    formato = request.GET.get("format", "html")
    if formato == "csv":
        # Esporta i dati come CSV
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="classifiche.csv"'
        
        writer = csv.writer(response)
        writer.writerow(headers)  # Scrivi le intestazioni
        writer.writerows(rows)    # Scrivi i dati
        
        return response
    
    # Rendi i dati disponibili al template
    return render(request, "table_view.html", {"classifiche": classifiche})


# Percorso del file JSON
JSON_FILE = 'data/ferie_data.json'

# Funzione per leggere i dati dal file JSON
def read_ferie_data():
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"ferie_godute": 0, "permessi_goduti": 0}

# Funzione per scrivere i dati nel file JSON
def write_ferie_data(data):
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f)

# Riepilogo ferie e permessi
def riepilogo_ferie_permessi(request):
    data = read_ferie_data()

    # Dati annuali calcolati
    ferie_totali_annuali_ore = 14.6 * 12  # 14.4 ore al mese
    permessi_totali_annuali_ore = 5.33 * 12  # 4.66 ore al mese

    # Converto le ferie totali annuali in giorni (8 ore per giorno lavorativo)
    ferie_totali_annuali_giorni = ferie_totali_annuali_ore / 8
    permessi_totali_annuali_giorni = permessi_totali_annuali_ore / 8

    ferie_rimanenti_ore = ferie_totali_annuali_ore - data['ferie_godute']
    permessi_rimanenti_ore = permessi_totali_annuali_ore - data['permessi_goduti']

    # Conversione in giorni
    ferie_rimanenti_giorni = ferie_rimanenti_ore / 8
    permessi_rimanenti_giorni = permessi_rimanenti_ore / 8

    if request.method == 'POST':
        form = AggiungiOreForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            ore = form.cleaned_data['ore']

            if tipo == 'ferie':
                data['ferie_godute'] += ore
            elif tipo == 'permessi':
                data['permessi_goduti'] += ore

            write_ferie_data(data)
            return redirect('riepilogo')
    else:
        form = AggiungiOreForm()

    return render(request, 'riepilogo.html', {
        'data': data,
        'ferie_totali_annuali_ore': ferie_totali_annuali_ore,
        'permessi_totali_annuali_ore': permessi_totali_annuali_ore,
        'ferie_totali_annuali_giorni': ferie_totali_annuali_giorni,
        'permessi_totali_annuali_giorni': permessi_totali_annuali_giorni,
        'ferie_rimanenti_giorni' : ferie_rimanenti_giorni,
        'permessi_rimanenti_giorni' : permessi_rimanenti_giorni,
        'form': form
    })


# Reset ferie e permessi
def reset_ferie_permessi(request):
    data = {
        "ferie_godute": 0,
        "permessi_goduti": 0
    }
    write_ferie_data(data)
    return redirect('riepilogo')


def esporta_pdf(request):
    # Crea una risposta HTTP con il contenuto PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="riepilogo_ferie_permessi.pdf"'

    # Crea un canvas PDF
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Dimensioni pagina

    # Dati
    data = read_ferie_data()
    ferie_totali_annuali_ore = 14.6 * 12
    permessi_totali_annuali_ore = 5.33 * 12
    ferie_godute_ore = data.get('ferie_godute', 0)
    permessi_goduti_ore = data.get('permessi_goduti', 0)
    ferie_rimanenti_ore = ferie_totali_annuali_ore - ferie_godute_ore
    permessi_rimanenti_ore = permessi_totali_annuali_ore - permessi_goduti_ore

    # Scrivi i dati nel PDF
    c.drawString(100, height - 100, f"Riepilogo Ferie e Permessi")
    c.drawString(100, height - 120, f"Ferie Utilizzate: {ferie_godute_ore} ore ({ferie_godute_ore / 8:.2f} giorni)")
    c.drawString(100, height - 140, f"Permessi Utilizzati: {permessi_goduti_ore} ore ({permessi_goduti_ore / 8:.2f} giorni)")
    c.drawString(100, height - 160, f"Ferie Rimanenti: {ferie_rimanenti_ore:.2f} ore ({ferie_rimanenti_ore / 8:.2f} giorni)")
    c.drawString(100, height - 180, f"Permessi Rimanenti: {permessi_rimanenti_ore:.2f} ore ({permessi_rimanenti_ore / 8:.2f} giorni)")

    # Salva e restituisci il PDF
    c.save()
    return response
