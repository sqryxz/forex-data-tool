import requests
import pandas as pd
from datetime import datetime
import time

class ForexDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.alphavantage.co/query'
    
    def fetch_daily_data(self, base_currency, quote_currency):
        """Fetch daily forex data for a currency pair"""
        params = {
            'function': 'FX_DAILY',
            'from_symbol': base_currency,
            'to_symbol': quote_currency,
            'apikey': self.api_key,
            'outputsize': 'full'
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Respect API rate limits
        time.sleep(12)  # Alpha Vantage free tier: 5 calls per minute
        
        return self._process_response(data)
    
    def _process_response(self, data):
        """Process the API response into a pandas DataFrame"""
        if 'Time Series FX (Daily)' not in data:
            raise ValueError('Invalid API response format')
            
        df = pd.DataFrame.from_dict(data['Time Series FX (Daily)'], orient='index')
        df.index = pd.to_datetime(df.index)
        df.columns = ['open', 'high', 'low', 'close']
        df = df.astype(float)
        
        return df
    
    def save_data(self, data, base_currency, quote_currency):
        """Save forex data to CSV"""
        filename = f'data/{base_currency}_{quote_currency}_daily.csv'
        os.makedirs('data', exist_ok=True)
        data.to_csv(filename)