import yfinance as yf
from kafka import KafkaProducer
import json
import time
import os
import pandas as pd

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

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
    while True:
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
                producer.send('stock_data', message)
                print(f"Sent data for {symbol}: {message}")
        
        # Fetch data every minute
        time.sleep(60)

if __name__ == '__main__':
    fetch_and_send_stock_data()