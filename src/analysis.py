import pandas as pd
import numpy as np
from datetime import datetime

class ForexAnalyzer:
    def analyze_pair(self, data, base_currency, quote_currency):
        """Analyze forex data for a currency pair"""
        analysis = {
            'pair': f'{base_currency}/{quote_currency}',
            'timestamp': datetime.now().isoformat(),
            'metrics': self._calculate_metrics(data),
            'trends': self._analyze_trends(data)
        }
        return analysis
    
    def _calculate_metrics(self, data):
        """Calculate basic statistical metrics"""
        returns = data['close'].pct_change()
        
        metrics = {
            'current_price': data['close'].iloc[-1],
            'daily_change': returns.iloc[-1],
            'volatility': returns.std(),
            'avg_daily_range': (data['high'] - data['low']).mean(),
            'max_price': data['high'].max(),
            'min_price': data['low'].min()
        }
        return metrics
    
    def _analyze_trends(self, data):
        """Analyze price trends"""
        trends = {
            'sma_20': data['close'].rolling(20).mean().iloc[-1],
            'sma_50': data['close'].rolling(50).mean().iloc[-1],
            'trend_direction': 'up' if data['close'].iloc[-1] > data['close'].iloc[-20].mean() else 'down'
        }
        return trends
    
    def save_analysis(self, analysis, base_currency, quote_currency):
        """Save analysis results"""
        filename = f'data/forex_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(filename, 'w') as f:
            f.write(f'Forex Analysis Report\n')
            f.write(f'===================\n\n')
            f.write(f'Currency Pair: {analysis["pair"]}\n')
            f.write(f'Timestamp: {analysis["timestamp"]}\n\n')
            
            f.write('Metrics:\n')
            for key, value in analysis['metrics'].items():
                f.write(f'{key}: {value}\n')
            
            f.write('\nTrends:\n')
            for key, value in analysis['trends'].items():
                f.write(f'{key}: {value}\n')