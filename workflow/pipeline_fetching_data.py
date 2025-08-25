"""
Data Fetching Pipeline Module

This module handles data fetching from various sources including yfinance,
and provides a unified interface for retrieving financial market data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

# Import symbol mappings
from utility.forex_symbols import get_forex_symbols
from utility.indices_symbols import get_indices_symbols

class DataFetcher:
    """
    Unified data fetching class that handles multiple asset types
    including forex, stocks, indices, and crypto.
    """
    
    def __init__(self):
        self.forex_symbols = get_forex_symbols()
        self.indices_symbols = get_indices_symbols()
        self.logger = logging.getLogger(__name__)
        
    def get_symbol_for_asset(self, asset_key: str, asset_type: str = "forex") -> str:
        """
        Get the yfinance symbol for a given asset key and type.
        
        Args:
            asset_key: The friendly asset key (e.g., 'eurusd', 'sp500')
            asset_type: The type of asset ('forex', 'indices', 'stocks', 'crypto')
            
        Returns:
            The yfinance symbol string
        """
        asset_key = asset_key.lower()
        
        if asset_type == "forex":
            return self.forex_symbols.get(asset_key, asset_key)
        elif asset_type == "indices":
            return self.indices_symbols.get(asset_key, asset_key)
        elif asset_type == "stocks":
            # For stocks, return as-is (assume ticker symbol)
            return asset_key.upper()
        elif asset_type == "crypto":
            # For crypto, append -USD if not already present
            if not asset_key.endswith('-USD'):
                return f"{asset_key.upper()}-USD"
            return asset_key.upper()
        else:
            return asset_key
    
    def fetch_data(self, 
                   symbol: str, 
                   period: str = "7d", 
                   interval: str = "1h",
                   asset_type: str = "forex") -> pd.DataFrame:
        """
        Fetch OHLC data for a given symbol.
        
        Args:
            symbol: The asset symbol or friendly key
            period: The time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: The data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            asset_type: The type of asset
            
        Returns:
            DataFrame with OHLC data
        """
        try:
            # Get the yfinance symbol
            yf_symbol = self.get_symbol_for_asset(symbol, asset_type)
            
            self.logger.info(f"Fetching data for {yf_symbol} ({symbol}) - Period: {period}, Interval: {interval}")
            
            # Fetch the data
            data = yf.download(yf_symbol, period=period, interval=interval, progress=False)
            
            if data.empty:
                self.logger.warning(f"No data retrieved for {yf_symbol}")
                return pd.DataFrame()
            
            # Clean up the data
            data = self._clean_data(data, yf_symbol)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def _clean_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Clean and standardize the fetched data.
        
        Args:
            df: Raw data from yfinance
            symbol: The symbol string
            
        Returns:
            Cleaned DataFrame
        """
        # Handle MultiIndex columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]
            # Remove trailing underscores
            df.columns = [col[:-1] if col.endswith('_') else col for col in df.columns]
        
        # Remove symbol suffix from column names
        df.columns = [col.replace(f'_{symbol}', '') for col in df.columns]
        
        # Standardize column names
        column_mapping = {
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Ensure we have the required OHLC columns
        required_columns = ['open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df.columns:
                self.logger.warning(f"Missing column {col} in data for {symbol}")
        
        # Remove any NaN rows
        df = df.dropna()
        
        return df
    
    def fetch_multiple_assets(self, 
                            assets: List[Dict[str, str]], 
                            period: str = "7d", 
                            interval: str = "1h") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple assets.
        
        Args:
            assets: List of dictionaries with 'symbol' and 'type' keys
            period: The time period
            interval: The data interval
            
        Returns:
            Dictionary mapping asset symbols to their DataFrames
        """
        results = {}
        
        for asset in assets:
            symbol = asset.get('symbol', '')
            asset_type = asset.get('type', 'forex')
            
            if symbol:
                data = self.fetch_data(symbol, period, interval, asset_type)
                if not data.empty:
                    results[symbol] = data
                    
        return results

# Legacy code preservation - commenting out the original implementation
"""
# Original yfinance_data_loader.py code preserved below:

import yfinance as yf
import pandas as pd

# Fetch data for EURUSD, which is 'EURUSD=X' in yfinance
# Use period='7d' for the last day and interval='1h' for 1-hour data
target_symmbol = 'EURUSD=X'

eurusd_data = yf.download(target_symmbol, period='7d', interval='1h')

# Flatten the MultiIndex columns if they exist
if isinstance(eurusd_data.columns, pd.MultiIndex):
  eurusd_data.columns = ['_'.join(col).strip() for col in eurusd_data.columns.values]
  # Remove trailing underscores if they exist (from the empty string in the tuple)
  eurusd_data.columns = [col[:-1] if col.endswith('_') else col for col in eurusd_data.columns]

# Remove the '_EURUSD=X' suffix from column names
eurusd_data.columns = [col.replace(f'_{target_symmbol}', '') for col in eurusd_data.columns]

eurusd_data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)

# Display the OHLC data
display(eurusd_data)
"""

def get_legacy_eurusd_data():
    """
    Legacy function to maintain compatibility with existing code.
    Returns EURUSD data using the original approach.
    """
    fetcher = DataFetcher()
    return fetcher.fetch_data('eurusd', period='7d', interval='1h', asset_type='forex')

# Example usage and testing
if __name__ == "__main__":
    # Initialize the data fetcher
    fetcher = DataFetcher()
    
    # Test fetching EURUSD data (maintaining compatibility with original code)
    eurusd_data = fetcher.fetch_data('eurusd', period='7d', interval='1h', asset_type='forex')
    print("EURUSD Data:")
    print(eurusd_data.head())
    
    # Test fetching multiple assets
    assets = [
        {'symbol': 'eurusd', 'type': 'forex'},
        {'symbol': 'sp500', 'type': 'indices'},
        {'symbol': 'AAPL', 'type': 'stocks'}
    ]
    
    multi_data = fetcher.fetch_multiple_assets(assets)
    print(f"\nFetched data for {len(multi_data)} assets")