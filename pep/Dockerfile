FROM python:3.10-slim

WORKDIR /app
COPY pep.py .

RUN pip install flask requests

CMD ["python", "pep.py"]