FROM python:3.10-slim

WORKDIR /app
COPY pdp.py /app
RUN pip install flask requests
CMD ["python", "pdp.py"]
