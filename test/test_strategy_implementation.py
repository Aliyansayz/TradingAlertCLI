#!/usr/bin/env python3
"""
Test the new default strategy implementation
"""

import sys
import os
# Add the parent directory (backend) to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.default_strategy import get_strategy
from utility.symbol_groups_manager import SymbolConfig
from workflow.group_analysis_engine import SymbolAnalyzer

def test_strategy_implementation():
    """Test that the new strategy implementation works correctly."""
    print("🧪 TESTING NEW STRATEGY IMPLEMENTATION")
    print("=" * 50)
    
    # Test 1: Strategy creation
    print("\n1. Testing strategy creation...")
    try:
        strategy = get_strategy('default-check-single-timeframe')
        info = strategy.get_strategy_info()
        print(f"✅ Strategy created: {info['name']}")
        print(f"   Description: {info['description']}")
        print(f"   Type: {info['type']}")
        print(f"   Indicators: {len(info['indicators_used'])} indicators")
    except Exception as e:
        print(f"❌ Strategy creation failed: {e}")
        return False
    
    # Test 2: Legacy name mapping
    print("\n2. Testing legacy name mapping...")
    try:
        legacy_strategy = get_strategy('single-check')
        legacy_info = legacy_strategy.get_strategy_info()
        print(f"✅ Legacy mapping works: {legacy_info['name']}")
    except Exception as e:
        print(f"❌ Legacy mapping failed: {e}")
        return False
    
    # Test 3: Integration with analysis engine
    print("\n3. Testing integration with analysis engine...")
    try:
        # Create a test symbol config
        config = SymbolConfig(
            symbol="eurusd",
            asset_type="forex",
            timeframe="1h",
            period="5d",
            enabled=True
        )
        
        print(f"   Testing with EUR/USD (1h timeframe)...")
        # This will use our new strategy implementation
        result = SymbolAnalyzer.analyze_symbol("eurusd_1h", config)
        
        if result.success:
            print(f"✅ Analysis successful!")
            print(f"   Latest Price: ${result.latest_price:.5f}")
            print(f"   Sentiment: {result.overall_sentiment}")
            print(f"   Signals: Buy={result.signals_summary.get('Buy', 0)}, Sell={result.signals_summary.get('Sell', 0)}")
            print(f"   Indicators calculated: {len(result.indicators)}")
            print(f"   ATR bands available: {'Yes' if result.atr_bands else 'No'}")
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    print("\n✅ All tests passed! Strategy implementation is working correctly.")
    return True

if __name__ == "__main__":
    success = test_strategy_implementation()
    sys.exit(0 if success else 1)
