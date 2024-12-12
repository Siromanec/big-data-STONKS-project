import asyncio

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from aiohttp import ClientSession


def plot_prediction(historical_data, predictions, plot_running_window=True, title=None, window_size=24,
                    return_figure=False):
    """
    Plot predictions and historical data for the series.

    Parameters:
        historical_data (pd.Series): Time series of historical data (indexed by datetime).
        predictions (pd.Series): Time series of predicted data (indexed by datetime).
        plot_running_window (bool): Whether to plot a running average for historical data.
        title (str): Title of the plot.
        window_size (int): Size of the running average window.
        return_figure (bool): If True, returns the figure object instead of showing it.

    Returns:
        plotly.graph_objects.Figure: The figure object, if return_figure is True.
    """
    if not isinstance(historical_data, pd.Series) or not isinstance(predictions, pd.Series):
        raise ValueError("historical_data and predictions must be pandas Series objects indexed by datetime.")

    if not isinstance(historical_data.index, pd.DatetimeIndex) or not isinstance(predictions.index, pd.DatetimeIndex):
        raise ValueError("Both historical_data and predictions must be indexed by pd.DatetimeIndex.")

    fig = go.Figure()

    # Plot historical data
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data.values,
        mode='lines',
        name='Historical Data',
        line=dict(color='steelblue')
    ))

    # Plot predictions
    fig.add_trace(go.Scatter(
        x=predictions.index,
        y=predictions.values,
        mode='lines',
        name='Predictions',
        line=dict(color='red', dash='dot')
    ))

    # Add a running average window of the historical data
    if plot_running_window:
        running_average = historical_data.rolling(window=window_size).mean()
        fig.add_trace(go.Scatter(
            x=running_average.index,
            y=running_average.values,
            mode='lines',
            name=f'{window_size}-hour Running Average',
            line=dict(color='rgba(144, 244, 144, 0.9)', dash='dash')
        ))

    # Plot layout
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Price",
        legend_title="Legend",
        template="plotly_white",
        plot_bgcolor="whitesmoke",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )

    if return_figure:
        return fig
    else:
        fig.show()


async def main():
    async with ClientSession() as session:
        async with session.get('http://localhost:8000/predict?method=fbprophet&stock=AAPL&period=10') as response:
            prediction = (await response.json())
        async with session.get('http://localhost:8000/get_data?stock=AAPL') as response:
            history = (await response.json())

    historical_data = pd.Series(data=np.mean([history["low"], history["high"], history["close"]], axis=0),
                                index=[pd.Timestamp(i) for i in history["date"]])

    predictions = pd.Series(data=prediction["forecast"], index=[pd.Timestamp(i) for i in prediction["dates"]])

    plot_prediction(historical_data, predictions, plot_running_window=True, title="Example", window_size=24,
                    return_figure=False)

    # Example usage
if __name__ == "__main__":
    asyncio.run(main())

    # fig = plot_prediction(historical_data, predictions, plot_running_window=True, title="Example", window_size=24, return_figure=True)
    # fig.write_image("plot.png")
