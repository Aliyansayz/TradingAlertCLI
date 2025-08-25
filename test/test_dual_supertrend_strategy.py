#!/usr/bin/env python3
"""
Test script for the new Dual Supertrend Strategy

This script tests the dual-supertrend-check-single-timeframe strategy
to ensure it works correctly with the existing system.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_sample_data(periods=100):
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start=datetime.now() - timedelta(days=periods), periods=periods, freq='D')
    
    # Create somewhat realistic price data with trend
    np.random.seed(42)  # For reproducible results
    base_price = 100
    
    # Generate price series with some trend and volatility
    price_changes = np.random.normal(0.001, 0.02, periods)  # Small daily changes
    cumulative_changes = np.cumsum(price_changes)
    
    # Add a general upward trend
    trend = np.linspace(0, 0.3, periods)
    prices = base_price * (1 + cumulative_changes + trend)
    
    # Create OHLC data
    high = prices * (1 + np.abs(np.random.normal(0, 0.01, periods)))
    low = prices * (1 - np.abs(np.random.normal(0, 0.01, periods)))
    open_prices = prices + np.random.normal(0, 0.005, periods) * prices
    volume = np.random.randint(1000, 10000, periods)
    
    return pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high,
        'low': low,
        'close': prices,
        'volume': volume
    }).set_index('date')

def test_dual_supertrend_strategy():
    """Test the dual supertrend strategy."""
    print("🧪 Testing Dual Supertrend Strategy...")
    
    try:
        # Import the strategy
        from strategy import get_strategy, list_available_strategies, get_strategy_info
        
        print(f"✅ Available strategies: {list_available_strategies()}")
        
        # Get the dual supertrend strategy
        strategy = get_strategy("dual-supertrend-check-single-timeframe")
        print(f"✅ Successfully loaded strategy: {strategy.strategy_name}")
        
        # Get strategy info
        info = get_strategy_info("dual-supertrend-check-single-timeframe")
        print(f"\n📊 Strategy Information:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Create sample data
        print(f"\n📈 Creating sample OHLCV data...")
        data = create_sample_data(150)  # 150 days of data
        print(f"   Data shape: {data.shape}")
        print(f"   Date range: {data.index[0]} to {data.index[-1]}")
        print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        
        # Test the strategy
        print(f"\n🔄 Analyzing data with Dual Supertrend Strategy...")
        
        # Create a mock config object
        class MockConfig:
            def __init__(self):
                self.timeframe = "1d"
                self.period = "3mo"
        
        config = MockConfig()
        
        # Run the analysis
        result = strategy.analyze_symbol_data(data, "TEST_SYMBOL", config)
        
        if result['success']:
            print(f"✅ Strategy analysis completed successfully!")
            
            # Display key results
            print(f"\n📊 Analysis Results:")
            print(f"   Latest Price: ${result['latest_price']:.2f}")
            print(f"   Price Change: {result['price_change']:.2f} ({result['price_change_pct']:.2f}%)")
            print(f"   Overall Sentiment: {result['overall_sentiment']}")
            print(f"   Strategy Used: {result['strategy_used']}")
            
            # Supertrend signals
            if 'supertrend_signals' in result:
                st_signals = result['supertrend_signals']
                print(f"\n🎯 Supertrend Signals:")
                print(f"   Supertrend A (latest): {st_signals.get('latest_supertrend_a', 'N/A'):.2f}")
                print(f"   Direction A: {st_signals.get('latest_direction_a', 'N/A')}")
                print(f"   Supertrend B (latest): {st_signals.get('latest_supertrend_b', 'N/A'):.2f}")
                print(f"   Direction B: {st_signals.get('latest_direction_b', 'N/A')}")
                print(f"   Current Entry Signal: {st_signals.get('current_entry_signal', 'N/A')}")
                print(f"   Current Exit Signal: {st_signals.get('current_exit_signal', 'N/A')}")
            
            # Trading signals
            if 'trading_signals' in result:
                trade_signals = result['trading_signals']
                print(f"\n📈 Trading Signals:")
                print(f"   Signal Strength: {trade_signals.get('signal_strength', 'N/A')}")
                print(f"   Buy Confirmations: {trade_signals.get('buy_confirmations', 'N/A')}")
                print(f"   Sell Confirmations: {trade_signals.get('sell_confirmations', 'N/A')}")
                print(f"   Entry Recommended: {trade_signals.get('entry_recommended', 'N/A')}")
                print(f"   Exit Recommended: {trade_signals.get('exit_recommended', 'N/A')}")
            
            # ATR bands for risk management
            if 'atr_bands' in result:
                atr = result['atr_bands']
                print(f"\n🛡️ Risk Management (ATR Bands):")
                print(f"   ATR 14: {atr.get('atr_14', 'N/A'):.4f}")
                print(f"   Stop Loss (Long): ${atr.get('stop_loss_long', 'N/A'):.2f}")
                print(f"   Take Profit (Long): ${atr.get('take_profit_long', 'N/A'):.2f}")
                print(f"   Stop Loss (Short): ${atr.get('stop_loss_short', 'N/A'):.2f}")
                print(f"   Take Profit (Short): ${atr.get('take_profit_short', 'N/A'):.2f}")
            
            # Baseline indicators
            if 'indicators' in result:
                indicators = result['indicators']
                print(f"\n📉 Baseline Indicators:")
                for indicator, value in indicators.items():
                    print(f"   {indicator}: {value:.4f}")
            
            print(f"\n✅ Test completed successfully!")
            return True
            
        else:
            print(f"❌ Strategy analysis failed: {result.get('error_message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_comparison():
    """Compare results between default and dual supertrend strategies."""
    print(f"\n🔄 Comparing Default vs Dual Supertrend Strategies...")
    
    try:
        from strategy import get_strategy
        
        # Create sample data
        data = create_sample_data(100)
        
        class MockConfig:
            def __init__(self):
                self.timeframe = "1d"
                self.period = "3mo"
        
        config = MockConfig()
        
        # Test default strategy
        default_strategy = get_strategy("default-check-single-timeframe")
        default_result = default_strategy.analyze_symbol_data(data, "TEST_SYMBOL", config)
        
        # Test dual supertrend strategy
        dual_st_strategy = get_strategy("dual-supertrend-check-single-timeframe")
        dual_st_result = dual_st_strategy.analyze_symbol_data(data, "TEST_SYMBOL", config)
        
        if default_result['success'] and dual_st_result['success']:
            print(f"\n📊 Strategy Comparison:")
            print(f"   Default Strategy Sentiment: {default_result['overall_sentiment']}")
            print(f"   Dual Supertrend Sentiment: {dual_st_result['overall_sentiment']}")
            
            print(f"\n📈 Signal Counts:")
            print(f"   Default - Buy: {default_result['signals_summary']['Buy']}, "
                  f"Sell: {default_result['signals_summary']['Sell']}, "
                  f"Neutral: {default_result['signals_summary']['Neutral']}")
            print(f"   Dual ST - Buy: {dual_st_result['signals_summary']['Buy']}, "
                  f"Sell: {dual_st_result['signals_summary']['Sell']}, "
                  f"Neutral: {dual_st_result['signals_summary']['Neutral']}")
            
            return True
        else:
            print(f"❌ One or both strategies failed")
            return False
            
    except Exception as e:
        print(f"❌ Comparison test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DUAL SUPERTREND STRATEGY TEST SUITE")
    print("=" * 60)
    
    # Run individual test
    test1_passed = test_dual_supertrend_strategy()
    
    # Run comparison test
    test2_passed = test_strategy_comparison()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"   Individual Strategy Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Strategy Comparison Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! The Dual Supertrend Strategy is ready to use.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")
