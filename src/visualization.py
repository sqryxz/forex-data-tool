import plotly.graph_objects as go
from datetime import datetime
import os

class ChartGenerator:
    def create_candlestick_chart(self, data, base_currency, quote_currency):
        """Create an interactive candlestick chart"""
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close']
        )])
        
        # Update layout
        fig.update_layout(
            title=f'{base_currency}/{quote_currency} Exchange Rate',
            yaxis_title=f'Price ({quote_currency})',
            xaxis_title='Date'
        )
        
        # Save chart
        os.makedirs('data', exist_ok=True)
        filename = f'data/{base_currency}_{quote_currency}_trend.html'
        fig.write_html(filename)