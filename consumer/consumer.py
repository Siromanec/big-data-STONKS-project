from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
import os
import psycopg2

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
SPARK_MASTER_URL = os.getenv('SPARK_MASTER_URL', 'spark://spark:7077')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('DB_NAME', 'your_db')
DB_USER = os.getenv('DB_USER', 'your_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("StockDataConsumer") \
    .master("spark://spark:7077") \
    .config("spark.driver.host", "consumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema for incoming JSON data
schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("data", StructType([
        StructField("Open", DoubleType(), True),
        StructField("High", DoubleType(), True),
        StructField("Low", DoubleType(), True),
        StructField("Close", DoubleType(), True),
        StructField("Volume", DoubleType(), True),
        StructField("Datetime", TimestampType(), True),
    ]), True)
])

# Read data from Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", "stock_data") \
    .option("startingOffsets", "latest") \
    .load()

# Convert the binary 'value' column to string
df = df.selectExpr("CAST(value AS STRING) as json_str")

# Parse JSON data
json_df = df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

# Flatten the nested 'data' struct
flattened_df = json_df.select(
    col("symbol"),
    col("data.Open").alias("open"),
    col("data.High").alias("high"),
    col("data.Low").alias("low"),
    col("data.Close").alias("close"),
    col("data.Volume").alias("volume"),
    col("data.Datetime").alias("date")
)

# Define the function to write each batch to the database
def write_to_db(df, epoch_id):
    # Convert Spark DataFrame to Pandas DataFrame
    pandas_df = df.toPandas()
    if not pandas_df.empty:
        # Database connection parameters
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        for index, row in pandas_df.iterrows():
            insert_query = """
            INSERT INTO stock_prices (symbol, open, high, low, close, volume, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                row['symbol'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row['date']
            ))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Batch {epoch_id} written to database")

# Write stream to the database
query = flattened_df.writeStream \
    .foreachBatch(write_to_db) \
    .start()

query.awaitTermination()