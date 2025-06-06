FROM python:3.10-slim


# directory di lavoro
WORKDIR /app


# copia i file all'interno della directory del container
COPY pep.py .
COPY user_auth.py .
COPY users_db.json .
COPY create_users.py .
COPY . .


# Installa le dipendenze necessarie
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install flask requests psycopg2-binary pytz bcrypt cryptography python-dotenv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# avvio   
CMD ["python", "pep.py"]