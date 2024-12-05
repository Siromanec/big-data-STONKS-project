from typing import Callable, Literal
from repository import AVAILABLE_STOCKS
import fbprophet
import arima

PREDICTION_METHODS = Literal["fbprophet", "arima", "lstm"]


def fbprophet_predict():
    pass
def arima_predict():
    pass
def lstm_predict():
    pass

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
