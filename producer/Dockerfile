FROM python:3.9-slim

WORKDIR /app

COPY producer.py ./

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ARG KAFKA_BOOTSTRAP_SERVERS

CMD ["python", "producer.py"]