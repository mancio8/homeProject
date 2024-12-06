# Usa l'immagine ufficiale di Python
FROM python:3.10-slim

# Variabili d'ambiente per ottimizzare Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta la directory di lavoro
WORKDIR /app

# Installa le dipendenze
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia i file del progetto
COPY . /app/

# Espone la porta di Django
EXPOSE 3000

# Comando per avviare Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
