from typing import Annotated, Callable

import fastapi
from fastapi import Depends

from .repository import get_data
from .service import AVAILABLE_STOCKS, get_method

router = fastapi.APIRouter()


@router.get("/predict")
def predict(stock: AVAILABLE_STOCKS, method: Annotated[Callable, Depends(get_method)]):
    # predict stock price
    data = get_data(stock, "2021-01-01", "2021-12-31")
    prediction = method(data)
    return {"stock": stock, "data": data, "prediction": prediction, "method": method.__name__}
