import os
import time
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from forex_analyzer import ForexAnalyzer
from forex_data_fetcher import ForexDataFetcher

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print('Error: ALPHA_VANTAGE_API_KEY not found in environment variables')
        return
    
    # Initialize components
    data_fetcher = ForexDataFetcher(api_key)
    analyzer = ForexAnalyzer()
    
    # Currency pairs to monitor
    pairs = [
        ('EUR', 'USD'),
        ('USD', 'JPY'),
        ('GBP', 'USD'),
        ('AUD', 'USD'),
        ('EUR', 'GBP')
    ]

    # Store historical data for hourly analysis
    historical_data = {f"{base}/{quote}": [] for base, quote in pairs}
    last_hourly_report = datetime.now().replace(minute=0, second=0, microsecond=0)

    def fetch_and_analyze():
        nonlocal last_hourly_report
        current_time = datetime.now()
        print(f"\nFetching realtime forex data... {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        all_analyses = []
        
        # Fetch and process realtime data for each pair
        for base, quote in pairs:
            try:
                print(f"Processing {base}/{quote}...")
                
                # Fetch realtime forex data
                quote_data = data_fetcher.get_latest_quote(base, quote)
                if quote_data:
                    # Save realtime quote
                    data_fetcher.save_realtime_quote(quote_data, base, quote)
                    
                    # Store historical data point
                    rate = float(quote_data['5. Exchange Rate'])
                    historical_data[f"{base}/{quote}"].append({
                        'timestamp': current_time,
                        'rate': rate
                    })
                    
                    # Keep only last 24 hours of data
                    cutoff_time = current_time - timedelta(hours=24)
                    historical_data[f"{base}/{quote}"] = [
                        d for d in historical_data[f"{base}/{quote}"]
                        if d['timestamp'] > cutoff_time
                    ]
                    
                    # Create a simple DataFrame for analysis
                    data = pd.DataFrame({
                        'timestamp': [current_time],
                        'close': [rate]
                    })
                    
                    # Perform quick analysis on current rate
                    analysis = analyzer.analyze_pair(data, base, quote)
                    all_analyses.append(analysis)
                    
                    print(f"Current {base}/{quote} rate: {rate} ({quote_data['6. Last Refreshed']})")
                
            except Exception as e:
                print(f'Error processing {base}/{quote}: {str(e)}')
        
        # Generate realtime market report
        generate_market_summary(all_analyses, historical_data)
        
        # Check if we need to generate hourly report
        current_hour = current_time.replace(minute=0, second=0, microsecond=0)
        if current_hour > last_hourly_report:
            generate_hourly_summary(historical_data, current_time)
            last_hourly_report = current_hour
        
        print("\nAnalysis complete. Realtime reports have been generated in the data directory.")

    def calculate_arbitrage_opportunities(analyses):
        """Calculate potential arbitrage opportunities"""
        opportunities = []
        rates = {a['pair']: a['metrics']['current_price'] for a in analyses if 'metrics' in a and 'current_price' in a['metrics']}
        
        # Check EUR/USD vs EUR/GBP * GBP/USD
        if all(pair in rates for pair in ['EUR/USD', 'EUR/GBP', 'GBP/USD']):
            direct = rates['EUR/USD']
            indirect = rates['EUR/GBP'] * rates['GBP/USD']
            diff_pct = ((direct/indirect) - 1) * 100
            
            if abs(diff_pct) > 0.05:  # 0.05% threshold
                opportunities.append({
                    'type': 'Triangular',
                    'pairs': ['EUR/USD', 'EUR/GBP', 'GBP/USD'],
                    'direct_rate': direct,
                    'indirect_rate': indirect,
                    'difference_pct': diff_pct
                })
        
        return opportunities

    def generate_market_insights(analyses, historical_data):
        """Generate market insights based on current and historical data"""
        insights = []
        
        # Analyze volatility
        for analysis in analyses:
            pair = analysis['pair']
            if pair in historical_data and len(historical_data[pair]) > 1:
                rates = [d['rate'] for d in historical_data[pair]]
                volatility = np.std(rates) / np.mean(rates) * 100
                
                if volatility > 0.5:
                    insights.append(f"{pair} shows high volatility ({volatility:.2f}% std dev)")
                elif volatility < 0.1:
                    insights.append(f"{pair} shows unusually low volatility ({volatility:.2f}% std dev)")
        
        # Analyze trends
        for analysis in analyses:
            if 'trends' in analysis:
                trend = analysis['trends']
                if trend.get('trend_direction') == 'bullish' and trend.get('strength', 0) > 0.01:
                    insights.append(f"{analysis['pair']} shows strong upward momentum")
                elif trend.get('trend_direction') == 'bearish' and trend.get('strength', 0) > 0.01:
                    insights.append(f"{analysis['pair']} shows strong downward pressure")
        
        return insights

    def generate_market_summary(analyses, historical_data):
        """Generate a realtime market summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'data/forex_realtime_summary_{timestamp}.txt'
        
        with open(filename, 'w') as f:
            f.write("Forex Market Realtime Summary Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Current Exchange Rates
            f.write("Current Exchange Rates\n")
            f.write("-" * 30 + "\n")
            for analysis in analyses:
                if 'metrics' in analysis and 'current_price' in analysis['metrics']:
                    f.write(f"{analysis['pair']}: {analysis['metrics']['current_price']:.4f}\n")
            f.write("\n")
            
            # Market Overview
            f.write("Market Overview\n")
            f.write("-" * 30 + "\n")
            for analysis in analyses:
                if 'metrics' in analysis and 'current_price' in analysis['metrics']:
                    f.write(f"\n{analysis['pair']}:\n")
                    f.write(f"  Current Price: {analysis['metrics']['current_price']:.4f}\n")
                    if 'daily_change' in analysis['metrics']:
                        f.write(f"  Daily Change: {analysis['metrics']['daily_change']*100:.2f}%\n")
                    if 'trends' in analysis and 'trend_direction' in analysis['trends']:
                        f.write(f"  Trend Direction: {analysis['trends']['trend_direction']}\n")
                        if 'strength' in analysis['trends']:
                            f.write(f"  Trend Strength: {analysis['trends']['strength']*100:.2f}%\n")
            
            # Market Insights
            f.write("\nMarket Insights\n")
            f.write("-" * 30 + "\n")
            insights = generate_market_insights(analyses, historical_data)
            if insights:
                for insight in insights:
                    f.write(f"- {insight}\n")
            else:
                f.write("No significant insights at this time.\n")
            
            # Arbitrage Opportunities
            f.write("\nArbitrage Opportunities\n")
            f.write("-" * 30 + "\n")
            opportunities = calculate_arbitrage_opportunities(analyses)
            if opportunities:
                for opp in opportunities:
                    f.write(f"- {opp['type']} opportunity detected:\n")
                    f.write(f"  Pairs involved: {', '.join(opp['pairs'])}\n")
                    f.write(f"  Direct rate: {opp['direct_rate']:.4f}\n")
                    f.write(f"  Indirect rate: {opp['indirect_rate']:.4f}\n")
                    f.write(f"  Potential profit: {abs(opp['difference_pct']):.2f}%\n")
            else:
                f.write("No significant arbitrage opportunities detected.\n")
            
            # Risk Warning
            f.write("\nRisk Warning\n")
            f.write("-" * 30 + "\n")
            f.write("This analysis is based on realtime data and is for informational purposes only.\n")
            f.write("Trading forex carries significant risk. Always use proper risk management.\n")

    def generate_hourly_summary(historical_data, current_time):
        """Generate hourly summary report"""
        timestamp = current_time.strftime("%Y%m%d_%H%M%S")
        filename = f'data/forex_hourly_summary_{timestamp}.txt'
        
        with open(filename, 'w') as f:
            f.write("Forex Hourly Market Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Period: Last hour\n\n")
            
            for pair, data in historical_data.items():
                if data:
                    # Get data points from the last hour
                    hour_ago = current_time - timedelta(hours=1)
                    hour_data = [d for d in data if d['timestamp'] > hour_ago]
                    
                    if hour_data:
                        rates = [d['rate'] for d in hour_data]
                        f.write(f"\n{pair} Analysis:\n")
                        f.write("-" * 30 + "\n")
                        f.write(f"Opening Rate: {hour_data[0]['rate']:.4f}\n")
                        f.write(f"Closing Rate: {hour_data[-1]['rate']:.4f}\n")
                        f.write(f"High: {max(rates):.4f}\n")
                        f.write(f"Low: {min(rates):.4f}\n")
                        f.write(f"Average: {sum(rates)/len(rates):.4f}\n")
                        
                        # Calculate hourly change
                        hourly_change = ((hour_data[-1]['rate'] - hour_data[0]['rate']) / hour_data[0]['rate']) * 100
                        f.write(f"Hourly Change: {hourly_change:.2f}%\n")
                        
                        # Calculate volatility
                        volatility = np.std(rates) / np.mean(rates) * 100
                        f.write(f"Hourly Volatility: {volatility:.2f}%\n")

    print("Starting Forex Realtime Monitor")
    print("Press Ctrl+C to stop the program")
    
    try:
        while True:
            fetch_and_analyze()
            print("\nWaiting 10 minutes until next update...")
            time.sleep(600)  # Wait for 10 minutes
    except KeyboardInterrupt:
        print("\nStopping Forex Realtime Monitor...")
        print("Program terminated by user")

if __name__ == '__main__':
    main() 