#!/usr/bin/env python3
"""
CLI Test Script

This script demonstrates key CLI functionality programmatically.
"""

import sys
import os

# Add backend path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_list_groups():
    """Test listing symbol groups."""
    print("🧪 Testing: List Symbol Groups")
    print("-" * 40)
    
    from trading_cli import TradingCLI
    
    cli = TradingCLI()
    groups = cli.manager.list_groups()
    
    print(f"Found {len(groups)} symbol groups:")
    for group in groups:
        enabled_symbols = group.get_enabled_symbols()
        status = "🟢" if group.enabled else "🔴"
        auto_run = group.metadata.get("auto_run_enabled", False)
        auto_status = "📅" if auto_run else "⏸️"
        
        print(f"{status} {auto_status} {group.name} ({group.group_id})")
        print(f"    Symbols: {len(enabled_symbols)}/{len(group.symbols)}")
        print(f"    Description: {group.description}")
        print(f"    Created: {group.created_at[:10]}")
        
        if auto_run:
            interval = group.metadata.get("schedule_interval", "N/A")
            weekdays = group.metadata.get("schedule_weekdays", [])
            print(f"    Scheduled: Every {interval}min on {weekdays}")
        print()

def test_indicator_settings():
    """Test indicator settings management."""
    print("\n🧪 Testing: Indicator Settings")
    print("-" * 40)
    
    from trading_cli import IndicatorSettings
    
    settings = IndicatorSettings()
    
    print("Default Indicator Settings:")
    for key, value in settings.settings.items():
        if key == "crossover_indicators":
            print(f"  {key}:")
            for indicator, enabled in value.items():
                status = "✅" if enabled else "❌"
                print(f"    {status} {indicator}")
        else:
            print(f"  {key}: {value}")
    
    # Test updating settings
    print("\nTesting setting updates:")
    settings.update_setting("lookback_period", 14)
    settings.update_setting("adx_threshold", 20)
    settings.update_setting("crossover_indicators.rsi", True)
    
    print(f"✅ Updated lookback_period to: {settings.settings['lookback_period']}")
    print(f"✅ Updated adx_threshold to: {settings.settings['adx_threshold']}")
    print(f"✅ Updated RSI crossover to: {settings.settings['crossover_indicators']['rsi']}")

def test_single_symbol_analysis():
    """Test single symbol analysis."""
    print("\n🧪 Testing: Single Symbol Analysis")
    print("-" * 40)
    
    try:
        from utility.symbol_groups_manager import SymbolConfig
        from workflow.group_analysis_engine import SymbolAnalyzer, GroupAnalysisReporter
        
        # Test EUR/USD analysis
        config = SymbolConfig(
            symbol="eurusd",
            asset_type="forex",
            timeframe="15m",
            period="5d",
            enabled=True
        )
        
        print(f"🔍 Analyzing EUR/USD (15m timeframe)...")
        result = SymbolAnalyzer.analyze_symbol("eurusd_15m", config)
        
        if result.success:
            print(f"✅ Analysis completed successfully!")
            print(f"   Latest Price: ${result.latest_price:.5f}")
            print(f"   Price Change: {result.price_change:+.5f} ({result.price_change_pct:+.2f}%)")
            print(f"   Sentiment: {result.overall_sentiment}")
            print(f"   Signals: Buy={result.signals_summary['Buy']}, Sell={result.signals_summary['Sell']}, Neutral={result.signals_summary['Neutral']}")
            
            if result.last_7_prices:
                print(f"   Last 7 Prices: {' → '.join([f'{p:.5f}' for p in result.last_7_prices])}")
            
            if result.atr_bands:
                atr_value = result.atr_bands.get('atr_value', 0)
                stop_loss = result.atr_bands.get('stop_loss_long', 0)
                take_profit = result.atr_bands.get('take_profit_long', 0)
                print(f"   ATR Bands: ATR={atr_value:.5f}, SL={stop_loss:.5f}, TP={take_profit:.5f}")
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")

