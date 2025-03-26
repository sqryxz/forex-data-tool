# Forex Realtime Exchange Rates Tool

A simple Python tool for fetching and analyzing realtime forex exchange rates using the Alpha Vantage API.

## Features

- Fetch realtime exchange rates for major currency pairs
- Generate realtime market summaries
- Basic trend analysis for current rates
- Support for multiple currency pairs

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Alpha Vantage API key:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

## Usage

Run the main script to get realtime exchange rates:

```bash
python3 src/main.py
```

The script will:
1. Fetch realtime rates for major currency pairs
2. Perform basic trend analysis
3. Generate a realtime market summary report

## Currency Pairs

The tool currently monitors these currency pairs:
- EUR/USD
- USD/JPY
- GBP/USD
- AUD/USD
- EUR/GBP

## Output

The tool generates a realtime market summary in the `data` directory with:
- Current exchange rates
- Daily price changes
- Basic trend analysis
- Market overview

## Requirements

- Python 3.8+
- Alpha Vantage API key
- Required Python packages (see requirements.txt) 