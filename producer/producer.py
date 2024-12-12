import asyncio
import json
import os
import mysql.connector
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


# List of stock symbols to track
stock_symbols = ['AAPL', 'GOOGL', 'MSFT']

# MySQL Configuration
DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'stock_data')


class StockDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=json_serializer).encode('utf-8')
        )
        
        self.connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        self.cursor = self.connection.cursor()

    def fetch_and_send_stock_data(self):
        for symbol in stock_symbols:
            # Fetch stock data
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d', interval='1m')
            if not data.empty:
                # Convert DataFrame to dict with proper serialization
                latest_data = data.tail(1).reset_index().to_dict('records')[0]

                # Convert Timestamp to string
                if 'Date' in latest_data:
                    latest_data['Date'] = latest_data['Date'].isoformat()


                message = {'symbol': symbol, 'data': latest_data}

                # Send data to Kafka
                self.producer.send(TOPIC_NAME, message)
                print(f"Sent data for {symbol}: {message}")
    
    # Prepend DB with data for the last year to be able to build predictions
    def add_initial_stock_data(self):
        check_query = "SELECT COUNT(*) FROM stock_prices"
        
        self.cursor.execute(check_query)
        
        result = self.cursor.fetchone()
        
        print(f"Number of rows in stock_prices: {result[0]}")
        
        # If the table is empty, add data
        if result[0] == 0:
            for symbol in stock_symbols:
                stock = yf.Ticker(symbol)
                # Fetch stock data for the last month 
                data = stock.history(period='max', interval='1m')
                
                for _, row in data.iterrows():
                    insert_query = """
                    INSERT INTO stock_prices 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    values = (
                        symbol,
                        row.name,
                        row['Open'],
                        row['High'],
                        row['Low'],
                        row['Close'],
                        row['Volume']
                    )
                    
                    self.cursor.execute(insert_query, values)
                    self.connection.commit()
        
stock_data_producer = StockDataProducer()    
    
async def run_fetch_and_send_stock_data():    
    while True:
        try:
            stock_data_producer.fetch_and_send_stock_data()
            # Fetch data every minute
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    stock_data_producer.add_initial_stock_data()
    
    asyncio.run(run_fetch_and_send_stock_data())
