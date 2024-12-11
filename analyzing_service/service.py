import datetime
from typing import Callable, Literal, Sequence

import numpy as np
import pandas as pd
import prophet
from statsmodels.tsa.arima.model import ARIMA

PREDICTION_METHODS = Literal["fbprophet", "arima"]

DEFAULT_PREDICTION = [1, 2, 3, 4, 5]


def preprocess_data(func: Callable) -> Callable:
    def preprocess_data_wrapper(data: dict, period: int) -> tuple[Sequence[float], Sequence]:
        x, y, exog = data["date"], np.mean([data["low"], data["high"], data["close"]], axis=0), data["volume"]

        return func(x, y, period)
    return preprocess_data_wrapper

@preprocess_data
def fbprophet_predict(x: Sequence[float], y: Sequence, exog, period: int) -> tuple[
    Sequence[datetime.datetime], Sequence[float]]:
    prophet_model = prophet.Prophet()

    x = pd.date_range(start='1/1/2020', periods=len(y), freq="1m") # FIXME: This is a placeholder

    prophet_model.fit(pd.DataFrame({'ds': x, 'y': y}))
    future = prophet_model.make_future_dataframe(periods=period, freq="1m")
    forecast = prophet_model.predict(future)

    return forecast['ds'].tail(period).values, forecast['yhat'].tail(period).values

@preprocess_data
def arima_predict(x: Sequence[float], y: Sequence, exog, period: int) -> tuple[
    Sequence[datetime.datetime], Sequence[float]]:
    # Fit the ARIMA model
    order = (4, 2, 40)  # Adjust this based on model performance
    x = pd.date_range(start='1/1/2020', periods=len(y), freq="1m") # FIXME: This is a placeholder

    model = ARIMA(y, order=order, dates=x, exog=[exog])
    fitted_model = model.fit()
    forecast = fitted_model.forecast(steps=period)
    x_future = pd.date_range(start=x[-1], periods=period, freq="1m")

    return x_future, forecast


def get_method(method: PREDICTION_METHODS) -> Callable:
    match method:
        case "fbprophet":
            return fbprophet_predict
        case "arima":
            return arima_predict
        case _:
            raise ValueError("Invalid method")
