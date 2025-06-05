# Utilizza un'immagine base leggera di Python 3.10
FROM python:3.10-slim

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia tutti i file del progetto nella directory di lavoro
COPY . .

# Aggiorna i pacchetti e installa le dipendenze di sistema necessarie
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installa le dipendenze Python necessarie per l'applicazione
RUN pip install --no-cache-dir \
    flask \
    requests \
    psycopg2-binary \
    pytz \
    bcrypt \
    cryptography \
    python-dotenv

# Definisce il comando di default per eseguire l'applicazione
CMD ["python", "pep.py"]
