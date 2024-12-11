from typing import Annotated, Callable

import fastapi
from fastapi import Depends

from repository import AVAILABLE_STOCKS
from repository import get_data, data_to_dict
from service import get_method

router = fastapi.APIRouter()


@router.get("/predict")
async def predict(stock: AVAILABLE_STOCKS,
                  method: Annotated[Callable, Depends(get_method)],
                  period: Annotated[int, fastapi.Query(lt=40)],
                  max_history: Annotated[int, fastapi.Query(gt=20)] = None,
                  order: Annotated[tuple[int, int, int], fastapi.Query] = None):
    # predict stock price
    data_dict = data_to_dict(get_data(stock))

    dates, forecast = method(data_dict, period, max_history, order=order)
    dates = [str(date) for date in dates]
    forecast = [float(prediction) for prediction in forecast]

    return {"stock": stock, "dates": dates, "forecast": forecast, "method": method.__name__, "period": period,
            "max_history": max_history}


@router.get("/get_data")
async def get_stock_data(stock: AVAILABLE_STOCKS):
    return data_to_dict(get_data(stock))
