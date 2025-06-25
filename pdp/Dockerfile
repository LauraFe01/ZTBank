FROM python:3.10-slim

WORKDIR /app

COPY pdp.py ./
COPY .env ./
COPY utils.py ./
COPY policies.py ./
COPY encrypt_existing.py ./
COPY data/GeoLite2-Country.mmdb ./
COPY data/trust_db.json ./
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

RUN pip install flask requests cryptography python-dotenv geoip2

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "pdp.py"]
