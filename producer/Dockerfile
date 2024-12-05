FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY producer.py ./



ARG KAFKA_BOOTSTRAP_SERVERS

CMD ["python", "producer.py"]