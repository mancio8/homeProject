import os
import json
import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils import carica_json, salva_json, genera_pdf  # Se preferisci, puoi mantenere queste funzioni in un file separato

BILANCIO_FILE = "data/bilancio.json"
EVENTI_FILE = "data/eventi.json"

def bilancio_annuale(request, anno):
    bilancio = carica_json(BILANCIO_FILE).get(str(anno), {"entrate": [], "uscite": []})
    saldo = round(sum(t["importo"] for t in bilancio["entrate"]) - sum(t["importo"] for t in bilancio["uscite"]), 2)

    return render(request, "bilancio_annuale.html", {"anno": anno, "bilancio": bilancio, "saldo": saldo})

def bilancio_evento(request, evento):
    eventi = carica_json(EVENTI_FILE)
    
    if evento not in eventi:
        return HttpResponse("Evento non trovato", status=404)
    
    bilancio_evento = eventi[evento]
    saldo = round(sum(t["importo"] for t in bilancio_evento["entrate"]) - sum(t["importo"] for t in bilancio_evento["uscite"]), 2)

    return render(request, "bilancio_evento.html", {"evento": evento, "bilancio": bilancio_evento, "saldo": saldo})

def scarica_pdf(request, anno):
    bilancio = carica_json(BILANCIO_FILE).get(str(anno), {"entrate": [], "uscite": []})
    pdf_buffer = genera_pdf(bilancio, anno)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="bilancio_{anno}.pdf"'
    return response

def gestione_bilancio(request):
    bilancio = carica_json(BILANCIO_FILE)
    eventi = carica_json(EVENTI_FILE)

    bilancio.setdefault("entrate", {})
    bilancio.setdefault("uscite", {})

    if request.method == "POST":
        if "nuovo_evento" in request.POST:
            nuovo_evento = request.POST.get("nuovo_evento").strip()
            if nuovo_evento and nuovo_evento not in eventi:
                eventi[nuovo_evento] = {"entrate": [], "uscite": []}
                salva_json(EVENTI_FILE, eventi)
        else:
            tipo = request.POST.get("tipo")
            data = request.POST.get("data")
            descrizione = request.POST.get("descrizione")
            try:
                importo = float(request.POST.get("importo", 0) or 0)
            except ValueError:
                importo = 0

            evento = request.POST.get("evento")
            nuova_transazione = {"data": data, "descrizione": descrizione, "importo": importo}

            year = datetime.strptime(data, "%Y-%m-%d").year
            bilancio.setdefault(str(year), {"entrate": [], "uscite": []})

            if tipo == "entrata":
                bilancio[str(year)]["entrate"].append(nuova_transazione)
            else:
                bilancio[str(year)]["uscite"].append(nuova_transazione)

            if evento and evento in eventi:
                eventi[evento].setdefault("entrate", [])
                eventi[evento].setdefault("uscite", [])
                if tipo == "entrata":
                    eventi[evento]["entrate"].append(nuova_transazione)
                else:
                    eventi[evento]["uscite"].append(nuova_transazione)

            salva_json(BILANCIO_FILE, bilancio)
            salva_json(EVENTI_FILE, eventi)

        return redirect("gestione_bilancio")

    totale_entrate = sum(item["importo"] for item in bilancio.get(str(datetime.now().year), {}).get("entrate", []))
    totale_uscite = sum(item["importo"] for item in bilancio.get(str(datetime.now().year), {}).get("uscite", []))
    saldo = round(totale_entrate - totale_uscite, 2)

    return render(request, "gestione_bilancio.html", {
        "bilancio": bilancio,
        "eventi": eventi,
        "totale_entrate": totale_entrate,
        "totale_uscite": totale_uscite,
        "saldo": saldo
    })

