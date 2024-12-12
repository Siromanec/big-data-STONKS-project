import asyncio

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from aiohttp import ClientSession
from sklearn.linear_model import LinearRegression


def plot_prediction(historical_data, predictions, plot_running_window=True, plot_trend_line=True, title=None, window_size=60,
                    return_figure=False):
    """
    Plot predictions and historical data for the series.

    Parameters:
        historical_data (pd.Series): Time series of historical data (indexed by datetime).
        predictions (pd.Series): Time series of predicted data (indexed by datetime).
        plot_running_window (bool): Whether to plot a running average for historical data.
        plot_trend_line (bool): Whether to plot a trend for historical data.
        title (str): Title of the plot.
        window_size (int): Size of the running average window in minutes.
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
            name=f'{window_size}-minute Running Average',
            line=dict(color='rgba(144, 244, 144, 0.9)', dash='dash')
        ))

    # Add a trend line of the last 12 hours of historical data
    if plot_trend_line:
        last_timestamp = historical_data.index[-1]
        start_timestamp = last_timestamp - pd.Timedelta(minutes=720)
        if len(historical_data) > 720:
            last_12_hours = historical_data.loc[start_timestamp:last_timestamp]
        else:
            last_12_hours = historical_data
        if not last_12_hours.empty:
            x = (last_12_hours.index - last_12_hours.index[0]).total_seconds().values.reshape(-1, 1)
            y = last_12_hours.values.reshape(-1, 1)

            model = LinearRegression()
            model.fit(x, y)

            trend_x = (historical_data.index - last_12_hours.index[0]).total_seconds().values.reshape(-1, 1)
            trend_y = model.predict(trend_x)

            fig.add_trace(go.Scatter(
                x=last_12_hours.index,
                y=trend_y.flatten(),
                mode='lines',
                name='Trend Line',
                line=dict(color='rgba(128, 0, 128, 0.9)')
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
    app = Dash()

    # App layout
    app.layout = html.Div([
        html.Div(children='Predicting Stock Price'),
        html.Hr(),
        dcc.Dropdown(
            id='dropdown-placeholder',
            options=[
                {'label': 'AAPL', 'value': 'AAPL'},
                {'label': 'GOOGL', 'value': 'GOOGL'},
                {'label': 'MSFT', 'value': 'MSFT'}
            ],
        ),
        dcc.RadioItems(
            id='radio-buttons',
            options=[
                {'label': 'ARIMA', 'value': 'arima'},
                {'label': 'prophet', 'value': 'prophet'}
            ],
        ),
        dcc.Graph(figure={}, id='controls-and-graph')
    ])

    @callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    [
        Input(component_id='dropdown-placeholder', component_property='value'),
        Input(component_id='radio-buttons', component_property='value')
    ])
    def update_graph(dropdown_value, radio_value):
        async with ClientSession() as session:
            async with session.get(f'http://localhost:8000/predict?method={radio_value}&stock={dropdown_value}&period=99', json=[4, 1, 20]) as response:
                prediction = (await response.json())
                if response.status != 200:
                    raise ValueError(await response.text())
            async with session.get(f'http://localhost:8000/get_data?stock={dropdown_value}') as response:
                if response.status != 200:
                    raise ValueError(await response.text())
                history = (await response.json())
    
        historical_data = pd.Series(data=np.mean([history["low"], history["high"], history["close"]], axis=0),
                                    index=[pd.Timestamp(i) for i in history["date"]])
        predictions = pd.Series(data=prediction["forecast"], index=[pd.Timestamp(i) for i in prediction["dates"]])
    
        plot_prediction(historical_data,
                        predictions,
                        plot_running_window=True,
                        plot_trend_line=True,
                        title=f"Predicting {dropdown_value} with {radio_value}",
                        window_size=60,
                        return_figure=False)

if __name__ == "__main__":
    asyncio.run(main())
