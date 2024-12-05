from typing import Literal

import sqlalchemy as sa
AVAILABLE_STOCKS = Literal["AAPL", "GOOGL", "MSFT"]
def get_data(stock: AVAILABLE_STOCKS, start_date: str, end_date: str):
    engine = sa.create_engine("sqlite:///data.db")
    connection = engine.connect()
    query = f"SELECT * FROM {stock} WHERE date BETWEEN '{start_date}' AND '{end_date}'"
    result = connection.execute(query)
    return result.fetchall()