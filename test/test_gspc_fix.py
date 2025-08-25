#!/usr/bin/env python3
"""
Test script to verify ^GSPC analysis works after fixing the import error
"""

import sys
import os

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_gspc_analysis():
    """Test analysis of ^GSPC symbol"""
    try:
        from workflow.group_analysis_engine import SymbolAnalyzer
        from utility.symbol_groups_manager import SymbolConfig
        
        print("🔍 Testing ^GSPC analysis...")
        
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
            print(f"   Price: ${result.latest_price:.2f}")
            print(f"   Change: {result.price_change_pct:.2f}%")
            print(f"   Sentiment: {result.overall_sentiment}")
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            
    except ImportError as e:
        print(f"❌ Import error still exists: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")

if __name__ == "__main__":
    test_gspc_analysis()
