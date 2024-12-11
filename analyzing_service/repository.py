from typing import Literal

import sqlalchemy as sa
AVAILABLE_STOCKS = Literal["AAPL", "GOOGL", "MSFT"]

def get_data(stock: AVAILABLE_STOCKS):
    engine = sa.create_engine("mysql+psycopg2://user:password@db:3306/stock_data")
    connection = engine.connect()
    query = f"SELECT * FROM stock_prices WHERE symbol = '{stock}'"
    result = connection.execute(query)
    return result.fetchall()