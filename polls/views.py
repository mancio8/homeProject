from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.conf import settings
from django.utils import timezone
from pathlib import Path
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import csv
from django import forms
from .forms import AggiungiOreForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os




# Percorso del file JSON
JSON_FILE = 'data/ferie_data.json'
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

    # Elenco delle festività del 2025
    festivita = [
        {"nome": "Capodanno", "data": datetime(2025, 1, 1)},
        {"nome": "Epifania", "data": datetime(2025, 1, 6)},
        {"nome": "Pasqua", "data": datetime(2025, 4, 20)},
        {"nome": "Pasquetta", "data": datetime(2025, 4, 21)},
        {"nome": "Festa della Liberazione", "data": datetime(2025, 4, 25)},
        {"nome": "Festa del Lavoro", "data": datetime(2025, 5, 1)},
        {"nome": "Festa della Repubblica", "data": datetime(2025, 6, 2)},
        {"nome": "Ferragosto", "data": datetime(2025, 8, 15)},
        {"nome": "Ognissanti", "data": datetime(2025, 11, 1)},
        {"nome": "Immacolata Concezione", "data": datetime(2025, 12, 8)},
        {"nome": "Natale", "data": datetime(2025, 12, 25)},
        {"nome": "Santo Stefano", "data": datetime(2025, 12, 26)},
    ]

    # Aggiungi l'indicazione dei ponti
    for festa in festivita:
        giorno_settimana = festa["data"].weekday()  # 0=Lunedì, 1=Martedì, ..., 6=Domenica
        festa["ponte"] = giorno_settimana in [1, 3]  # Ponte se Martedì o Giovedì

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
        'ferie_rimanenti_giorni': ferie_rimanenti_giorni,
        'permessi_rimanenti_giorni': permessi_rimanenti_giorni,
        'form': form,
        'festivita': festivita,  # Aggiungi le festività al contesto
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


def artist_songs_view(request):
    # Cartella in cui si trovano i file JSON
    json_folder = 'data/karaoke/'

    # Carica i dati mantenendo separati i file JSON
    json_data = {}
    for file_name in os.listdir(json_folder):
        if file_name.endswith('.json'):
            file_path = os.path.join(json_folder, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data[file_name] = json.load(file)

    # Ottieni il parametro di ricerca
    query = request.GET.get('q', '')

    # Filtra i risultati se è presente una query
    filtered_songs = {}
    if query:
        for file_name, data in json_data.items():
            for artist, songs in data.items():
                # Cerca parzialmente nei titoli delle canzoni
                matched_songs = [song for song in songs if query.lower() in song.lower()]
                if matched_songs:
                    if file_name not in filtered_songs:
                        filtered_songs[file_name] = {}
                    filtered_songs[file_name][artist] = matched_songs
    else:
        # Se non c'è una query, carica tutti i dati
        filtered_songs = json_data

    # Passa i dati al template
    return render(request, 'artist_songs.html', {
        'artist_songs': filtered_songs,
        'query': query,
    })

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






# Funzione per caricare i libri dal file JSON
def load_books():
    try:
        with open('data/books.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Funzione per salvare i libri nel file JSON
def save_books(books):
    with open('data/books.json', 'w') as file:
        json.dump(books, file, indent=4)

# Funzione per aggiungere un libro
def add_book(title, author, read_date):
    cover_url = get_book_cover(title, author)
    return {
        'title': title,
        'author': author,
        'read_date': read_date,
        'cover': cover_url if cover_url else 'URL non disponibile'
    }

# Funzione per modificare un libro
def edit_book(book_to_edit, author, read_date, cover_url):
    book_to_edit['author'] = author
    book_to_edit['read_date'] = read_date
    book_to_edit['cover'] = cover_url if cover_url else book_to_edit['cover']
    return book_to_edit

def download_books_json(request):
    books = load_books()
    return JsonResponse(books, safe=False)

def add_and_view_books(request):
    books = load_books()
    sort_by = request.GET.get('sort_by', 'title')

    # Ordinamento dei libri
    books.sort(key=lambda x: x.get(sort_by, ''))

    if request.method == 'POST':
        # Aggiungi un libro
        if 'add_book' in request.POST:
            title = request.POST['title']
            author = request.POST['author']
            read_date = request.POST['read_date']

            book = add_book(title, author, read_date)
            books.append(book)
            save_books(books)

        # Modifica un libro
        elif 'edit_book' in request.POST:
            title = request.POST['title']
            author = request.POST['author']
            read_date = request.POST['read_date']
            cover_url = request.POST['cover_url']

            book_to_edit = next((book for book in books if book['title'] == title), None)
            if book_to_edit:
                edit_book(book_to_edit, author, read_date, cover_url)
                save_books(books)

            return redirect('view_books')

    # Verifica se stiamo cercando di modificare un libro
    edit_title = request.GET.get('edit')
    if edit_title:
        book_to_edit = next((book for book in books if book['title'] == edit_title), None)
        if book_to_edit:
            return render(request, 'view_books.html', {'books': books, 'sort_by': sort_by, 'edit_book': book_to_edit})

    return render(request, 'view_books.html', {'books': books, 'sort_by': sort_by})


def delete_book(request, title):
    # Carica i libri dal file JSON
    try:
        with open('data/books.json', 'r') as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []

    # Trova e rimuovi il libro con il titolo specificato
    books = [book for book in books if book['title'] != title]

    # Salva il file JSON dopo aver rimosso il libro
    with open('data/books.json', 'w') as file:
        json.dump(books, file, indent=4)

    # Reindirizza alla pagina dei libri dopo la rimozione
    return redirect('view_books')






















