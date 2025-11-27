FROM python:3.11-slim

WORKDIR /app

COPY postprocessing-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY postprocessing-service/app/ /app/app/

ENV PYTHONPATH=/app

CMD ["python", "-m", "app.consumer"]

