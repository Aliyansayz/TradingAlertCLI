"""
Simple US30 Analysis Script - Debug Version

This script fetches US30 data and displays the structure to debug column issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

def debug_us30_data():
    """Debug US30 data fetching to understand column structure."""
    print("="*60)
    print("US30 DATA DEBUGGING")
    print("="*60)
    
    # Fetch US30 data
    symbol = '^DJI'  # Dow Jones Industrial Average
    print(f"Fetching data for {symbol}...")
    
    try:
        # Fetch data with verbose output
        data = yf.download(symbol, period='7d', interval='30m', progress=True)
        
        print(f"\nRaw data shape: {data.shape}")
        print(f"Raw columns: {list(data.columns)}")
        print(f"Raw index type: {type(data.index)}")
        
        if hasattr(data.columns, 'nlevels'):
            print(f"Column levels: {data.columns.nlevels}")
        
        print(f"\nFirst few rows of raw data:")
        print(data.head())
        
        # Clean the data step by step
        print(f"\n" + "="*40)
        print("CLEANING DATA")
        print("="*40)
        
        # Handle MultiIndex columns if they exist
        if isinstance(data.columns, pd.MultiIndex):
            print("MultiIndex columns detected, flattening...")
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            data.columns = [col[:-1] if col.endswith('_') else col for col in data.columns]
            print(f"After flattening: {list(data.columns)}")
        
        # Remove symbol suffix from column names if present
        original_cols = list(data.columns)
        data.columns = [col.replace(f'_{symbol}', '') for col in data.columns]
        if list(data.columns) != original_cols:
            print(f"After removing symbol suffix: {list(data.columns)}")
        
        # Standardize column names
        column_mapping = {
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        
        print(f"Applying column mapping: {column_mapping}")
        data.rename(columns=column_mapping, inplace=True)
        print(f"After renaming: {list(data.columns)}")
        
        # Remove NaN rows
        original_length = len(data)
        data = data.dropna()
        if len(data) != original_length:
            print(f"Removed {original_length - len(data)} NaN rows")
        
        print(f"\nFinal cleaned data:")
        print(f"Shape: {data.shape}")
        print(f"Columns: {list(data.columns)}")
        print(f"Data types:")
        for col in data.columns:
            print(f"  {col}: {data[col].dtype}")
        
        print(f"\nFirst few rows of cleaned data:")
        print(data.head())
        
        # Test accessing close prices
        if 'close' in data.columns:
            print(f"\nLast 7 close prices:")
            last_closes = data['close'].tail(7)
            for i, (timestamp, price) in enumerate(last_closes.items(), 1):
                print(f"{i}. {timestamp}: ${price:,.2f}")
        else:
            print(f"\nError: 'close' column not found!")
            print(f"Available columns: {list(data.columns)}")
        
        return data
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def test_indicators_with_clean_data(data):
    """Test indicators with properly cleaned data."""
    if data.empty or 'close' not in data.columns:
        print("Cannot test indicators - no valid data")
        return
    
    print(f"\n" + "="*40)
    print("TESTING INDICATORS")
    print("="*40)
    
    try:
        # Import indicators
        from indicators_oscillators import Oscillator, Oscillator_Status
        
        # Create oscillator instance
        oscillator = Oscillator(data)
        
        # Test a few key oscillators
        print("Testing RSI...")
        rsi = oscillator.rsi_14()
        print(f"RSI calculated, latest value: {rsi.iloc[-1]:.4f}")
        
        print("Testing Stochastic...")
        stoch = oscillator.stochastic_k_14_3_3()
        print(f"Stochastic K: {stoch['%K'].iloc[-1]:.4f}, D: {stoch['%D'].iloc[-1]:.4f}")
        
        print("Testing CCI...")
        cci = oscillator.cci_20()
        print(f"CCI latest value: {cci.iloc[-1]:.4f}")
        
        print("Testing MACD...")
        macd = oscillator.macd_12_26()
        print(f"MACD: {macd['MACD'].iloc[-1]:.4f}, Signal: {macd['Signal_Line'].iloc[-1]:.4f}")
        
        # Get status for RSI
        rsi_status = Oscillator_Status.get_status(rsi.iloc[-1], 'RSI_14')
        print(f"RSI Status: {rsi_status}")
        
        # Get status for Stochastic
        stoch_status = Oscillator_Status.get_status(stoch['%K'].iloc[-1], '%K')
        print(f"Stochastic K Status: {stoch_status}")
        
        # Get status for CCI
        cci_status = Oscillator_Status.get_status(cci.iloc[-1], 'CCI_20')
        print(f"CCI Status: {cci_status}")
        
        print("\nIndicators test completed successfully!")
        
    except Exception as e:
        print(f"Error testing indicators: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting US30 debug analysis...")
    
    # Debug data fetching
    cleaned_data = debug_us30_data()
    
    # Test indicators if data is valid
    if not cleaned_data.empty:
        test_indicators_with_clean_data(cleaned_data)
    
    print(f"\n" + "="*60)
    print("DEBUG ANALYSIS COMPLETED")
    print("="*60)
