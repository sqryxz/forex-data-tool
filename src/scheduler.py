import os
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv
from forex_data_fetcher import ForexDataFetcher
from correlation_analyzer import CorrelationAnalyzer
from report_generator import ReportGenerator

def run_analysis():
    print(f"\nStarting analysis at {datetime.now()}")
    
    # Load environment variables
    load_dotenv()
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    if not API_KEY:
        print("Error: ALPHA_VANTAGE_API_KEY not found in environment variables")
        return
    
    # Initialize fetcher
    fetcher = ForexDataFetcher(API_KEY)
    
    # Currency pairs to monitor
    currency_pairs = [
        ("EUR", "USD"),
        ("GBP", "USD"),
        ("JPY", "USD"),
        ("AUD", "USD")
    ]
    
    # Fetch and save data for each currency pair
    for base, quote in currency_pairs:
        print(f"\nFetching data for {base}/{quote}...")
        
        # Get and save real-time quote first (it's a different API endpoint)
        latest = fetcher.get_latest_quote(base, quote)
        if latest:
            print(f"Latest {base}/{quote} rate: {latest['5. Exchange Rate']}")
            fetcher.save_realtime_quote(latest, base, quote)
        
        # Then get daily historical data
        data = fetcher.fetch_forex_data(base, quote, outputsize="compact")
        if data:
            fetcher.save_forex_data(data, base, quote)
        
        # Respect API rate limits
        time.sleep(15)
    
    # Fetch and save Bitcoin data
    print("\nFetching Bitcoin data...")
    
    # Get and save real-time crypto quote first
    latest_crypto = fetcher.get_latest_quote("BTC", "USD")
    if latest_crypto:
        print(f"Latest BTC/USD rate: {latest_crypto['5. Exchange Rate']}")
        fetcher.save_realtime_quote(latest_crypto, "BTC", "USD")
    
    # Then get daily historical crypto data
    btc_data = fetcher.fetch_crypto_data(symbol="BTC", market="USD", outputsize="compact")
    if btc_data:
        fetcher.save_crypto_data(btc_data, "BTC", "USD")
    
    # Run correlation analysis
    print("\nRunning correlation analysis...")
    analyzer = CorrelationAnalyzer()
    try:
        correlations, price_data = analyzer.calculate_correlations(currency_pairs)
        analyzer.plot_correlations(correlations, price_data)
        print("\nAnalysis completed successfully")
    except Exception as e:
        print(f"Error during analysis: {e}")
    
    # Generate report
    print("\nGenerating report...")
    generator = ReportGenerator()
    try:
        report_path = generator.generate_report(currency_pairs)
        print(f"Report generated successfully at: {report_path}")
    except Exception as e:
        print(f"Error generating report: {e}")

def main():
    print("Starting scheduler...")
    
    # Run immediately on start
    run_analysis()
    
    # Schedule to run every 4 hours
    schedule.every(4).hours.do(run_analysis)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 