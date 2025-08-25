#!/usr/bin/env python3
"""
Demo script to test the Trading CLI system

This script demonstrates the basic functionality of the CLI system.
"""

import sys
import os

# Add backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cli_imports():
    """Test if all CLI imports work correctly."""
    print("🧪 Testing CLI imports...")
    
    try:
        from trading_cli import TradingCLI, IndicatorSettings, SchedulerSettings
        print("✅ Main CLI classes imported successfully")
        
        from symbol_groups_manager import SymbolGroupManager
        print("✅ Symbol groups manager imported successfully")
        
        from workflow.group_analysis_engine import GroupAnalysisEngine, GroupAnalysisReporter
        print("✅ Analysis engine imported successfully")
        
        import schedule
        print("✅ Schedule package imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_basic_functionality():
    """Test basic CLI functionality without running the full menu."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from trading_cli import IndicatorSettings, SchedulerSettings
        
        # Test indicator settings
        indicator_settings = IndicatorSettings()
        print(f"✅ Indicator settings created: {len(indicator_settings.settings)} settings")
        
        # Test scheduler settings
        scheduler_settings = SchedulerSettings()
        print(f"✅ Scheduler settings created: {len(scheduler_settings.settings)} settings")
        
        # Test symbol groups manager
        from symbol_groups_manager import SymbolGroupManager
        manager = SymbolGroupManager()
        groups = manager.list_groups()
        print(f"✅ Symbol groups manager working: {len(groups)} groups found")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {str(e)}")
        return False

def demo_indicator_settings():
    """Demonstrate indicator settings functionality."""
    print("\n📊 Demonstrating Indicator Settings...")
    
    from trading_cli import IndicatorSettings
    
    settings = IndicatorSettings()
    print("Default settings:")
    for key, value in settings.settings.items():
        print(f"  {key}: {value}")
    
    # Test updating settings
    settings.update_setting("lookback_period", 10)
    settings.update_setting("adx_threshold", 25)
    settings.update_setting("crossover_indicators.rsi", True)
    
    print("\nUpdated settings:")
    print(f"  lookback_period: {settings.settings['lookback_period']}")
    print(f"  adx_threshold: {settings.settings['adx_threshold']}")
    print(f"  rsi crossover: {settings.settings['crossover_indicators']['rsi']}")

def demo_scheduler_settings():
    """Demonstrate scheduler settings functionality."""
    print("\n📅 Demonstrating Scheduler Settings...")
    
    from trading_cli import SchedulerSettings
    
    settings = SchedulerSettings()
    print("Default scheduler settings:")
    for key, value in settings.settings.items():
        print(f"  {key}: {value}")

def create_sample_group():
    """Create a sample symbol group for testing."""
    print("\n🏗️ Creating a sample symbol group...")
    
    try:
        from symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig
        from datetime import datetime
        
        manager = SymbolGroupManager()
        
        # Create sample symbols
        symbols = {
            "eurusd_15m": SymbolConfig(
                symbol="eurusd",
                asset_type="forex",
                timeframe="15m",
                period="5d",
                enabled=True
            ),
            "gbpusd_15m": SymbolConfig(
                symbol="gbpusd",
                asset_type="forex",
                timeframe="15m",
                period="5d",
                enabled=True
            )
        }
        
        # Create the group
        group = SymbolGroup(
            group_id="demo_forex_group",
            name="Demo Forex Group",
            description="Sample forex group for CLI testing",
            symbols=symbols,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            enabled=True,
            tags=["demo", "forex"],
            metadata={
                "periodic_alerts": True,
                "auto_run_enabled": False,
                "schedule_interval": 15,
                "schedule_weekdays": [0, 1, 2, 3, 4]
            }
        )
        
        # Save the group
        success = manager.save_group(group)
        if success:
            print(f"✅ Sample group '{group.name}' created successfully!")
            print(f"   Group ID: {group.group_id}")
            print(f"   Symbols: {len(group.symbols)}")
        else:
            print("❌ Failed to create sample group")
            
        return success
        
    except Exception as e:
        print(f"❌ Error creating sample group: {str(e)}")
        return False

def main():
    """Main demo function."""
    print("🚀 Trading CLI Demo Script")
    print("=" * 50)
    
    # Test imports
    if not test_cli_imports():
        print("❌ CLI imports failed. Cannot continue.")
        return
    
    # Test basic functionality
    if not test_basic_functionality():
        print("❌ Basic functionality test failed.")
        return
    
    # Demo settings
    demo_indicator_settings()
    demo_scheduler_settings()
    
    # Create sample group
    create_sample_group()
    
    print("\n" + "=" * 50)
    print("✅ All demo tests completed successfully!")
    print("\nTo run the full CLI, execute:")
    print("python trading_cli.py")
    print("\n📋 Available CLI features:")
    print("  • Single symbol analysis")
    print("  • Symbol group analysis")
    print("  • Group creation and management")
    print("  • Indicator settings configuration")
    print("  • Periodic analysis scheduling")
    print("  • Real-time alerts and monitoring")

if __name__ == "__main__":
    main()
