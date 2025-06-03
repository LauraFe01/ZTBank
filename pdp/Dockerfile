FROM python:3.10-slim

WORKDIR /app

COPY pdp.py ./
COPY .env ./
COPY utils.py ./
COPY splunk_methods.py ./
COPY encrypt_existing.py ./
COPY data/GeoLite2-Country.mmdb ./
COPY data/trust_db.json ./

RUN pip install flask requests cryptography python-dotenv geoip2
CMD ["python", "pdp.py"]