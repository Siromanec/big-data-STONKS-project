import os
from typing import Literal

import sqlalchemy as sa
from sqlalchemy import Table, MetaData

AVAILABLE_STOCKS = Literal["AAPL", "GOOGL", "MSFT"]

# MySQL Configuration
DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv("DB_NAME", 'stock_data')

engine = sa.create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}")
# Reflect the table from the database
metadata = MetaData()
stock_prices_table = Table('stock_prices', metadata, autoload_with=engine)


def get_data(stock: AVAILABLE_STOCKS) -> sa.engine.result.Result:
    with engine.connect() as connection:
        query = sa.select(stock_prices_table).where(stock_prices_table.c.symbol == stock)
        result = connection.execute(query)
        return result


def data_to_dict(data_query_result: sa.engine.result.Result) -> dict:
    data = data_query_result.fetchall()
    zip_data = list(zip(*data))
    return {
        "id": zip_data[0],
        "symbol": zip_data[1],
        "open": zip_data[2],
        "high": zip_data[3],
        "low": zip_data[4],
        "close": zip_data[5],
        "volume": zip_data[6],
        "date": zip_data[7],

    }
