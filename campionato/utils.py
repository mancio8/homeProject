def statistiche_multi_stagione(stagioni, nome_squadra):
    stats = {
        "stagioni": len(stagioni),
        "giocate": 0,
        "vittorie": 0,
        "pareggi": 0,
        "sconfitte": 0,
        "gol_fatti": 0,
        "gol_subiti": 0,
        "punti": 0,
    }

    for stagione in stagioni:
        for p in stagione.partite.all():
            stats["giocate"] += 1

            if p.casa == nome_squadra:
                fatti, subiti = p.gol_casa, p.gol_trasferta
            else:
                fatti, subiti = p.gol_trasferta, p.gol_casa

            stats["gol_fatti"] += fatti
            stats["gol_subiti"] += subiti

            if fatti > subiti:
                stats["vittorie"] += 1
                stats["punti"] += 3
            elif fatti == subiti:
                stats["pareggi"] += 1
                stats["punti"] += 1
            else:
                stats["sconfitte"] += 1

    stats["diff_reti"] = stats["gol_fatti"] - stats["gol_subiti"]
    stats["media_gol"] = round(stats["gol_fatti"] / stats["giocate"], 2) if stats["giocate"] else 0
    stats["media_punti"] = round(stats["punti"] / stats["giocate"], 2) if stats["giocate"] else 0

    return stats

def calcola_statistiche(partite, nome_squadra):
    stats = {
        "giocate": 0,
        "vittorie": 0,
        "pareggi": 0,
        "sconfitte": 0,
        "gol_fatti": 0,
        "gol_subiti": 0,
        "punti": 0,
        "casa": {"V": 0, "N": 0, "P": 0},
        "trasferta": {"V": 0, "N": 0, "P": 0},
    }

    for p in partite:
        stats["giocate"] += 1

        if p.casa == nome_squadra:
            fatti, subiti = p.gol_casa, p.gol_trasferta
        else:
            fatti, subiti = p.gol_trasferta, p.gol_casa

        stats["gol_fatti"] += fatti
        stats["gol_subiti"] += subiti

        if p.risultato == "V":
            stats["vittorie"] += 1
            stats["punti"] += 3
        elif p.risultato == "N":
            stats["pareggi"] += 1
            stats["punti"] += 1
        else:
            stats["sconfitte"] += 1

        stats[p.campo][p.risultato] += 1

    stats["diff_reti"] = stats["gol_fatti"] - stats["gol_subiti"]
    stats["media_gol"] = round(stats["gol_fatti"] / stats["giocate"], 2)

    return stats

