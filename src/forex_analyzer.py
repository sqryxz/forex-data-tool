import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests

class ForexAnalyzer:
    def __init__(self, data_dir="data", api_key=None):
        self.data_dir = data_dir
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch_crypto_data(self, symbol="BTC", market="USD"):
        """Fetch cryptocurrency data from Alpha Vantage"""
        if not self.api_key:
            return None
            
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Time Series (Digital Currency Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Digital Currency Daily)"], orient="index")
                df.index = pd.to_datetime(df.index)
                # Use closing price in USD
                df = df["4a. close (USD)"].astype(float)
                return df
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto data: {e}")
            return None
    
    def load_currency_data(self, from_currency, to_currency):
        """Load forex data from CSV file"""
        filename = f"{self.data_dir}/{from_currency}_{to_currency}_daily.csv"
        if not os.path.exists(filename):
            return None
        
        df = pd.read_csv(filename, index_col=0, parse_dates=True)
        return df
    
    def calculate_daily_stats(self, df, days=7):
        """Calculate daily statistics for the last N days"""
        if df is None or df.empty:
            return None
            
        cutoff_date = df.index.max() - pd.Timedelta(days=days)
        recent_data = df.loc[df.index > cutoff_date]
        
        stats = {
            "mean_price": recent_data["close"].mean(),
            "std_dev": recent_data["close"].std(),
            "high": recent_data["high"].max(),
            "low": recent_data["low"].min(),
            "volatility": recent_data["close"].pct_change().std() * np.sqrt(252),  # Annualized volatility
            "daily_returns": recent_data["close"].pct_change().mean() * 100
        }
        
        return stats
    
    def calculate_crypto_correlation(self, forex_data, crypto_data, window=30):
        """Calculate rolling correlation between forex and crypto returns"""
        if forex_data is None or crypto_data is None or forex_data.empty or crypto_data.empty:
            return None
            
        # Align data on same dates and calculate returns
        common_dates = forex_data.index.intersection(crypto_data.index)
        if len(common_dates) < window:
            return None
            
        forex_returns = forex_data.loc[common_dates, "close"].pct_change()
        crypto_returns = crypto_data.loc[common_dates].pct_change()
        
        # Calculate rolling correlation
        correlation = forex_returns.rolling(window=window).corr(crypto_returns)
        
        return {
            "current_correlation": correlation.iloc[-1],
            "avg_correlation": correlation.mean(),
            "correlation_trend": "increasing" if correlation.iloc[-1] > correlation.mean() else "decreasing"
        }
    
    def detect_arbitrage_opportunities(self, currency_pairs):
        """
        Detect potential arbitrage opportunities across currency pairs
        Example: EUR/USD vs (EUR/GBP * GBP/USD)
        """
        opportunities = []
        
        # Load latest data for all pairs
        pair_rates = {}
        for base, quote in currency_pairs:
            df = self.load_currency_data(base, quote)
            if df is not None:
                pair_rates[f"{base}/{quote}"] = df["close"].iloc[-1]
        
        # Check for triangular arbitrage
        if "EUR/USD" in pair_rates and "GBP/USD" in pair_rates and "EUR/GBP" in pair_rates:
            direct = pair_rates["EUR/USD"]
            indirect = pair_rates["EUR/GBP"] * pair_rates["GBP/USD"]
            
            # If difference is more than 0.1%
            if abs((direct/indirect - 1) * 100) > 0.1:
                opportunities.append({
                    "type": "triangular",
                    "pairs": ["EUR/USD", "EUR/GBP", "GBP/USD"],
                    "direct_rate": direct,
                    "indirect_rate": indirect,
                    "difference_pct": (direct/indirect - 1) * 100
                })
        
        return opportunities
    
    def generate_summary_report(self, currency_pairs, days=7):
        """Generate a summary report for all currency pairs"""
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": f"Last {days} days",
            "currency_analysis": {},
            "crypto_correlations": {},
            "arbitrage_opportunities": []
        }
        
        # Fetch Bitcoin data for correlation analysis
        btc_data = self.fetch_crypto_data()
        
        # Analyze each currency pair
        for base, quote in currency_pairs:
            df = self.load_currency_data(base, quote)
            if df is not None:
                stats = self.calculate_daily_stats(df, days)
                if stats:
                    report["currency_analysis"][f"{base}/{quote}"] = stats
                    
                # Calculate crypto correlation if BTC data is available
                if btc_data is not None:
                    correlation = self.calculate_crypto_correlation(df, btc_data)
                    if correlation:
                        report["crypto_correlations"][f"{base}/{quote}"] = correlation
        
        # Check for arbitrage opportunities
        opportunities = self.detect_arbitrage_opportunities(currency_pairs)
        if opportunities:
            report["arbitrage_opportunities"] = opportunities
        
        return report
    
    def plot_currency_trends(self, from_currency, to_currency, days=30):
        """Generate an interactive plot of currency trends"""
        df = self.load_currency_data(from_currency, to_currency)
        if df is None:
            return None
            
        cutoff_date = df.index.max() - pd.Timedelta(days=days)
        recent_data = df.loc[df.index > cutoff_date]
        
        # Create main candlestick chart
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=recent_data.index,
            open=recent_data['open'],
            high=recent_data['high'],
            low=recent_data['low'],
            close=recent_data['close'],
            name=f"{from_currency}/{to_currency}"
        ))
        
        # Add Bitcoin price if available
        btc_data = self.fetch_crypto_data()
        if btc_data is not None:
            btc_recent = btc_data[btc_data.index > cutoff_date]
            if not btc_recent.empty:
                # Normalize BTC price to fit on the same scale
                btc_normalized = btc_recent * (recent_data['close'].mean() / btc_recent.mean())
                fig.add_trace(go.Scatter(
                    x=btc_recent.index,
                    y=btc_normalized,
                    name="BTC (normalized)",
                    line=dict(color='orange', dash='dash')
                ))
        
        fig.update_layout(
            title=f'{from_currency}/{to_currency} vs BTC - Last {days} Days',
            yaxis_title=f'Price ({to_currency})',
            xaxis_title='Date',
            legend_title="Assets"
        )
        
        # Save the plot as HTML
        output_file = f"{self.data_dir}/{from_currency}_{to_currency}_trend.html"
        fig.write_html(output_file)
        return output_file

