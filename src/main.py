import os
import time
from datetime import datetime
from forex_data_fetcher import ForexDataFetcher
from forex_analyzer import ForexAnalyzer

def main():
    # Configuration
    API_KEY = "JU64QY60HLSVUOUU"
    
    # Priority currency pairs based on crypto market correlation
    CURRENCY_PAIRS = [
        ("EUR", "USD"),  # High liquidity, global risk sentiment indicator
        ("USD", "JPY"),  # Safe-haven currency, risk-off indicator
        ("GBP", "USD"),  # Major pair with crypto correlation
        ("AUD", "USD"),  # Commodity price movement proxy
        ("EUR", "GBP")   # For triangular arbitrage detection
    ]
    
    # Initialize components
    fetcher = ForexDataFetcher(API_KEY)
    analyzer = ForexAnalyzer(api_key=API_KEY)  # Pass API key for crypto data access
    
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Fetch latest data for all currency pairs
    print("\nFetching latest forex data...")
    for base, quote in CURRENCY_PAIRS:
        print(f"\nProcessing {base}/{quote}...")
        
        # Fetch and save daily data
        data = fetcher.fetch_forex_data(base, quote)
        if data:
            fetcher.save_forex_data(data, base, quote)
            
        # Get latest quote
        latest = fetcher.get_latest_quote(base, quote)
        if latest:
            print(f"Latest {base}/{quote} rate: {latest['5. Exchange Rate']}")
        
        # Respect API rate limits
        time.sleep(15)
    
    # Generate analysis report
    print("\nGenerating analysis report...")
    report = analyzer.generate_summary_report(CURRENCY_PAIRS)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"data/forex_report_{timestamp}.txt"
    
    with open(report_file, "w") as f:
        f.write("Forex Market Summary Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated at: {report['timestamp']}\n")
        f.write(f"Period: {report['period']}\n\n")
        
        f.write("Currency Pair Analysis:\n")
        for pair, stats in report['currency_analysis'].items():
            f.write(f"\n{pair}:\n")
            f.write(f"  Mean Price: {stats['mean_price']:.4f}\n")
            f.write(f"  Volatility: {stats['volatility']:.2f}%\n")
            f.write(f"  Daily Returns: {stats['daily_returns']:.2f}%\n")
            
            # Add crypto correlation analysis if available
            if pair in report['crypto_correlations']:
                corr = report['crypto_correlations'][pair]
                f.write("\n  Bitcoin Correlation Analysis:\n")
                f.write(f"    Current Correlation: {corr['current_correlation']:.3f}\n")
                f.write(f"    Average Correlation: {corr['avg_correlation']:.3f}\n")
                f.write(f"    Correlation Trend: {corr['correlation_trend']}\n")
        
        if report['arbitrage_opportunities']:
            f.write("\nPotential Arbitrage Opportunities:\n")
            for opp in report['arbitrage_opportunities']:
                f.write(f"\nType: {opp['type']}\n")
                f.write(f"Pairs involved: {', '.join(opp['pairs'])}\n")
                f.write(f"Difference: {opp['difference_pct']:.2f}%\n")
    
    print(f"\nReport saved to: {report_file}")
    
    # Generate plots for each currency pair
    print("\nGenerating trend plots with Bitcoin comparison...")
    for base, quote in CURRENCY_PAIRS:
        plot_file = analyzer.plot_currency_trends(base, quote)
        if plot_file:
            print(f"Generated trend plot: {plot_file}")

if __name__ == "__main__":
    main() 