#!/usr/bin/env python3
"""
Test script to verify the fixes for yfinance warning and indicators import
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utility.symbol_groups_manager import SymbolGroupManager, SymbolConfig
from workflow.group_analysis_engine import GroupAnalysisEngine, SymbolAnalyzer

def test_symbol_analysis():
    """Test single symbol analysis to verify fixes."""
    print("Testing symbol analysis fixes...")
    
    # Create a test symbol config
    config = SymbolConfig(
        symbol='eurusd',
        asset_type='forex',
        timeframe='1h',
        period='5d',
        enabled=True
    )
    
    try:
        # Test the analysis
        result = SymbolAnalyzer.analyze_symbol('eurusd_1h', config)
        
        if result.success:
            print("✅ Analysis successful!")
            print(f"   Symbol: {result.symbol}")
            print(f"   Latest Price: ${result.latest_price:.4f}")
            print(f"   Data Points: {result.data_points}")
            print(f"   Overall Sentiment: {result.overall_sentiment}")
            
            if result.indicators:
                print("   Key Indicators:")
                for key, value in list(result.indicators.items())[:5]:  # Show first 5
                    print(f"     {key}: {value:.4f}")
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_symbol_analysis()
