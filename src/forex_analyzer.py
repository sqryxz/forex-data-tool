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

    def analyze_pair(self, data, base_currency, quote_currency):
        """Analyze forex data for a currency pair"""
        analysis = {
            'pair': f'{base_currency}/{quote_currency}',
            'timestamp': datetime.now().isoformat(),
            'metrics': self._calculate_metrics(data),
            'trends': self._analyze_trends(data),
            'patterns': self._identify_patterns(data),
            'risk_metrics': self._calculate_risk_metrics(data)
        }
        return analysis
    
    def _calculate_metrics(self, data):
        """Calculate basic statistical metrics"""
        returns = data['close'].pct_change()
        weekly_returns = data['close'].pct_change(5)
        monthly_returns = data['close'].pct_change(20)
        
        metrics = {
            'current_price': data['close'].iloc[-1],
            'daily_change': returns.iloc[-1],
            'weekly_change': weekly_returns.iloc[-1],
            'monthly_change': monthly_returns.iloc[-1],
            'volatility': returns.std(),
            'avg_daily_range': (data['high'] - data['low']).mean(),
            'max_price': data['high'].max(),
            'min_price': data['low'].min(),
            'avg_volume': (data['high'] - data['low']).mean() * 100000  # Approximate volume
        }
        return metrics
    
    def _analyze_trends(self, data):
        """Analyze price trends"""
        sma_20 = data['close'].rolling(20).mean()
        sma_50 = data['close'].rolling(50).mean()
        sma_200 = data['close'].rolling(200).mean()
        
        trends = {
            'sma_20': sma_20.iloc[-1],
            'sma_50': sma_50.iloc[-1],
            'sma_200': sma_200.iloc[-1],
            'trend_direction': self._determine_trend_direction(sma_20, sma_50, sma_200),
            'trend_strength': self._calculate_trend_strength(data['close'], sma_20),
            'support_level': self._find_support_level(data),
            'resistance_level': self._find_resistance_level(data)
        }
        return trends
    
    def _identify_patterns(self, data):
        """Identify common price patterns"""
        patterns = {
            'double_top': self._check_double_top(data),
            'double_bottom': self._check_double_bottom(data),
            'head_and_shoulders': self._check_head_and_shoulders(data),
            'breakout_potential': self._check_breakout_potential(data)
        }
        return patterns
    
    def _calculate_risk_metrics(self, data):
        """Calculate risk-related metrics"""
        returns = data['close'].pct_change()
        risk_metrics = {
            'var_95': np.percentile(returns.dropna(), 5),  # 95% Value at Risk
            'max_drawdown': self._calculate_max_drawdown(data['close']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'beta': self._calculate_beta(returns)
        }
        return risk_metrics
    
    def _determine_trend_direction(self, sma_20, sma_50, sma_200):
        """Determine overall trend direction using multiple SMAs"""
        current_price = sma_20.iloc[-1]
        if current_price > sma_50.iloc[-1] and current_price > sma_200.iloc[-1]:
            return 'strong_uptrend'
        elif current_price > sma_50.iloc[-1]:
            return 'moderate_uptrend'
        elif current_price < sma_50.iloc[-1] and current_price < sma_200.iloc[-1]:
            return 'strong_downtrend'
        elif current_price < sma_50.iloc[-1]:
            return 'moderate_downtrend'
        return 'sideways'
    
    def _calculate_trend_strength(self, prices, sma_20):
        """Calculate trend strength using price deviation from SMA"""
        deviation = abs(prices - sma_20) / sma_20
        return deviation.mean()
    
    def _find_support_level(self, data, window=20):
        """Find potential support level"""
        return data['low'].rolling(window).min().iloc[-1]
    
    def _find_resistance_level(self, data, window=20):
        """Find potential resistance level"""
        return data['high'].rolling(window).max().iloc[-1]
    
    def _check_double_top(self, data):
        """Check for double top pattern"""
        highs = data['high'].rolling(10).max()
        if abs(highs.iloc[-1] - highs.iloc[-10]) < 0.001:
            return True
        return False
    
    def _check_double_bottom(self, data):
        """Check for double bottom pattern"""
        lows = data['low'].rolling(10).min()
        if abs(lows.iloc[-1] - lows.iloc[-10]) < 0.001:
            return True
        return False
    
    def _check_head_and_shoulders(self, data):
        """Basic head and shoulders pattern detection"""
        # Simplified check - can be enhanced
        return False
    
    def _check_breakout_potential(self, data):
        """Check for potential breakout"""
        recent_volatility = data['close'].pct_change().std()
        current_range = (data['high'] - data['low']).iloc[-1]
        if current_range > 2 * recent_volatility:
            return True
        return False
    
    def _calculate_max_drawdown(self, prices):
        """Calculate maximum drawdown"""
        peak = prices.expanding(min_periods=1).max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate/252
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def _calculate_beta(self, returns, market_returns=None):
        """Calculate beta (simplified)"""
        if market_returns is None:
            # Using a simple proxy
            return returns.std()
        return returns.cov(market_returns) / market_returns.var()
    
    def save_analysis(self, analysis, base_currency, quote_currency):
        """Save analysis results with detailed insights"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'data/forex_report_{timestamp}.txt'
        
        with open(filename, 'w') as f:
            f.write("Forex Market Analysis Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Currency Pair: {analysis['pair']}\n\n")
            
            # Market Overview
            f.write("Market Overview\n")
            f.write("-" * 30 + "\n")
            f.write(f"Current Price: {analysis['metrics']['current_price']:.4f}\n")
            f.write(f"Daily Change: {analysis['metrics']['daily_change']*100:.2f}%\n")
            f.write(f"Weekly Change: {analysis['metrics']['weekly_change']*100:.2f}%\n")
            f.write(f"Monthly Change: {analysis['metrics']['monthly_change']*100:.2f}%\n")
            f.write(f"Average Daily Trading Range: {analysis['metrics']['avg_daily_range']:.4f}\n")
            f.write(f"Approximate Daily Volume: {analysis['metrics']['avg_volume']:,.0f} units\n\n")
            
            # Technical Analysis
            f.write("Technical Analysis\n")
            f.write("-" * 30 + "\n")
            f.write(f"Trend Direction: {analysis['trends']['trend_direction']}\n")
            f.write(f"20-day SMA: {analysis['trends']['sma_20']:.4f}\n")
            f.write(f"50-day SMA: {analysis['trends']['sma_50']:.4f}\n")
            f.write(f"200-day SMA: {analysis['trends']['sma_200']:.4f}\n")
            f.write(f"Support Level: {analysis['trends']['support_level']:.4f}\n")
            f.write(f"Resistance Level: {analysis['trends']['resistance_level']:.4f}\n")
            
            # Pattern Analysis
            f.write("\nPrice Patterns\n")
            f.write("-" * 30 + "\n")
            for pattern, present in analysis['patterns'].items():
                f.write(f"{pattern.replace('_', ' ').title()}: {'Yes' if present else 'No'}\n")
            
            # Risk Analysis
            f.write("\nRisk Metrics\n")
            f.write("-" * 30 + "\n")
            f.write(f"Daily Volatility: {analysis['metrics']['volatility']*100:.2f}%\n")
            f.write(f"Value at Risk (95%): {analysis['risk_metrics']['var_95']*100:.2f}%\n")
            f.write(f"Maximum Drawdown: {analysis['risk_metrics']['max_drawdown']*100:.2f}%\n")
            f.write(f"Sharpe Ratio: {analysis['risk_metrics']['sharpe_ratio']:.2f}\n")
            f.write(f"Beta: {analysis['risk_metrics']['beta']:.2f}\n\n")
            
            # Market Commentary
            f.write("Market Commentary\n")
            f.write("-" * 30 + "\n")
            f.write(self._generate_market_commentary(analysis) + "\n\n")
            
            # Trading Implications
            f.write("Trading Implications\n")
            f.write("-" * 30 + "\n")
            f.write(self._generate_trading_implications(analysis) + "\n")
    
    def _generate_market_commentary(self, analysis):
        """Generate market commentary based on analysis"""
        commentary = []
        
        # Trend analysis
        if analysis['trends']['trend_direction'] == 'strong_uptrend':
            commentary.append("The pair is showing strong bullish momentum with prices above all major moving averages.")
        elif analysis['trends']['trend_direction'] == 'strong_downtrend':
            commentary.append("The pair is in a significant downtrend, trading below key moving averages.")
        
        # Volatility commentary
        vol = analysis['metrics']['volatility'] * 100
        if vol > 1:
            commentary.append(f"Market volatility is elevated at {vol:.2f}%, suggesting increased risk and potential opportunities.")
        else:
            commentary.append(f"Market volatility remains contained at {vol:.2f}%, indicating stable trading conditions.")
        
        # Pattern implications
        if analysis['patterns']['breakout_potential']:
            commentary.append("Technical indicators suggest a potential breakout scenario developing.")
        
        return " ".join(commentary)
    
    def _generate_trading_implications(self, analysis):
        """Generate trading implications based on analysis"""
        implications = []
        
        # Risk assessment
        risk_level = "high" if analysis['metrics']['volatility'] > 0.01 else "moderate" if analysis['metrics']['volatility'] > 0.005 else "low"
        implications.append(f"Risk Level: {risk_level.title()}")
        
        # Trading suggestion
        if analysis['trends']['trend_direction'].endswith('uptrend'):
            implications.append("Consider long positions with stops below the identified support level.")
        elif analysis['trends']['trend_direction'].endswith('downtrend'):
            implications.append("Short positions might be favorable with stops above the resistance level.")
        else:
            implications.append("Range-trading strategies may be more appropriate in current conditions.")
        
        # Risk management
        implications.append(f"Suggested Stop Loss: {analysis['risk_metrics']['var_95']*100:.2f}% below entry for long positions.")
        
        return "\n".join(implications)

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