def scarica_bilancio_csv(request, anno):
    bilancio = carica_json(BILANCIO_FILE).get(str(anno), {"entrate": [], "uscite": []})

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="bilancio_{anno}.csv"'

    writer = csv.writer(response, delimiter=";")  # Usa ";" per compatibilità Excel

    # Intestazione
    writer.writerow(["Bilancio", anno])
    writer.writerow(["Data", "Descrizione", "Importo", "", "Data", "Descrizione", "Importo"])
    writer.writerow(["Entrate", "", "", "", "Uscite", "", ""])

    # Determiniamo il numero massimo di righe per allineare entrate e uscite
    max_righe = max(len(bilancio["entrate"]), len(bilancio["uscite"]))

    # Scriviamo i dati allineati
    for i in range(max_righe):
        entrata = bilancio["entrate"][i] if i < len(bilancio["entrate"]) else {"data": "", "descrizione": "", "importo": ""}
        uscita = bilancio["uscite"][i] if i < len(bilancio["uscite"]) else {"data": "", "descrizione": "", "importo": ""}
        
        writer.writerow([
            entrata["data"], entrata["descrizione"], entrata["importo"], "",
            uscita["data"], uscita["descrizione"], uscita["importo"]
        ])

    # Calcoliamo i totali
    totale_entrate = round(sum(t["importo"] for t in bilancio["entrate"]), 2)
    totale_uscite = round(sum(t["importo"] for t in bilancio["uscite"]), 2)
    saldo_finale = round(totale_entrate - totale_uscite, 2)

    # Riga di separazione
    writer.writerow(["-" * 10, "", "", "", "-" * 10, "", ""])

    # Totali
    writer.writerow(["Totale Entrate", "", totale_entrate, "", "Totale Uscite", "", totale_uscite])

    # Saldo finale
    writer.writerow(["Saldo Finale", "", saldo_finale])

    return response


def scarica_bilancio_evento_csv(request, evento):
    eventi = carica_json(EVENTI_FILE)
    evento_dati = eventi.get(str(evento))

    if not evento_dati:
        return HttpResponse("Evento non trovato", status=404)

    # Controlla se "bilancio" è presente o se le entrate/uscite sono direttamente dentro l'evento
    bilancio = evento_dati.get("bilancio", evento_dati)

    entrate = bilancio.get("entrate", [])
    uscite = bilancio.get("uscite", [])

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="bilancio_evento_{evento}.csv"'

    writer = csv.writer(response, delimiter=";")

    # Intestazione
    writer.writerow(["Bilancio Evento", evento])
    writer.writerow(["Data", "Descrizione", "Importo", "", "Data", "Descrizione", "Importo"])
    writer.writerow(["Entrate", "", "", "", "Uscite", "", ""])

    # Determina il numero massimo di righe per allineare entrate e uscite
    max_righe = max(len(entrate), len(uscite))

    # Scriviamo i dati allineati
    for i in range(max_righe):
        entrata = entrate[i] if i < len(entrate) else {"data": "", "descrizione": "", "importo": ""}
        uscita = uscite[i] if i < len(uscite) else {"data": "", "descrizione": "", "importo": ""}

        writer.writerow([
            entrata.get("data", ""), entrata.get("descrizione", ""), entrata.get("importo", ""), "",
            uscita.get("data", ""), uscita.get("descrizione", ""), uscita.get("importo", "")
        ])

    
    # Calcoliamo i totali e arrotondiamo
    totale_entrate = round(sum(t.get("importo", 0) for t in entrate), 2)
    totale_uscite = round(sum(t.get("importo", 0) for t in uscite), 2)
    saldo_finale = round(totale_entrate - totale_uscite, 2)


    # Riga di separazione
    writer.writerow(["-" * 10, "", "", "", "-" * 10, "", ""])

    # Totali
    writer.writerow(["Totale Entrate", "", totale_entrate, "", "Totale Uscite", "", totale_uscite])

    # Saldo finale
    writer.writerow(["Saldo Finale", "", saldo_finale])

    return response
