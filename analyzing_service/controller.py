from typing import Annotated, Callable

import fastapi
from fastapi import Depends

from .repository import get_data
from .service import AVAILABLE_STOCKS, get_method

router = fastapi.APIRouter()


@router.get("/predict")
async def predict(stock: AVAILABLE_STOCKS, method: Annotated[Callable, Depends(get_method)]):
    # predict stock price
    data = get_data(stock, "2021-01-01", "2021-12-31")
    prediction = method(data)
    return {"prediction": prediction}

@router.get("/get_data")
async def get_stock_data(stock: AVAILABLE_STOCKS, start_date: str, end_date: str):
    return get_data(stock, start_date, end_date)
