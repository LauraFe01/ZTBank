FROM python:3.10-slim

WORKDIR /app
COPY pep.py .

# Installa le dipendenze necessarie
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install flask requests python-dotenv psycopg2-binary && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["python", "pep.py"]