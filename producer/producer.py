import asyncio
import json
import os

import pandas as pd
import yfinance as yf
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC_NAME = 'stock_data_topic'


# Custom JSON encoder to handle Pandas Timestamp
def json_serializer(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v, default=json_serializer).encode('utf-8')
)

# List of stock symbols to track
stock_symbols = ['AAPL', 'GOOGL', 'MSFT']


def fetch_and_send_stock_data():
    for symbol in stock_symbols:
        # Fetch stock data
        stock = yf.Ticker(symbol)
        data = stock.history(period='1m')
        if not data.empty:
            # Convert DataFrame to dict with proper serialization
            latest_data = data.tail(1).reset_index().to_dict('records')[0]

            # Convert Timestamp to string
            if 'Date' in latest_data:
                latest_data['Date'] = latest_data['Date'].isoformat()

            message = {'symbol': symbol, 'data': latest_data}

            # Send data to Kafka
            producer.send(TOPIC_NAME, message)
            print(f"Sent data for {symbol}: {message}")


async def run_fetch_and_send_stock_data():
    while True:
        try:
            fetch_and_send_stock_data()
            # Fetch data every minute
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    asyncio.run(run_fetch_and_send_stock_data())
