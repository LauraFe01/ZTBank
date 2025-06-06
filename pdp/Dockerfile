FROM python:3.10-slim


# directory di lavoro
WORKDIR /app


# copia i file nella directory del container
COPY pdp.py ./
COPY .env ./
COPY utils.py ./
COPY policies.py ./
COPY encrypt_existing.py ./
COPY data/GeoLite2-Country.mmdb ./
COPY data/trust_db.json ./


# installa le dipendenze necessarie
RUN pip install flask requests cryptography python-dotenv geoip2


# avvio
CMD ["python", "pdp.py"]
