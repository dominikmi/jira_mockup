FROM python:3.12-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik requirements.txt do katalogu roboczego
COPY requirements.txt /app/

# Zainstaluj zależności
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip3 install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj resztę plików aplikacji do katalogu roboczego
COPY . /app

# Ustaw zmienną środowiskową dla Flask
ENV FLASK_APP=jira-api-mock.py

# Otwórz port 5000
EXPOSE 5000

# Utwórz punkt montowania dla katalogu danych
VOLUME ["/app/data"]

# Uruchom aplikację za pomocą Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "jira-api-mock:app"]