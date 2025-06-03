FROM python:3.10-slim

WORKDIR /app

COPY pdp.py ./
COPY .env ./
COPY splunk_methods.py ./
COPY encrypt_existing.py ./
RUN pip install flask requests cryptography python-dotenv
CMD ["python", "pdp.py"]
