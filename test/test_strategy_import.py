#!/usr/bin/env python3
"""
Simple strategy import test
"""
import sys
import os

# Add backend path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

try:
    from strategy import list_available_strategies, get_strategy_info
    
    print("Available strategies:", list_available_strategies())
    print("\nDual Supertrend info:", get_strategy_info('dual-supertrend-check-single-timeframe'))
    print("\nAll strategy info:")
    for strategy_name in list_available_strategies():
        try:
            info = get_strategy_info(strategy_name)
            print(f"  - {strategy_name}: {info.get('description', 'No description')}")
        except Exception as e:
            print(f"  - {strategy_name}: Error getting info: {e}")
    print("\n✅ Strategy import test completed successfully!")
except Exception as e:
    print(f"❌ Strategy import test failed: {e}")
    import traceback
    traceback.print_exc()
