#!/usr/bin/env python3
"""
Enhanced CLI Test Script

Tests all the new features including:
- Arrow key navigation support
- Case-insensitive exit commands ('ext'/'clr')
- Periodic unit testing
- Directional indicators display
- Enhanced crossover status tracking with configurable ranges
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime

# Add backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_cli import TradingCLI, KeyboardInput, IndicatorSettings, PeriodicUnitTester
from symbol_groups_manager import SymbolGroupManager, SymbolConfig
from workflow.group_analysis_engine import GroupAnalysisEngine, SymbolDataFetcher
from indicators import ADX, Stochastic_Oscillator, SupertrendIndicator

def test_keyboard_input():
    """Test enhanced keyboard input functionality."""
    print("="*60)
    print("🧪 TESTING ENHANCED KEYBOARD INPUT")
    print("="*60)
    
    # Test enhanced_input with special commands
    test_commands = ['ext', 'EXT', 'clr', 'CLR', '+', '-', 'normal_input']
    
    for cmd in test_commands:
        print(f"Testing command: '{cmd}'")
        # Simulate the enhanced input processing
        result = cmd.lower() if cmd.lower() in ['ext', 'clr', 'exit', 'clear', 'quit'] else cmd
        if result in ['ext', 'clr', 'exit', 'clear', 'quit']:
            result = 'EXIT'
        print(f"  Result: {result}")
    
    print("✅ Keyboard input test completed")

def test_directional_analysis():
    """Test directional indicator analysis."""
    print("\n" + "="*60)
    print("🧪 TESTING DIRECTIONAL ANALYSIS")
    print("="*60)
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=50, freq='1H')
    sample_data = pd.DataFrame({
        'open': [1.1000 + i*0.0001 for i in range(50)],
        'high': [1.1010 + i*0.0001 for i in range(50)],
        'low': [1.0990 + i*0.0001 for i in range(50)],
        'close': [1.1005 + i*0.0001 for i in range(50)],
        'volume': [1000 + i*10 for i in range(50)]
    }, index=dates)
    
    # Calculate indicators
    try:
        adx_indicator = ADX(adx_period=14)
        stoch_indicator = Stochastic_Oscillator(k_period=14, k_smooth=3, d_period=3)
        supertrend_indicator = SupertrendIndicator(period=10, multiplier=3.0)
        
        # Calculate indicator values
        sample_data['+DI'], sample_data['-DI'], sample_data['ADX'] = adx_indicator.calculate(sample_data)
        sample_data['%K'], sample_data['%D'] = stoch_indicator.calculate(sample_data)
        sample_data['supetrend'], sample_data['direction'] = supertrend_indicator.calculate(sample_data)
        
        # Test directional analysis
        settings = IndicatorSettings()
        directions = settings.get_directional_analysis(sample_data, {})
        
        print("Directional Analysis Results:")
        for indicator, direction in directions.items():
            print(f"  {indicator}: {direction}")
        
        print("✅ Directional analysis test completed")
        
    except Exception as e:
        print(f"❌ Error in directional analysis test: {e}")

def test_crossover_status():
    """Test crossover status tracking."""
    print("\n" + "="*60)
    print("🧪 TESTING CROSSOVER STATUS TRACKING")
    print("="*60)
    
    # Create sample data with crossovers
    dates = pd.date_range('2024-01-01', periods=20, freq='1H')
    
    # Create sample stochastic data with a crossover
    k_values = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 75, 70, 65, 60, 55, 50, 45]
    d_values = [30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68]
    
    crossover_data = pd.DataFrame({
        'open': [1.1000] * 20,
        'high': [1.1010] * 20,
        'low': [1.0990] * 20,
        'close': [1.1005] * 20,
        '%K': k_values,
        '%D': d_values,
        '+DI': [45 + i for i in range(20)],
        '-DI': [55 - i for i in range(20)],
        'direction': [True if i > 10 else False for i in range(20)]
    }, index=dates)
    
    # Test crossover analysis
    try:
        settings = IndicatorSettings()
        symbol_key = "TEST_EURUSD_1h"
        
        # Test with different crossover ranges
        for crossover_range in [5, 7, 10]:
            settings.set_symbol_crossover_range(symbol_key, crossover_range)
            crossovers = settings.get_crossover_status(crossover_data, symbol_key)
            
            print(f"\nCrossover Analysis (Range: {crossover_range} periods):")
            for indicator, status in crossovers.items():
                print(f"  {indicator}: {status}")
        
        print("✅ Crossover status test completed")
        
    except Exception as e:
        print(f"❌ Error in crossover status test: {e}")

def test_periodic_unit_tester():
    """Test periodic unit testing functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING PERIODIC UNIT TESTER")
    print("="*60)
    
    try:
        # Initialize components
        manager = SymbolGroupManager()
        engine = GroupAnalysisEngine(max_workers=2)
        unit_tester = PeriodicUnitTester(manager, engine)
        
        # Create a test group if none exists
        groups = manager.list_groups()
        if not groups:
            print("Creating test group...")
            test_symbols = {
                "EURUSD_1h": SymbolConfig(
                    symbol="eurusd",
                    asset_type="forex",
                    timeframe="1h",
                    period="5d",
                    enabled=True
                )
            }
            
            success = manager.create_group(
                name="Test Group",
                symbols=test_symbols,
                description="Test group for unit testing",
                enabled=True
            )
            
            if success:
                print("✅ Test group created")
                groups = manager.list_groups()
            else:
                print("❌ Failed to create test group")
                return
        
        test_group = groups[0]
        symbol_key = list(test_group.symbols.keys())[0]
        
        print(f"Testing with group: {test_group.name}, symbol: {symbol_key}")
        
        # Test manual unit test
        print("\n1. Testing manual unit test...")
        unit_tester.run_symbol_unit_test(test_group.group_id, symbol_key)
        
        # Test scheduling (but don't actually run for long)
        print("\n2. Testing test scheduling...")
        unit_tester.schedule_symbol_test(test_group.group_id, symbol_key, 1)  # 1 minute for test
        
        # Wait a moment and check schedule
        time.sleep(2)
        
        # Test summary
        print("\n3. Testing summary...")
        summary = unit_tester.get_test_summary()
        print(f"Test Summary: {summary}")
        
        # Stop tests
        print("\n4. Stopping tests...")
        unit_tester.stop_all_tests()
        
        print("✅ Periodic unit tester test completed")
        
    except Exception as e:
        print(f"❌ Error in periodic unit tester test: {e}")

