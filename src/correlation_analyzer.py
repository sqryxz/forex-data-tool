import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CorrelationAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir

    def load_data(self, symbol_pair):
        """Load data for a given symbol pair"""
        filename = f"{self.data_dir}/{symbol_pair}_daily.csv"
        if os.path.exists(filename):
            return pd.read_csv(filename, index_col=0, parse_dates=True)
        return None

    def calculate_correlations(self, base_pairs, crypto_pair="BTC_USD"):
        """Calculate correlations between crypto and forex pairs"""
        # Load crypto data
        crypto_df = self.load_data(crypto_pair)
        if crypto_df is None:
            raise ValueError(f"No data found for {crypto_pair}")

        correlations = {}
        price_data = {}
        
        # Store crypto data
        price_data[crypto_pair] = crypto_df['close']

        # Load and calculate correlations for each forex pair
        for pair in base_pairs:
            pair_str = f"{pair[0]}_{pair[1]}"
            forex_df = self.load_data(pair_str)
            
            if forex_df is not None:
                price_data[pair_str] = forex_df['close']
                
                # Calculate correlation
                combined_df = pd.DataFrame({
                    'crypto': crypto_df['close'],
                    'forex': forex_df['close']
                }).dropna()
                
                if not combined_df.empty:
                    correlation = combined_df['crypto'].corr(combined_df['forex'])
                    correlations[pair_str] = correlation

        return correlations, price_data

    def plot_correlations(self, correlations, price_data, output_dir="data"):
        """Create correlation plots and price comparisons"""
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create correlation bar plot
        fig1 = go.Figure(data=[
            go.Bar(
                x=list(correlations.keys()),
                y=list(correlations.values()),
                text=[f"{v:.2f}" for v in correlations.values()],
                textposition='auto',
            )
        ])
        
        fig1.update_layout(
            title="Correlation between Bitcoin and Forex Pairs",
            xaxis_title="Forex Pair",
            yaxis_title="Correlation Coefficient",
            yaxis=dict(range=[-1, 1])
        )
        
        # Save correlation plot
        fig1.write_html(f"{output_dir}/correlations.html")

        # Create price comparison plots
        crypto_pair = [k for k in price_data.keys() if k.startswith('BTC')][0]
        crypto_prices = price_data[crypto_pair]
        
        # Create subplots for price comparisons
        n_pairs = len(price_data) - 1
        fig2 = make_subplots(rows=n_pairs, cols=1, 
                           subplot_titles=[k for k in price_data.keys() if k != crypto_pair])

        # Add crypto price as a trace to each subplot
        for i, (pair, prices) in enumerate(price_data.items()):
            if pair == crypto_pair:
                continue
                
            row = i + 1
            
            # Normalize prices to compare trends
            crypto_norm = (crypto_prices - crypto_prices.mean()) / crypto_prices.std()
            forex_norm = (prices - prices.mean()) / prices.std()
            
            fig2.add_trace(
                go.Scatter(x=crypto_prices.index, y=crypto_norm, name=f"{crypto_pair} (normalized)",
                          line=dict(color='blue')), row=row, col=1)
            fig2.add_trace(
                go.Scatter(x=prices.index, y=forex_norm, name=f"{pair} (normalized)",
                          line=dict(color='red')), row=row, col=1)

        fig2.update_layout(height=300*n_pairs, title_text="Normalized Price Comparisons")
        fig2.write_html(f"{output_dir}/price_comparisons.html")

if __name__ == "__main__":
    # Example usage
    analyzer = CorrelationAnalyzer()
    
    currency_pairs = [
        ("EUR", "USD"),
        ("GBP", "USD"),
        ("JPY", "USD"),
        ("AUD", "USD")
    ]
    
    correlations, price_data = analyzer.calculate_correlations(currency_pairs)
    analyzer.plot_correlations(correlations, price_data) 