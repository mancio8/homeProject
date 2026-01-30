# Usa l'immagine Python slim
FROM python:3.10-slim

# Variabili ambiente Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta la working directory
WORKDIR /app

# Aggiorna pip e installa le dipendenze Python
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia il progetto
COPY . /app/

# Esponi porta Django (sviluppo)
EXPOSE 3000

# Comando per avviare Django in sviluppo
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
