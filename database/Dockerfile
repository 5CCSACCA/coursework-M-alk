FROM python:3.11-slim

WORKDIR /app

COPY database/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY database/ /app/database/

ENV PYTHONPATH=/app

