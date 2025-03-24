import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
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
    
    print("\nFetching and analyzing forex data...\n")
    
    all_analyses = []
    
    # Fetch and process data for each pair
    for base, quote in pairs:
        try:
            print(f"Processing {base}/{quote}...")
            
            # Fetch forex data
            data = data_fetcher.fetch_daily_data(base, quote)
            
            # Save raw data
            data_fetcher.save_data(data, base, quote)
            
            # Perform detailed analysis
            analysis = analyzer.analyze_pair(data, base, quote)
            all_analyses.append(analysis)
            
            # Save individual pair analysis
            analyzer.save_analysis(analysis, base, quote)
            
        except Exception as e:
            print(f'Error processing {base}/{quote}: {str(e)}')
    
    # Generate comprehensive market report
    generate_market_summary(all_analyses)
    
    print("\nAnalysis complete. Reports have been generated in the data directory.")

def generate_market_summary(analyses):
    """Generate a comprehensive market summary report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'data/forex_market_summary_{timestamp}.txt'
    
    with open(filename, 'w') as f:
        f.write("Forex Market Summary Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Overall Market Sentiment
        f.write("Overall Market Sentiment\n")
        f.write("-" * 30 + "\n")
        bullish_pairs = sum(1 for a in analyses if a['trends']['trend_direction'].endswith('uptrend'))
        bearish_pairs = sum(1 for a in analyses if a['trends']['trend_direction'].endswith('downtrend'))
        f.write(f"Bullish Pairs: {bullish_pairs}/{len(analyses)}\n")
        f.write(f"Bearish Pairs: {bearish_pairs}/{len(analyses)}\n")
        f.write("\n")
        
        # Market Volatility Overview
        f.write("Market Volatility Overview\n")
        f.write("-" * 30 + "\n")
        avg_volatility = sum(a['metrics']['volatility'] for a in analyses) / len(analyses)
        f.write(f"Average Market Volatility: {avg_volatility*100:.2f}%\n")
        most_volatile = max(analyses, key=lambda x: x['metrics']['volatility'])
        f.write(f"Most Volatile Pair: {most_volatile['pair']} ({most_volatile['metrics']['volatility']*100:.2f}%)\n\n")
        
        # Individual Pair Analysis
        f.write("Currency Pair Analysis\n")
        f.write("-" * 30 + "\n")
        for analysis in analyses:
            f.write(f"\n{analysis['pair']}:\n")
            f.write(f"  Current Price: {analysis['metrics']['current_price']:.4f}\n")
            f.write(f"  Daily Change: {analysis['metrics']['daily_change']*100:.2f}%\n")
            f.write(f"  Weekly Change: {analysis['metrics']['weekly_change']*100:.2f}%\n")
            f.write(f"  Monthly Change: {analysis['metrics']['monthly_change']*100:.2f}%\n")
            f.write(f"  Trend Direction: {analysis['trends']['trend_direction']}\n")
            f.write(f"  Support Level: {analysis['trends']['support_level']:.4f}\n")
            f.write(f"  Resistance Level: {analysis['trends']['resistance_level']:.4f}\n")
            f.write(f"  Risk Level: {'High' if analysis['metrics']['volatility'] > 0.01 else 'Moderate' if analysis['metrics']['volatility'] > 0.005 else 'Low'}\n")
        
        # Correlation Analysis
        f.write("\nCorrelation Analysis\n")
        f.write("-" * 30 + "\n")
        f.write("Highly correlated pairs (based on daily returns):\n")
        # Add correlation analysis here if needed
        
        # Trading Opportunities
        f.write("\nTrading Opportunities\n")
        f.write("-" * 30 + "\n")
        for analysis in analyses:
            if analysis['patterns']['breakout_potential']:
                f.write(f"Potential breakout detected in {analysis['pair']}\n")
            if analysis['patterns']['double_top']:
                f.write(f"Double top pattern detected in {analysis['pair']}\n")
            if analysis['patterns']['double_bottom']:
                f.write(f"Double bottom pattern detected in {analysis['pair']}\n")
        
        # Risk Warning
        f.write("\nRisk Warning\n")
        f.write("-" * 30 + "\n")
        f.write("This analysis is for informational purposes only. Trading forex carries significant risk.\n")
        f.write("Always use proper risk management and consider seeking professional advice.\n")

if __name__ == '__main__':
    main() 