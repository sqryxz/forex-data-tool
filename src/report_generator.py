import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests

class ReportGenerator:
    def __init__(self, data_dir="data", api_key=None):
        self.data_dir = data_dir
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_crypto_rate(self, from_currency="BTC", to_currency="USD"):
        """Get real-time crypto exchange rate"""
        if not self.api_key:
            print("Warning: No API key provided for crypto rate fetch")
            return None
            
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Realtime Currency Exchange Rate" in data:
                # Save the rate to build trend data
                self.save_crypto_rate(data["Realtime Currency Exchange Rate"])
                return data["Realtime Currency Exchange Rate"]
            return None
            
        except Exception as e:
            print(f"Error fetching crypto rate: {e}")
            return None

    def save_crypto_rate(self, rate_data):
        """Save crypto rate to CSV for trend analysis"""
        filename = f"{self.data_dir}/BTC_USD_trend.csv"
        timestamp = datetime.now()
        
        # Prepare the new row
        new_row = {
            'timestamp': timestamp,
            'rate': float(rate_data['5. Exchange Rate']),
            'bid': float(rate_data['8. Bid Price']),
            'ask': float(rate_data['9. Ask Price']),
            'last_refreshed': rate_data['6. Last Refreshed']
        }
        
        # Load existing data or create new DataFrame
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            # Keep only last 30 days of data
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[df['timestamp'] > (timestamp - timedelta(days=30))]
        else:
            df = pd.DataFrame(columns=['timestamp', 'rate', 'bid', 'ask', 'last_refreshed'])
        
        # Append new data
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(filename, index=False)

    def get_crypto_trend_data(self):
        """Get Bitcoin trend data from stored rates"""
        filename = f"{self.data_dir}/BTC_USD_trend.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df.sort_values('timestamp')
        return None

    def analyze_crypto_trend(self, trend_data):
        """Analyze Bitcoin price trend"""
        if trend_data is None or len(trend_data) < 2:
            return []
            
        analysis = []
        
        # Calculate overall trend
        first_rate = trend_data.iloc[0]['rate']
        last_rate = trend_data.iloc[-1]['rate']
        total_change = ((last_rate - first_rate) / first_rate) * 100
        
        # Determine trend direction
        if total_change > 0:
            trend = "upward"
        elif total_change < 0:
            trend = "downward"
        else:
            trend = "neutral"
            
        analysis.append(f"Bitcoin has shown a {trend} trend over the monitored period with a {abs(total_change):.2f}% {trend} movement.")
        
        # Calculate volatility (standard deviation of returns)
        returns = trend_data['rate'].pct_change().dropna()
        volatility = returns.std() * 100  # Convert to percentage
        
        analysis.append(f"Price volatility is {volatility:.2f}% based on rate changes.")
        
        # Analyze recent movement
        if len(trend_data) > 6:  # If we have enough data points
            recent_change = ((last_rate - trend_data.iloc[-7]['rate']) / trend_data.iloc[-7]['rate']) * 100
            if abs(recent_change) > abs(total_change):
                analysis.append(f"Recent movement is more volatile with a {recent_change:.2f}% change in the last 24 hours.")
            else:
                analysis.append(f"Recent movement is relatively stable with a {recent_change:.2f}% change in the last 24 hours.")
        
        return analysis

    def load_realtime_data(self, from_currency, to_currency):
        """Load real-time data for a currency pair"""
        filename = f"{self.data_dir}/{from_currency}_{to_currency}_realtime.csv"
        if os.path.exists(filename):
            return pd.read_csv(filename, parse_dates=['timestamp'])
        return None

    def load_daily_data(self, from_currency, to_currency):
        """Load daily data for a currency pair"""
        filename = f"{self.data_dir}/{from_currency}_{to_currency}_daily.csv"
        if os.path.exists(filename):
            # Read CSV with unnamed index column
            df = pd.read_csv(filename, index_col=0)
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            return df
        return None

    def generate_market_analysis(self, currency_pairs, realtime_data):
        """Generate written market analysis based on real-time data"""
        analysis = []
        
        # Overall market sentiment
        up_count = 0
        down_count = 0
        for pair_data in realtime_data:
            if pair_data['change_pct'] > 0:
                up_count += 1
            elif pair_data['change_pct'] < 0:
                down_count += 1
        
        # Market sentiment
        total_pairs = len(currency_pairs)
        if up_count > down_count:
            sentiment = "bullish"
        elif down_count > up_count:
            sentiment = "bearish"
        else:
            sentiment = "mixed"
            
        analysis.append(f"Overall market sentiment is {sentiment} with {up_count} pairs up and {down_count} pairs down in the last 24 hours.")
        
        # Strongest and weakest performers
        if realtime_data:
            sorted_pairs = sorted(realtime_data, key=lambda x: x['change_pct'], reverse=True)
            best = sorted_pairs[0]
            worst = sorted_pairs[-1]
            
            analysis.append(f"The strongest performer is {best['pair']} with a {best['change_pct']:.2f}% change.")
            analysis.append(f"The weakest performer is {worst['pair']} with a {worst['change_pct']:.2f}% change.")
        
        return analysis

    def generate_crypto_analysis(self, btc_data, forex_changes):
        """Generate written analysis for Bitcoin performance"""
        if not btc_data:
            return ["No Bitcoin data available for analysis."]
            
        analysis = []
        btc_rate = float(btc_data['5. Exchange Rate'])
        bid_price = float(btc_data['8. Bid Price'])
        ask_price = float(btc_data['9. Ask Price'])
        
        # Calculate spread percentage
        spread_pct = ((ask_price - bid_price) / bid_price) * 100
            
        analysis.append(f"Current Bitcoin exchange rate is ${btc_rate:,.2f}")
        analysis.append(f"The current bid-ask spread is {spread_pct:.2f}% (Bid: ${bid_price:,.2f}, Ask: ${ask_price:,.2f})")
        
        # Compare with forex market only if we have forex data
        if forex_changes and len(forex_changes) > 0:
            forex_rates = [d['rate'] for d in forex_changes if 'rate' in d]
            forex_spreads = [d.get('spread_pct', 0) for d in forex_changes if 'spread_pct' in d]
            
            if forex_rates:
                forex_avg_rate = np.mean(forex_rates)
                if forex_spreads:
                    forex_avg_spread = np.mean(forex_spreads)
                    if spread_pct > forex_avg_spread:
                        analysis.append(f"Bitcoin is showing higher liquidity spread than the forex market average of {forex_avg_spread:.2f}%")
                    else:
                        analysis.append(f"Bitcoin is showing tighter liquidity spread than the forex market average of {forex_avg_spread:.2f}%")
            
        return analysis

    def analyze_correlations(self, correlation_matrix):
        """Generate written analysis of correlations"""
        if correlation_matrix.empty:
            return ["No correlation data available for analysis."]
            
        analysis = []
        
        # Find strongest positive and negative correlations
        strongest_pos = None
        strongest_neg = None
        max_corr = -1
        min_corr = 1
        
        for col in correlation_matrix.columns:
            for idx in correlation_matrix.index:
                if col != idx:  # Skip self-correlations
                    corr = correlation_matrix.loc[idx, col]
                    if corr > max_corr:
                        max_corr = corr
                        strongest_pos = (idx, col)
                    if corr < min_corr:
                        min_corr = corr
                        strongest_neg = (idx, col)
        
        if strongest_pos:
            analysis.append(f"Strongest positive correlation: {strongest_pos[0]} and {strongest_pos[1]} ({max_corr:.2f})")
        if strongest_neg:
            analysis.append(f"Strongest negative correlation: {strongest_neg[0]} and {strongest_neg[1]} ({min_corr:.2f})")
            
        return analysis

    def generate_report(self, currency_pairs, output_dir="reports"):
        """Generate comprehensive report with real-time and historical analysis"""
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize HTML content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = [
            f"<html><head><title>Forex Analysis Report - {timestamp}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "h1, h2 { color: #333; }",
            ".chart { width: 100%; margin: 20px 0; }",
            ".analysis { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }",
            "</style></head><body>",
            f"<h1>Forex and Crypto Analysis Report</h1>",
            f"<p>Generated at: {timestamp}</p>"
        ]

        # Real-time Analysis Section
        html_content.append("<h2>Real-time Exchange Rates</h2>")
        
        # Create real-time rates table
        realtime_rows = ["<table><tr><th>Currency Pair</th><th>Latest Rate</th><th>24h Change</th><th>Last Updated</th></tr>"]
        realtime_data = []
        
        for base, quote in currency_pairs:
            df = self.load_realtime_data(base, quote)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                pair_data = {
                    'pair': f"{base}/{quote}",
                    'rate': latest['exchange_rate'],
                    'change_pct': 0,
                    'last_updated': latest['last_refreshed']
                }
                
                if len(df) > 6:  # If we have at least 24 hours of data (4-hour intervals)
                    prev_rate = df.iloc[-6]['exchange_rate']
                    change_pct = ((latest['exchange_rate'] - prev_rate) / prev_rate) * 100
                    pair_data['change_pct'] = change_pct
                    change_color = 'green' if change_pct > 0 else 'red'
                    change_str = f"<span style='color: {change_color}'>{change_pct:.2f}%</span>"
                else:
                    change_str = "N/A"
                
                realtime_rows.append(
                    f"<tr><td>{base}/{quote}</td><td>{latest['exchange_rate']:.4f}</td>"
                    f"<td>{change_str}</td><td>{latest['last_refreshed']}</td></tr>"
                )
                realtime_data.append(pair_data)
        
        html_content.extend(realtime_rows)
        html_content.append("</table>")
        
        # Add market analysis
        market_analysis = self.generate_market_analysis(currency_pairs, realtime_data)
        html_content.append("<div class='analysis'>")
        html_content.append("<h3>Market Analysis</h3>")
        html_content.extend([f"<p>{analysis}</p>" for analysis in market_analysis])
        html_content.append("</div>")

        # Add Bitcoin section with trend analysis
        html_content.append("<h2>Bitcoin Analysis</h2>")
        btc_data = self.get_crypto_rate("BTC", "USD")
        
        if btc_data:
            btc_rate = float(btc_data['5. Exchange Rate'])
            bid_price = float(btc_data['8. Bid Price'])
            ask_price = float(btc_data['9. Ask Price'])
            
            html_content.extend([
                "<table>",
                "<tr><th>Metric</th><th>Value</th></tr>",
                f"<tr><td>Current BTC/USD Rate</td><td>${btc_rate:,.2f}</td></tr>",
                f"<tr><td>Bid Price</td><td>${bid_price:,.2f}</td></tr>",
                f"<tr><td>Ask Price</td><td>${ask_price:,.2f}</td></tr>",
                f"<tr><td>Last Refreshed</td><td>{btc_data['6. Last Refreshed']} {btc_data['7. Time Zone']}</td></tr>",
                "</table>"
            ])
        
            # Add Bitcoin analysis
            crypto_analysis = self.generate_crypto_analysis(btc_data, realtime_data)
            html_content.append("<div class='analysis'>")
            html_content.append("<h3>Crypto Market Analysis</h3>")
            html_content.extend([f"<p>{analysis}</p>" for analysis in crypto_analysis])
            html_content.append("</div>")
            
            # Add Bitcoin trend analysis
            trend_data = self.get_crypto_trend_data()
            if trend_data is not None:
                # Create Bitcoin trend chart
                fig_btc = go.Figure()
                fig_btc.add_trace(
                    go.Scatter(x=trend_data['timestamp'], y=trend_data['rate'],
                              name='BTC/USD', line=dict(color='orange'))
                )
                fig_btc.update_layout(
                    title="Bitcoin Price Trend",
                    xaxis_title="Time",
                    yaxis_title="Rate (USD)",
                    height=400
                )
                
                # Save the Bitcoin trend chart
                fig_btc.write_html(f"{output_dir}/btc_trend.html")
                
                # Add the chart to the report
                html_content.append("<h3>Bitcoin Price Trend</h3>")
                html_content.append(f'<div class="chart"><iframe src="btc_trend.html" width="100%" height="400px" frameborder="0"></iframe></div>')
                
                # Add trend analysis
                trend_analysis = self.analyze_crypto_trend(trend_data)
                html_content.append("<div class='analysis'>")
                html_content.append("<h3>Bitcoin Trend Analysis</h3>")
                html_content.extend([f"<p>{analysis}</p>" for analysis in trend_analysis])
                html_content.append("</div>")
        else:
            html_content.append("<p>No Bitcoin data available</p>")

        # Price Trends Section
        html_content.append("<h2>Price Trends Analysis</h2>")
        
        # Create price trends chart for forex pairs
        fig = make_subplots(rows=len(currency_pairs), cols=1,
                          subplot_titles=[f'{base}/{quote}' for base, quote in currency_pairs],
                          vertical_spacing=0.05)

        # Add forex pairs price trends
        for i, (base, quote) in enumerate(currency_pairs, start=1):
            df = self.load_daily_data(base, quote)
            if df is not None:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['close'],
                              name=f'{base}/{quote}'),
                    row=i, col=1
                )

        fig.update_layout(height=300*len(currency_pairs),
                         title_text="Forex Price Trends (Last 30 Days)",
                         showlegend=True)
        
        # Save the price trends chart
        fig.write_html(f"{output_dir}/price_trends.html")
        
        # Add the chart to the report
        html_content.append(f'<div class="chart"><iframe src="price_trends.html" width="100%" height="{300*len(currency_pairs)}px" frameborder="0"></iframe></div>')

        # Correlation Analysis Section
        html_content.append("<h2>Currency Pair Correlations</h2>")
        correlation_matrix = pd.DataFrame()
        
        # Calculate correlations between forex pairs and Bitcoin
        all_pairs = currency_pairs + [("BTC", "USD")]
        for base1, quote1 in all_pairs:
            pair_data = {}
            if base1 == "BTC":
                # Use trend data for Bitcoin
                df1 = self.get_crypto_trend_data()
                if df1 is not None:
                    df1 = df1.set_index('timestamp')[['rate']].rename(columns={'rate': 'close'})
            else:
                df1 = self.load_daily_data(base1, quote1)
                
            if df1 is not None:
                for base2, quote2 in all_pairs:
                    if base2 == "BTC":
                        # Use trend data for Bitcoin
                        df2 = self.get_crypto_trend_data()
                        if df2 is not None:
                            df2 = df2.set_index('timestamp')[['rate']].rename(columns={'rate': 'close'})
                    else:
                        df2 = self.load_daily_data(base2, quote2)
                        
                    if df2 is not None:
                        # Calculate correlation on aligned dates
                        if base1 == "BTC" or base2 == "BTC":
                            # For Bitcoin correlations, use the trend data timestamps
                            df1_resampled = df1.resample('4H').last()
                            df2_resampled = df2.resample('4H').last()
                            merged = pd.merge(df1_resampled['close'], df2_resampled['close'],
                                           left_index=True, right_index=True,
                                           suffixes=('_1', '_2'))
                        else:
                            merged = pd.merge(df1['close'], df2['close'],
                                           left_index=True, right_index=True,
                                           suffixes=('_1', '_2'))
                        
                        if not merged.empty:
                            corr = merged['close_1'].corr(merged['close_2'])
                            pair_data[f"{base2}/{quote2}"] = corr
                            
            if pair_data:
                correlation_matrix[f"{base1}/{quote1}"] = pd.Series(pair_data)

        # Add correlation analysis
        correlation_analysis = self.analyze_correlations(correlation_matrix)
        html_content.append("<div class='analysis'>")
        html_content.append("<h3>Correlation Analysis</h3>")
        html_content.extend([f"<p>{analysis}</p>" for analysis in correlation_analysis])
        html_content.append("</div>")

        # Create correlation heatmap
        if not correlation_matrix.empty:
            fig_corr = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                text=correlation_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
                colorscale="RdBu"
            ))
            
            fig_corr.update_layout(
                title="Correlation Heatmap (including Bitcoin)",
                height=600,
                width=800
            )
            
            # Save the correlation heatmap
            fig_corr.write_html(f"{output_dir}/correlation_heatmap.html")
            
            # Add the heatmap to the report
            html_content.append(f'<div class="chart"><iframe src="correlation_heatmap.html" width="100%" height="600px" frameborder="0"></iframe></div>')

        # Close HTML
        html_content.append("</body></html>")

        # Save the report
        report_path = f"{output_dir}/forex_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, "w") as f:
            f.write("\n".join(html_content))
        
        print(f"Report generated: {report_path}")
        return report_path

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Example usage
    generator = ReportGenerator()
    currency_pairs = [
        ("EUR", "USD"),
        ("GBP", "USD"),
        ("JPY", "USD"),
        ("AUD", "USD")
    ]
    generator.generate_report(currency_pairs) 