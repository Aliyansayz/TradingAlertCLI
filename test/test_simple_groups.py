"""
Quick test of the Symbol Groups system with working symbols
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig
from workflow.group_analysis_engine import GroupAnalysisEngine, GroupAnalysisReporter
from datetime import datetime

def test_symbol_groups():
    """Test with a simple working configuration."""
    
    print("🚀 Quick Symbol Groups Test")
    print("="*50)
    
    # Initialize components
    manager = SymbolGroupManager()
    engine = GroupAnalysisEngine(max_workers=2)
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    # Create a simple test group with working stock symbols
    test_group = SymbolGroup(
        group_id="test_stocks",
        name="Test Stock Group",
        description="Simple test with major stock symbols",
        symbols={
            "aapl_1d": SymbolConfig(
                symbol="AAPL",
                asset_type="stocks",
                timeframe="1d",
                period="1mo",
                enabled=True
            ),
            "msft_1d": SymbolConfig(
                symbol="MSFT", 
                asset_type="stocks",
                timeframe="1d",
                period="1mo",
                enabled=True
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["test", "stocks"]
    )
    
    # Save the test group
    success = manager.save_group(test_group)
    print(f"✅ Created test group: {success}")
    
    # List groups
    groups = manager.list_groups()
    print(f"📋 Available groups: {[g.group_id for g in groups]}")
    
    # Run analysis
    print(f"\n🔍 Running analysis on test group...")
    result = engine.analyze_group(test_group)
    
    # Print results
    GroupAnalysisReporter.print_group_result(result, detailed=True)
    
    # Show summary
    print(f"\n✅ Test completed!")
    print(f"   - Successful analyses: {result.successful_analyses}/{result.total_symbols}")
    print(f"   - Execution time: {result.execution_time:.2f}s")
    print(f"   - Group sentiment: {result.group_sentiment}")
    
    # Show one symbol's detailed data
    if result.symbol_results:
        symbol_key = list(result.symbol_results.keys())[0]
        symbol_result = result.symbol_results[symbol_key]
        
        if symbol_result.success:
            print(f"\n📊 Sample data for {symbol_key}:")
            print(f"   Latest Price: ${symbol_result.latest_price:.2f}")
            print(f"   Price Change: {symbol_result.price_change:+.2f} ({symbol_result.price_change_pct:+.1f}%)")
            print(f"   Data Points: {symbol_result.data_points}")
            
            if symbol_result.indicators:
                print(f"   Key Indicators:")
                for indicator, value in list(symbol_result.indicators.items())[:3]:
                    print(f"     {indicator}: {value:.2f}")

if __name__ == "__main__":
    test_symbol_groups()