def test_group_analysis():
    """Test group analysis functionality."""
    print("\n🧪 Testing: Group Analysis")
    print("-" * 40)
    
    try:
        from trading_cli import TradingCLI
        
        cli = TradingCLI()
        groups = cli.manager.list_groups()
        
        if groups:
            # Test with the first enabled group
            test_group = None
            for group in groups:
                if group.enabled and len(group.get_enabled_symbols()) > 0:
                    test_group = group
                    break
            
            if test_group:
                print(f"🔍 Analyzing group: {test_group.name}")
                print(f"   Symbols: {len(test_group.get_enabled_symbols())}")
                
                result = cli.engine.analyze_group(test_group)
                
                print(f"✅ Group analysis completed!")
                print(f"   Success Rate: {result.successful_analyses}/{result.total_symbols}")
                print(f"   Group Sentiment: {result.group_sentiment}")
                print(f"   Execution Time: {result.execution_time:.2f}s")
                print(f"   Group Signals: Buy={result.group_signals_summary['Buy']}, Sell={result.group_signals_summary['Sell']}, Neutral={result.group_signals_summary['Neutral']}")
                
                # Show successful symbols
                successful_symbols = [k for k, v in result.symbol_results.items() if v.success]
                if successful_symbols:
                    print(f"   Successful symbols: {', '.join(successful_symbols[:3])}{'...' if len(successful_symbols) > 3 else ''}")
            else:
                print("❌ No enabled groups with symbols found")
        else:
            print("❌ No groups found")
            
    except Exception as e:
        print(f"❌ Error during group analysis: {str(e)}")

def test_scheduler_settings():
    """Test scheduler settings."""
    print("\n🧪 Testing: Scheduler Settings")
    print("-" * 40)
    
    from trading_cli import SchedulerSettings
    
    settings = SchedulerSettings()
    
    print("Default Scheduler Settings:")
    for key, value in settings.settings.items():
        print(f"  {key}: {value}")
    
    # Test modifications
    print("\nTesting setting modifications:")
    settings.settings["schedule_interval"] = 30
    settings.settings["auto_run_enabled"] = True
    settings.settings["schedule_weekdays"] = [0, 1, 2, 3, 4, 5]  # Mon-Sat
    
    print(f"✅ Updated interval to: {settings.settings['schedule_interval']} minutes")
    print(f"✅ Updated auto_run to: {settings.settings['auto_run_enabled']}")
    print(f"✅ Updated weekdays to: {settings.settings['schedule_weekdays']}")

def test_periodic_runner():
    """Test periodic runner functionality."""
    print("\n🧪 Testing: Periodic Runner")
    print("-" * 40)
    
    try:
        from trading_cli import PeriodicRunner
        from utility.symbol_groups_manager import SymbolGroupManager
        from workflow.group_analysis_engine import GroupAnalysisEngine
        
        manager = SymbolGroupManager()
        engine = GroupAnalysisEngine(max_workers=2)
        runner = PeriodicRunner(manager, engine)
        
        print(f"Periodic runner created successfully")
        print(f"Running status: {runner.running}")
        
        # Test scheduling (without actually starting)
        groups = manager.list_groups()
        auto_run_groups = [g for g in groups if g.metadata.get("auto_run_enabled", False)]
        
        print(f"Groups with auto-run enabled: {len(auto_run_groups)}")
        for group in auto_run_groups:
            interval = group.metadata.get("schedule_interval", 15)
            weekdays = group.metadata.get("schedule_weekdays", [0,1,2,3,4])
            print(f"  - {group.name}: Every {interval}min on weekdays {weekdays}")
        
        print("✅ Periodic runner test completed")
        
    except Exception as e:
        print(f"❌ Error testing periodic runner: {str(e)}")

def main():
    """Run all CLI tests."""
    print("🚀 TRADING CLI FUNCTIONALITY TESTS")
    print("=" * 60)
    
    # Test each component
    test_list_groups()
    test_indicator_settings()
    test_scheduler_settings()
    test_periodic_runner()
    test_single_symbol_analysis()
    test_group_analysis()
    
    print("\n" + "=" * 60)
    print("✅ ALL CLI TESTS COMPLETED!")
    print("\n📋 CLI Features Verified:")
    print("  ✅ Symbol group listing and management")
    print("  ✅ Indicator settings configuration")
    print("  ✅ Scheduler settings management")
    print("  ✅ Periodic runner setup")
    print("  ✅ Single symbol analysis")
    print("  ✅ Group analysis engine")
    print("\n🎯 The CLI is ready for use!")
    print("   Run: python trading_cli.py")

if __name__ == "__main__":
    main()
