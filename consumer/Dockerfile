FROM python:3.9-slim

WORKDIR /app

COPY consumer.py ./

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


ARG KAFKA_BOOTSTRAP_SERVERS
ARG SPARK_MASTER_URL
ARG DB_HOST
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD

CMD ["python", "consumer.py"]


# ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
# ENV SPARK_MASTER_URL=spark://spark:7077
# ENV DB_HOST=db
# ENV DB_NAME=your_db
# ENV DB_USER=your_user
# ENV DB_PASSWORD=your_password