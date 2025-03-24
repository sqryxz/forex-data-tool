# Forex Data Aggregator

A Python-based tool for fetching, analyzing, and visualizing forex data using the Alpha Vantage API. The tool provides daily summaries, trend analysis, crypto market correlations, and potential arbitrage opportunities detection.

## Features

- Fetch daily forex data for major currency pairs with crypto market correlation:
  - EUR/USD (High liquidity, global risk sentiment indicator)
  - USD/JPY (Safe-haven currency, risk-off indicator)
  - GBP/USD (Major pair with crypto correlation)
  - AUD/USD (Commodity price movement proxy)
- Real-time exchange rate quotes
- Statistical analysis of currency trends
- Bitcoin price correlation analysis
- Interactive candlestick charts with Bitcoin comparison
- Triangular arbitrage opportunity detection
- Daily/weekly summary reports

## Requirements

- Python 3.7+
- Alpha Vantage API key (free tier available at https://www.alphavantage.co)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd forex-data-tool
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the main script:
```bash
python3 src/main.py
```

The script will:
- Fetch latest forex data for configured currency pairs
- Generate statistical analysis
- Calculate Bitcoin price correlations
- Create interactive charts with Bitcoin comparison
- Save a comprehensive summary report

## Data and Reports

- Raw forex data is saved in CSV format in the `data` directory
- Analysis reports are saved as text files with timestamp in the `data` directory
- Interactive charts are saved as HTML files in the `data` directory

## Analysis Features

### Currency Pair Analysis
- Mean price and volatility
- Daily returns
- Bitcoin price correlation metrics:
  - Current correlation
  - Average correlation
  - Correlation trend (increasing/decreasing)

### Visualization
- Interactive candlestick charts for each currency pair
- Normalized Bitcoin price overlay for comparison
- Trend analysis with multiple timeframes

### Arbitrage Detection
- Triangular arbitrage opportunities between major pairs
- Minimum threshold of 0.1% price difference

## Configuration

The main configuration is in `src/main.py`:
- API key
- Currency pairs to monitor (prioritized based on crypto correlation)
- Analysis parameters
- Correlation window size

## Output Files

The tool generates several types of files in the `data` directory:
- `{BASE}_{QUOTE}_daily.csv`: Raw daily forex data
- `{BASE}_{QUOTE}_trend.html`: Interactive candlestick charts with Bitcoin comparison
- `forex_report_{TIMESTAMP}.txt`: Comprehensive analysis reports including crypto correlations

## Note on API Limits

The free tier of Alpha Vantage API has the following limits:
- 5 API calls per minute
- 500 API calls per day

The tool automatically respects these limits by adding appropriate delays between API calls.

## License

MIT 