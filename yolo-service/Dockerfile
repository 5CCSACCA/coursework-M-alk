FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY yolo-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY yolo-service/app/ /app/app/
COPY yolo-service/model/ /app/model/

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "app.yolo_server:app", "--host", "0.0.0.0", "--port", "8001"]

