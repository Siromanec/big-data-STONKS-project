from typing import Callable, Literal
from repository import AVAILABLE_STOCKS

PREDICTION_METHODS = Literal["fbprophet", "arima", "lstm"]

DEFAULT_PREDICTION = [1, 2, 3, 4, 5]

def fbprophet_predict(data):
    return DEFAULT_PREDICTION
def arima_predict(data):
    return DEFAULT_PREDICTION
def lstm_predict(data):
    return DEFAULT_PREDICTION

def get_method(method: PREDICTION_METHODS) -> Callable:
    match method:
        case "fbprophet":
            return fbprophet_predict
        case "arima":
            return arima_predict
        case "lstm":
            return lstm_predict
        case _:
            raise ValueError("Invalid method")
