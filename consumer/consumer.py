import os
import json
import mysql.connector
from kafka import KafkaConsumer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka and Database Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC_NAME = 'stock_data_topic'

# MySQL Configuration
DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'stock_data')

class StockDataConsumer:
    def __init__(self):
        # Initialize Kafka Consumer
        self.consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='stock-data-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        # Initialize MySQL Connection
        self.connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        self.cursor = self.connection.cursor()

    def consume_and_save(self):
        logger.info(f"Starting consumer for topic {TOPIC_NAME}")
        
        try:
            for message in self.consumer:
                try:
                    stock_data = message.value
                    symbol = stock_data['symbol']
                    data = stock_data['data']

                    # Prepare SQL query
                    insert_query = """
                    INSERT INTO stock_prices 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                    # Extract values from the data
                    values = (
                        symbol,
                        data.get('Date', None),
                        data.get('Open', None),
                        data.get('High', None),
                        data.get('Low', None),
                        data.get('Close', None),
                        data.get('Volume', None)
                    )

                    # Execute the insert
                    self.cursor.execute(insert_query, values)
                    self.connection.commit()

                    logger.info(f"Saved stock data for {symbol}")

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    self.connection.rollback()

        except Exception as e:
            logger.error(f"Unexpected error in consumer: {e}")

        finally:
            self.cursor.close()
            self.connection.close()

def main():
    consumer = StockDataConsumer()
    consumer.consume_and_save()

if __name__ == '__main__':
    main()