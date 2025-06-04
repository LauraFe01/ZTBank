FROM python:3.10-slim

WORKDIR /app
COPY pep.py .
COPY user_auth.py .
COPY users_db.json .
COPY create_users.py .

# Installa le dipendenze necessarie
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install flask requests psycopg2-binary pytz bcrypt cryptography python-dotenv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["python", "pep.py"]