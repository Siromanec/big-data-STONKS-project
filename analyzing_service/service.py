import datetime
from typing import Callable, Literal, Sequence

import numpy as np
import pandas as pd
import prophet
from statsmodels.tsa.arima.model import ARIMA

PREDICTION_METHODS = Literal["fbprophet", "arima"]

DEFAULT_PREDICTION = [1, 2, 3, 4, 5]


def preprocess_data(func: Callable) -> Callable:
    def preprocess_data_wrapper(data: dict, period: int, max_history: int, order) -> tuple[Sequence[float], Sequence]:
        x, y, exog = (data["date"],
                      np.mean(np.array([data["low"], data["high"], data["close"]]), axis=0),
                      data["volume"])

        return func(x, y, period, exog=exog, order=order)
    return preprocess_data_wrapper

@preprocess_data
def fbprophet_predict(x: Sequence[float], y: Sequence, period: int, *args, **kwargs) -> tuple[
    Sequence[datetime.datetime], Sequence[float]]:
    prophet_model = prophet.Prophet(n_changepoints=30,changepoint_range=0.8, daily_seasonality=180)

    x = pd.date_range(start='1/1/2024', periods=len(y), freq="1min") # FIXME: This is a placeholder

    prophet_model.fit(pd.DataFrame({'ds': x, 'y': y}))
    future = prophet_model.make_future_dataframe(periods=period, freq="1min")
    forecast = prophet_model.predict(future)

    return forecast['ds'].tail(period).values, forecast['yhat'].tail(period).values

@preprocess_data
def arima_predict(x: Sequence[float], y: Sequence, period: int, exog=None, order=None, *args, **kwargs) -> tuple[
    Sequence[datetime.datetime], Sequence[float]]:
    # Fit the ARIMA model
    if order is None:
        order = (4, 2, 40)  # Adjust this based on model performance
    x = pd.date_range(start='1/1/2024', periods=len(y), freq="1min") # FIXME: This is a placeholder

    model = ARIMA(y, order=order, dates=x,)
    fitted_model = model.fit()
    forecast = fitted_model.forecast(steps=period)
    x_future = pd.date_range(start=x[-1], periods=period, freq="1min")

    return x_future.values, forecast


def get_method(method: PREDICTION_METHODS) -> Callable:
    match method:
        case "fbprophet":
            return fbprophet_predict
        case "arima":
            return arima_predict
        case _:
            raise ValueError("Invalid method")
