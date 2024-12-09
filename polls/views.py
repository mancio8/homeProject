from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.conf import settings
from django.utils import timezone
from pathlib import Path
from datetime import datetime

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
        matches_data = json.load(f)['matches']  # Supponiamo che i match siano sotto la chiave 'matches'

    # Carica il file JSON dei loghi
    with open('data/team_logos.json', 'r') as f:
        logos_data = json.load(f)

    # Crea un dizionario per velocizzare la ricerca del logo
    logos_dict = {logo['team']: logo['logo'] for logo in logos_data}

    # Aggiungi il logo a ogni partita
    for match in matches_data:
        team1_logo = logos_dict.get(match['team1'], '')
        team2_logo = logos_dict.get(match['team2'], '')

    


        match['team1_logo'] = team1_logo
        match['team2_logo'] = team2_logo

    next_match = None
    today = datetime.now()
    for match in matches_data:
        match_date = datetime.strptime(match['data'], "%d/%m/%y %H:%M")
        if match_date > today:
            next_match = match
            break

    
    
    # Passa i dati al template
    return render(request, 'calendar.html', {
        'matches': matches_data,  # Tutti i match
        'next_match': next_match  # Il prossimo match
    })
