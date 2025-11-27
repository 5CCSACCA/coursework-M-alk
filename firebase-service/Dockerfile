FROM python:3.11-slim

WORKDIR /app

COPY firebase-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY firebase-service/app/ /app/app/
COPY database/ /app/database/
COPY firebase-key.json /app/firebase-key.json

ENV PYTHONPATH=/app
ENV FIREBASE_CREDENTIALS=/app/firebase-key.json

EXPOSE 8002

CMD ["python", "-m", "uvicorn", "app.firebase_server:app", "--host", "0.0.0.0", "--port", "8002"]

