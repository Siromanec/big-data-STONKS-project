from typing import Literal

import sqlalchemy as sa
from sqlalchemy import Table, MetaData

AVAILABLE_STOCKS = Literal["AAPL", "GOOGL", "MSFT"]

engine = sa.create_engine("mysql+pymysql://user:password@localhost:3306/stock_data")
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
    zip_data = zip(*data)
    return {
        "symbol": zip_data[0],
        "open": zip_data[1],
        "high": zip_data[1],
        "low": zip_data[3],
        "close": zip_data[4],
        "volume": zip_data[5],
        "date": zip_data[6],

    }
