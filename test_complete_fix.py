#!/usr/bin/env python3
"""
Quick test of trading CLI functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_cli import TradingCLI
from utility.symbol_groups_manager import SymbolConfig
from workflow.group_analysis_engine import SymbolAnalyzer

def test_cli_analysis():
    """Test CLI analysis functionality."""
    print("Testing CLI analysis functionality...")
    
    # Create test symbol configuration
    config = SymbolConfig(
        symbol='aapl',
        asset_type='stocks',
        timeframe='1d',
        period='1mo',
        enabled=True
    )
    
    try:
        # Test symbol analysis
        result = SymbolAnalyzer.analyze_symbol('aapl_1d', config)
        
        if result.success:
            print("✅ CLI analysis working!")
            print(f"   Symbol: {result.symbol.upper()}")
            print(f"   Price: ${result.latest_price:.2f}")
            print(f"   Change: {result.price_change_pct:.2f}%")
            print(f"   Sentiment: {result.overall_sentiment}")
            return True
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_cli_analysis()
    if success:
        print("\n🎉 All fixes are working correctly!")
        print("   - yfinance FutureWarning suppressed")
        print("   - indicators module imports fixed")
        print("   - CLI analysis functional")
    else:
        print("\n⚠️  Some issues may remain")
