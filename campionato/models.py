from django.db import models

class Stagione(models.Model):
    squadra = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    girone = models.CharField(max_length=5)
    posizione = models.PositiveSmallIntegerField()
    stagione = models.CharField(max_length=20)
    inizio = models.DateField()
    fine = models.DateField()
    partite_giocate = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.squadra} - {self.stagione}"


class Partita(models.Model):
    CAMPO_CHOICES = [
        ('casa', 'Casa'),
        ('trasferta', 'Trasferta')
    ]

    RISULTATO_CHOICES = [
        ('V', 'Vittoria'),
        ('P', 'Perdita'),
        ('N', 'Pareggio')
    ]

    stagione = models.ForeignKey(Stagione, related_name='partite', on_delete=models.CASCADE)
    data = models.DateField()
    casa = models.CharField(max_length=100)
    trasferta = models.CharField(max_length=100)
    gol_casa = models.PositiveIntegerField()
    gol_trasferta = models.PositiveIntegerField()
    campo = models.CharField(max_length=10, choices=CAMPO_CHOICES)
    risultato = models.CharField(max_length=1, choices=RISULTATO_CHOICES)

    def __str__(self):
        return f"{self.casa} vs {self.trasferta} - {self.data}"