# Example usage
if __name__ == "__main__":
    analyzer = ForexAnalyzer()
    
    # Example currency pairs
    currency_pairs = [
        ("EUR", "USD"),
        ("GBP", "USD"),
        ("JPY", "USD"),
        ("AUD", "USD")
    ]
    
    # Generate summary report
    report = analyzer.generate_summary_report(currency_pairs)
    
    # Print report
    print("\nForex Market Summary Report")
    print("=" * 50)
    print(f"Generated at: {report['timestamp']}")
    print(f"Period: {report['period']}")
    
    print("\nCurrency Pair Analysis:")
    for pair, stats in report['currency_analysis'].items():
        print(f"\n{pair}:")
        print(f"  Mean Price: {stats['mean_price']:.4f}")
        print(f"  Volatility: {stats['volatility']:.2f}%")
        print(f"  Daily Returns: {stats['daily_returns']:.2f}%")
        
    if report['arbitrage_opportunities']:
        print("\nPotential Arbitrage Opportunities:")
        for opp in report['arbitrage_opportunities']:
            print(f"\nType: {opp['type']}")
            print(f"Pairs involved: {', '.join(opp['pairs'])}")
            print(f"Difference: {opp['difference_pct']:.2f}%")
    
    # Generate plots for each currency pair
    for base, quote in currency_pairs:
        plot_file = analyzer.plot_currency_trends(base, quote)
        if plot_file:
            print(f"\nGenerated trend plot: {plot_file}") 