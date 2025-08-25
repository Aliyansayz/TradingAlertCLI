#!/usr/bin/env python3
"""
Test script to verify ^GSPC analysis works in the CLI context
"""

import sys
import os

# Add backend path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gspc_analysis():
    """Test analysis of ^GSPC symbol using CLI components"""
    try:
        from workflow.group_analysis_engine import SymbolAnalyzer
        from utility.symbol_groups_manager import SymbolConfig
        
        print("🔍 Testing ^GSPC analysis (indices)...")
        
        # Create a test config for ^GSPC
        config = SymbolConfig(
            symbol="^GSPC",
            asset_type="indices",
            timeframe="1d",
            period="1mo"
        )
        
        # Test the analysis
        result = SymbolAnalyzer.analyze_symbol("^GSPC_1d", config)
        
        if result.success:
            print("✅ ^GSPC analysis completed successfully!")
            print(f"   Symbol: {result.symbol}")
            print(f"   Asset Type: {result.asset_type}")
            print(f"   Price: ${result.latest_price:.2f}")
            print(f"   Change: {result.price_change_pct:.2f}%")
            print(f"   Sentiment: {result.overall_sentiment}")
            print(f"   Data Points: {result.data_points}")
            
            if result.indicators:
                print(f"   Indicators available: {list(result.indicators.keys())}")
            
            if result.signals_summary:
                print(f"   Signals: {result.signals_summary}")
                
            print("\n✅ CLI integration test PASSED - No 'close' column error!")
            return True
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_gspc_analysis()
    sys.exit(0 if success else 1)
