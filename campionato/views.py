import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Stagione, Partita
from django.http import HttpResponse
from .utils import statistiche_multi_stagione, calcola_statistiche


def statistiche_squadra(request, stagione_id):
    stagione = get_object_or_404(Stagione, id=stagione_id)
    partite = stagione.partite.all()

    stats = calcola_statistiche(partite, stagione.squadra)
    stats["posizione"] = stagione.posizione

    # Dati per grafico: vittorie/pareggi/sconfitte
    grafico = {
        "labels": ["Vittorie", "Pareggi", "Sconfitte"],
        "data": [stats["vittorie"], stats["pareggi"], stats["sconfitte"]],
        "colors": ["#28a745", "#ffc107", "#dc3545"],
    }

    return render(request, "campionato/statistiche.html", {
        "stagione": stagione,
        "stats": stats,
        "grafico": grafico,
    })




def statistiche_squadra_multi(request):
    squadra = request.GET.get("squadra", "FC Guardia Sanframondi")
    n = int(request.GET.get("n", 2))  # ultime n stagioni

    stagioni = (
        Stagione.objects
        .filter(squadra=squadra)
        .order_by("-inizio")[:n]
    )

    stats = statistiche_multi_stagione(stagioni, squadra)
    stats["stagioni"] = len(stagioni)  # numero stagioni considerate

    # Dati per grafico: punti per stagione
    grafico = {
        "labels": [s.stagione for s in stagioni][::-1],  # ordine cronologico
        "data": [s.posizione for s in stagioni][::-1],  # puoi usare punti se vuoi
        "colors": ["#007bff"] * len(stagioni)
    }

    return render(request, "campionato/statistiche_multi.html", {
        "squadra": squadra,
        "stagioni": stagioni,
        "stats": stats,
        "grafico": grafico,
    })


def import_success(request):
    return HttpResponse("Importazione completata")


@require_http_methods(["GET", "POST"])
def importa_json(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return HttpResponseBadRequest("File non trovato")

        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("JSON non valido")

        meta = data.get("meta")
        partite = data.get("partite")

        if not meta or not partite:
            return HttpResponseBadRequest("Struttura JSON non valida")

        # Crea stagione
        stagione = Stagione.objects.create(
            squadra=meta["squadra"],
            categoria=meta["categoria"],
            girone=meta["girone"],
            posizione=meta.get("posizione", 0),
            stagione=meta["stagione"],
            inizio=datetime.strptime(meta["periodo"]["inizio"], "%Y-%m-%d").date(),
            fine=datetime.strptime(meta["periodo"]["fine"], "%Y-%m-%d").date(),
            partite_giocate=meta["partite_giocate"],
        )

        # Crea partite
        for p in partite:
            Partita.objects.create(
                stagione=stagione,
                data=datetime.strptime(p["data"], "%Y-%m-%d").date(),
                casa=p["casa"],
                trasferta=p["trasferta"],
                gol_casa=p["gol_casa"],
                gol_trasferta=p["gol_trasferta"],
                campo=p["campo"],
                risultato=p["risultato"],
            )

        return redirect("import_success")

    return render(request, "campionato/importa_json.html")