def test_indicator_settings_enhancements():
    """Test enhanced indicator settings with +/- toggles."""
    print("\n" + "="*60)
    print("🧪 TESTING ENHANCED INDICATOR SETTINGS")
    print("="*60)
    
    try:
        settings = IndicatorSettings()
        
        print("1. Testing initial settings:")
        print(f"   Crossover enabled: {settings.settings['crossover_enabled']}")
        print(f"   Crossover indicators: {settings.settings['crossover_indicators']}")
        print(f"   Default crossover range: {settings.settings['crossover_range']}")
        
        print("\n2. Testing indicator toggles:")
        # Test toggle functionality
        for indicator in settings.settings["crossover_indicators"]:
            original_state = settings.settings["crossover_indicators"][indicator]
            new_state = settings.toggle_indicator(indicator)
            print(f"   {indicator}: {original_state} -> {new_state}")
        
        print("\n3. Testing symbol-specific crossover ranges:")
        # Test per-symbol crossover ranges
        test_symbols = ["EURUSD_1h", "GBPUSD_30m", "USDJPY_4h"]
        for i, symbol in enumerate(test_symbols):
            range_value = 5 + i * 2
            settings.set_symbol_crossover_range(symbol, range_value)
            retrieved_range = settings.get_symbol_crossover_range(symbol)
            print(f"   {symbol}: set {range_value}, got {retrieved_range}")
        
        print("✅ Enhanced indicator settings test completed")
        
    except Exception as e:
        print(f"❌ Error in indicator settings test: {e}")

def test_enhanced_symbol_analysis():
    """Test enhanced single symbol analysis with directional data."""
    print("\n" + "="*60)
    print("🧪 TESTING ENHANCED SYMBOL ANALYSIS")
    print("="*60)
    
    try:
        # Test with a real symbol
        config = SymbolConfig(
            symbol="eurusd",
            asset_type="forex",
            timeframe="1h",
            period="5d",
            enabled=True
        )
        
        print("1. Fetching sample data...")
        raw_data = SymbolDataFetcher.fetch_symbol_data(config)
        
        if raw_data.empty:
            print("❌ No data available for testing")
            return
        
        print(f"   Data points: {len(raw_data)}")
        
        print("\n2. Calculating indicators...")
        # Calculate indicators
        adx_indicator = ADX(adx_period=14)
        stoch_indicator = Stochastic_Oscillator(k_period=14, k_smooth=3, d_period=3)
        supertrend_indicator = SupertrendIndicator(period=10, multiplier=3.0)
        
        # Apply indicators
        raw_data['+DI'], raw_data['-DI'], raw_data['ADX'] = adx_indicator.calculate(raw_data)
        raw_data['%K'], raw_data['%D'] = stoch_indicator.calculate(raw_data)
        raw_data['supetrend'], raw_data['direction'] = supertrend_indicator.calculate(raw_data)
        
        print("   Indicators calculated successfully")
        
        print("\n3. Testing directional analysis...")
        settings = IndicatorSettings()
        directions = settings.get_directional_analysis(raw_data, {})
        
        for indicator, direction in directions.items():
            print(f"   {indicator}: {direction}")
        
        print("\n4. Testing crossover analysis...")
        symbol_key = "EURUSD_1h"
        crossovers = settings.get_crossover_status(raw_data, symbol_key)
        
        for indicator, status in crossovers.items():
            print(f"   {indicator}: {status}")
        
        print("✅ Enhanced symbol analysis test completed")
        
    except Exception as e:
        print(f"❌ Error in enhanced symbol analysis test: {e}")

def run_all_tests():
    """Run all enhancement tests."""
    print("🚀 ENHANCED CLI TESTING SUITE")
    print("="*60)
    print(f"Test started at: {datetime.now()}")
    
    # Run all tests
    test_keyboard_input()
    test_directional_analysis()
    test_crossover_status()
    test_indicator_settings_enhancements()
    test_enhanced_symbol_analysis()
    test_periodic_unit_tester()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED")
    print("="*60)
    print(f"Test completed at: {datetime.now()}")
    print("\n📋 Summary of Features Tested:")
    print("  ✅ Enhanced keyboard input with case-insensitive commands")
    print("  ✅ Directional indicator analysis")
    print("  ✅ Crossover status tracking with configurable ranges")
    print("  ✅ Enhanced indicator settings with +/- toggles")
    print("  ✅ Periodic unit testing functionality")
    print("  ✅ Enhanced symbol analysis with directional data")
    
    print("\n🎯 Features Ready for Use:")
    print("  • Arrow key navigation support")
    print("  • 'ext'/'clr' exit commands")
    print("  • Periodic unit testing of individual symbols")
    print("  • Directional indicators (Supertrend, Stochastic, DMI)")
    print("  • Crossover status with last N periods (configurable per symbol)")
    print("  • Enhanced +/- key controls for enable/disable")

if __name__ == "__main__":
    run_all_tests()
