import os
import json
import time
from datetime import datetime, timedelta
import requests
import pandas as pd

class ForexDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.data_dir = "data"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_forex_data(self, from_currency, to_currency, outputsize="compact"):
        """Fetch forex data for a currency pair"""
        params = {
            "function": "FX_DAILY",
            "from_symbol": from_currency,
            "to_symbol": to_currency,
            "apikey": self.api_key,
            "outputsize": outputsize
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                raise Exception(f"API Error: {data['Error Message']}")
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def fetch_crypto_data(self, symbol="BTC", market="USD", outputsize="compact"):
        """Fetch cryptocurrency data"""
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            "apikey": self.api_key,
            "outputsize": outputsize
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                raise Exception(f"API Error: {data['Error Message']}")
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto data: {e}")
            return None
    
    def save_forex_data(self, data, from_currency, to_currency):
        """Save forex data to CSV file"""
        if not data or "Time Series FX (Daily)" not in data:
            return False
            
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(data["Time Series FX (Daily)"], orient="index")
        df.index = pd.to_datetime(df.index)
        df.columns = ["open", "high", "low", "close"]
        df = df.astype(float)
        
        # Save to CSV
        filename = f"{self.data_dir}/{from_currency}_{to_currency}_daily.csv"
        df.to_csv(filename)
        print(f"Data saved to {filename}")
        return True

    def save_crypto_data(self, data, symbol, market):
        """Save cryptocurrency data to CSV file"""
        if not data or "Time Series (Digital Currency Daily)" not in data:
            return False
            
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(data["Time Series (Digital Currency Daily)"], orient="index")
        df.index = pd.to_datetime(df.index)
        
        # Select only the USD columns we need
        columns = {
            f"1a. open ({market})": "open",
            f"2a. high ({market})": "high",
            f"3a. low ({market})": "low",
            f"4a. close ({market})": "close"
        }
        df = df[list(columns.keys())].rename(columns=columns)
        df = df.astype(float)
        
        # Save to CSV
        filename = f"{self.data_dir}/{symbol}_{market}_daily.csv"
        df.to_csv(filename)
        print(f"Data saved to {filename}")
        return True
    
    def get_latest_quote(self, from_currency, to_currency):
        """Get real-time exchange rate for a currency pair"""
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
                return data["Realtime Currency Exchange Rate"]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching real-time quote: {e}")
            return None

    def save_realtime_quote(self, quote_data, from_currency, to_currency):
        """Save real-time quote to CSV file"""
        if not quote_data:
            return False
            
        # Create a DataFrame with the real-time data
        timestamp = datetime.now()
        data = {
            'timestamp': [timestamp],
            'from_currency': [from_currency],
            'to_currency': [to_currency],
            'exchange_rate': [float(quote_data['5. Exchange Rate'])],
            'last_refreshed': [quote_data['6. Last Refreshed']],
            'timezone': [quote_data['7. Time Zone']]
        }
        new_row_df = pd.DataFrame(data)
        
        # Load existing data or create new file
        filename = f"{self.data_dir}/{from_currency}_{to_currency}_realtime.csv"
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename, parse_dates=['timestamp'])
                df = pd.concat([df, new_row_df], ignore_index=True)
            else:
                df = new_row_df
            
            # Save to CSV
            df.to_csv(filename, index=False)
            print(f"Real-time data saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving real-time data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    # Initialize fetcher
    fetcher = ForexDataFetcher(API_KEY)
    
    # Example currency pairs to monitor
    currency_pairs = [
        ("EUR", "USD"),
        ("GBP", "USD"),
        ("JPY", "USD"),
        ("AUD", "USD")
    ]
    
    # Fetch and save data for each currency pair (last 30 days with compact output)
    for base, quote in currency_pairs:
        print(f"\nFetching data for {base}/{quote}...")
        data = fetcher.fetch_forex_data(base, quote, outputsize="compact")
        if data:
            fetcher.save_forex_data(data, base, quote)
            
        # Get and save latest quote
        latest = fetcher.get_latest_quote(base, quote)
        if latest:
            print(f"Latest {base}/{quote} rate: {latest['5. Exchange Rate']}")
            fetcher.save_realtime_quote(latest, base, quote)
        
        # Respect API rate limits
        time.sleep(15)

    # Fetch and save Bitcoin data
    print("\nFetching Bitcoin data...")
    btc_data = fetcher.fetch_crypto_data(symbol="BTC", market="USD", outputsize="compact")
    if btc_data:
        fetcher.save_crypto_data(btc_data, "BTC", "USD")
        
    # Get and save latest crypto quote
    latest_crypto = fetcher.get_latest_quote("BTC", "USD")
    if latest_crypto:
        print(f"Latest BTC/USD rate: {latest_crypto['5. Exchange Rate']}")
        fetcher.save_realtime_quote(latest_crypto, "BTC", "USD")
    
    # Respect API rate limits
    time.sleep(15) 