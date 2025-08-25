#!/usr/bin/env python3
"""
Test yfinance warning suppression
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import warnings
import yfinance as yf

def test_yfinance_warning():
    """Test that yfinance FutureWarning is suppressed."""
    print("Testing yfinance auto_adjust parameter...")
    
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # This should NOT generate a FutureWarning
        data = yf.download('EURUSD=X', period='5d', interval='1h', progress=False, auto_adjust=False)
        
        # Check for FutureWarnings
        future_warnings = [warning for warning in w if issubclass(warning.category, FutureWarning)]
        
        if future_warnings:
            print("❌ FutureWarnings still present:")
            for warning in future_warnings:
                print(f"   {warning.message}")
        else:
            print("✅ No FutureWarnings detected!")
            print(f"   Data shape: {data.shape}")

if __name__ == "__main__":
    test_yfinance_warning()
