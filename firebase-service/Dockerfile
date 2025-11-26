FROM python:3.11-slim

WORKDIR /app

COPY firebase-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY firebase-service/app/ /app/app/
COPY services/database/ /app/services/database/
COPY firebase-key.json /app/firebase-key.json

ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["python", "-m", "uvicorn", "app.firebase_server:app", "--host", "0.0.0.0", "--port", "8002"]

