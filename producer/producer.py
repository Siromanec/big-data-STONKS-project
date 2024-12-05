import yfinance as yf
from kafka import KafkaProducer
import json
import time
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# List of stock symbols to track
stock_symbols = ['AAPL', 'GOOGL', 'MSFT']

def fetch_and_send_stock_data():
    while True:
        for symbol in stock_symbols:
            # Fetch stock data
            stock = yf.Ticker(symbol)
            data = stock.history(period='1m')
            if not data.empty:
                latest_data = data.tail(1).reset_index().to_dict('records')[0]
                message = {'symbol': symbol, 'data': latest_data}
                # Send data to Kafka
                producer.send('stock_data', message)
                print(f"Sent data for {symbol}: {message}")
        # Fetch data every minute
        time.sleep(60)

if __name__ == '__main__':
    fetch_and_send_stock_data()
    
    