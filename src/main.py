import os
from dotenv import load_dotenv
from forex_data import ForexDataFetcher
from analysis import ForexAnalyzer
from visualization import ChartGenerator

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
    chart_gen = ChartGenerator()
    
    # Currency pairs to monitor
    pairs = [
        ('EUR', 'USD'),
        ('USD', 'JPY'),
        ('GBP', 'USD'),
        ('AUD', 'USD')
    ]
    
    # Fetch and process data for each pair
    for base, quote in pairs:
        try:
            # Fetch forex data
            data = data_fetcher.fetch_daily_data(base, quote)
            
            # Save raw data
            data_fetcher.save_data(data, base, quote)
            
            # Analyze data
            analysis = analyzer.analyze_pair(data, base, quote)
            analyzer.save_analysis(analysis, base, quote)
            
            # Generate charts
            chart_gen.create_candlestick_chart(data, base, quote)
            
        except Exception as e:
            print(f'Error processing {base}/{quote}: {str(e)}')

if __name__ == '__main__':
    main()