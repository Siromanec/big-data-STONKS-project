from typing import Annotated, Callable

import fastapi
from fastapi import Depends

from .repository import get_data
from .service import AVAILABLE_STOCKS, get_method

router = fastapi.APIRouter()


@router.get("/predict")
async def predict(stock: AVAILABLE_STOCKS,
                  method: Annotated[Callable, Depends(get_method)],
                  period: Annotated[int, fastapi.Query(lt=40)]):
    # predict stock price
    data = get_data(stock)
    prediction = method(data, period)
    return {"prediction": prediction}

@router.get("/get_data")
async def get_stock_data(stock: AVAILABLE_STOCKS):
    return get_data(stock)
