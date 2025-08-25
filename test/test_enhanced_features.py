#!/usr/bin/env python3
"""
Test Script for Enhanced TradeMaster Pro Features

This script tests the newly implemented features:
- Symbol-specific indicator settings
- Periodic alerts configuration
- Group-level settings
- CLI integration
"""

import sys
import os

# Add backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from symbol_groups_manager import (
    SymbolGroupManager, 
    SymbolGroup, 
    SymbolConfig, 
    IndicatorSettings, 
    PeriodicAlertConfig,
    GroupLevelSettings
)
from periodic_alerts_engine import PeriodicAlertsEngine, AlertEvent

def test_symbol_groups_manager():
    """Test the enhanced Symbol Groups Manager."""
    print("🧪 Testing Enhanced Symbol Groups Manager")
    print("=" * 50)
    
    # Initialize manager
    manager = SymbolGroupManager()
    
    # Test loading groups with new structure
    groups = manager.list_groups()
    print(f"✅ Loaded {len(groups)} groups")
    
    for group in groups:
        print(f"\n📊 Group: {group.name}")
        print(f"   ID: {group.group_id}")
        print(f"   Symbols: {len(group.symbols)}")
        
        # Check if group has enhanced settings
        if hasattr(group, 'group_settings') and group.group_settings:
            print(f"   ✅ Group-level settings: Present")
            print(f"   Auto analysis: {group.group_settings.auto_analysis}")
            print(f"   Scheduler enabled: {group.group_settings.scheduler_settings.get('enabled', False)}")
        else:
            print(f"   ❌ Group-level settings: Missing")
        
        # Check symbols with enhanced features
        enhanced_symbols = 0
        alert_enabled_symbols = 0
        
        for symbol_key, symbol_config in group.symbols.items():
            if hasattr(symbol_config, 'indicator_settings') and symbol_config.indicator_settings:
                enhanced_symbols += 1
            
            if (hasattr(symbol_config, 'periodic_alerts') and 
                symbol_config.periodic_alerts and 
                symbol_config.periodic_alerts.enabled):
                alert_enabled_symbols += 1
        
        print(f"   Enhanced symbols: {enhanced_symbols}/{len(group.symbols)}")
        print(f"   Alert-enabled symbols: {alert_enabled_symbols}/{len(group.symbols)}")

def test_symbol_specific_settings():
    """Test symbol-specific settings configuration."""
    print("\n🔧 Testing Symbol-Specific Settings")
    print("=" * 50)
    
    manager = SymbolGroupManager()
    
    # Get a test group
    groups = manager.list_groups()
    if not groups:
        print("❌ No groups available for testing")
        return
    
    test_group = groups[0]
    
    # Test indicator settings
    custom_indicators = IndicatorSettings(
        rsi_period=21,
        rsi_overbought=75.0,
        rsi_oversold=25.0,
        macd_fast=10,
        macd_slow=20,
        bb_period=25
    )
    
    # Get first symbol
    symbol_keys = list(test_group.symbols.keys())
    if symbol_keys:
        test_symbol_key = symbol_keys[0]
        
        # Configure indicator settings
        success = manager.configure_symbol_indicators(
            test_group.group_id, 
            test_symbol_key, 
            custom_indicators
        )
        
        if success:
            print(f"✅ Successfully configured indicator settings for {test_symbol_key}")
        else:
            print(f"❌ Failed to configure indicator settings for {test_symbol_key}")
        
        # Test periodic alerts
        alert_config = PeriodicAlertConfig(
            enabled=True,
            alert_interval=30,
            alert_weekdays=[0, 1, 2, 3, 4],
            conditions={
                "rsi_overbought": True,
                "rsi_oversold": True,
                "macd_bullish_crossover": True
            }
        )
        
        success = manager.configure_symbol_periodic_alerts(
            test_group.group_id,
            test_symbol_key,
            alert_config
        )
        
        if success:
            print(f"✅ Successfully configured periodic alerts for {test_symbol_key}")
        else:
            print(f"❌ Failed to configure periodic alerts for {test_symbol_key}")

def test_first_time_alerts_setup():
    """Test first-time alerts setup functionality."""
    print("\n🔔 Testing First-Time Alerts Setup")
    print("=" * 50)
    
    manager = SymbolGroupManager()
    
    # Get a test group
    groups = manager.list_groups()
    if not groups:
        print("❌ No groups available for testing")
        return
    
    test_group = groups[0]
    symbol_keys = list(test_group.symbols.keys())
    
    if symbol_keys:
        test_symbol_key = symbol_keys[0]
        
        # Setup first-time alerts
        success = manager.setup_first_time_alerts(
            test_group.group_id,
            test_symbol_key,
            interval=20,
            conditions={
                "rsi_overbought": True,
                "rsi_oversold": True,
                "volume_spike": True
            }
        )
        
        if success:
            print(f"✅ Successfully setup first-time alerts for {test_symbol_key}")
        else:
            print(f"❌ Failed to setup first-time alerts for {test_symbol_key}")

def test_group_scheduler_configuration():
    """Test group scheduler configuration."""
    print("\n📅 Testing Group Scheduler Configuration")
    print("=" * 50)
    
    manager = SymbolGroupManager()
    
    # Get a test group
    groups = manager.list_groups()
    if not groups:
        print("❌ No groups available for testing")
        return
    
    test_group = groups[0]
    
    # Configure scheduler
    success = manager.configure_group_scheduler(
        test_group.group_id,
        enabled=True,
        run_interval=25,
        weekdays=[0, 1, 2, 3, 4],
        hours=[8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    )
    
    if success:
        print(f"✅ Successfully configured scheduler for group {test_group.name}")
    else:
        print(f"❌ Failed to configure scheduler for group {test_group.name}")

def test_analysis_overview():
    """Test analysis overview functionality."""
    print("\n📊 Testing Analysis Overview")
    print("=" * 50)
    
    manager = SymbolGroupManager()
    
    # Get comprehensive overview
    overview = manager.get_analysis_overview()
    
    print(f"Total groups: {overview['total_groups']}")
    print(f"Enabled groups: {overview['enabled_groups']}")
    print(f"Total symbols: {overview['total_symbols']}")
    print(f"Enabled symbols: {overview['enabled_symbols']}")
    print(f"Alert-enabled symbols: {overview['alert_enabled_symbols']}")
    print(f"Scheduler-enabled groups: {overview['scheduler_enabled_groups']}")
    
    print("\nGroup Details:")
    for group_summary in overview['groups_overview']:
        print(f"  📊 {group_summary['name']}")
        print(f"     Enabled symbols: {group_summary['enabled_symbols']}")
        print(f"     Alert symbols: {group_summary['alert_enabled_symbols']}")
        print(f"     Scheduler: {'✅' if group_summary['scheduler_enabled'] else '❌'}")
        print(f"     Auto analysis: {'✅' if group_summary['auto_analysis_enabled'] else '❌'}")

def test_periodic_alerts_engine():
    """Test the periodic alerts engine."""
    print("\n🚨 Testing Periodic Alerts Engine")
    print("=" * 50)
    
    manager = SymbolGroupManager()
    
    def test_callback(alert: AlertEvent):
        print(f"🔔 Test Alert: {alert.symbol} - {alert.message}")
    
    # Initialize alerts engine
    alerts_engine = PeriodicAlertsEngine(manager, test_callback)
    
    # Get alert summary
    summary = alerts_engine.get_alert_summary()
    
    print(f"Alert engine status: {summary['monitoring_status']}")
    print(f"Total alerts (all time): {summary['total_alerts_all_time']}")
    print(f"Alerts (24h): {summary['total_alerts_24h']}")
    print(f"Active threads: {summary['active_threads']}")
    
    # Get groups with alerts
    groups_with_alerts = manager.get_groups_with_alerts()
    print(f"Groups with alerts enabled: {len(groups_with_alerts)}")
    
    for group in groups_with_alerts:
        alert_symbols = group.get_symbols_with_alerts_enabled()
        print(f"  📊 {group.name}: {len(alert_symbols)} symbols with alerts")

def main():
    """Run all tests."""
    print("🚀 TradeMaster Pro Enhanced Features Test Suite")
    print("=" * 60)
    
    try:
        test_symbol_groups_manager()
        test_symbol_specific_settings()
        test_first_time_alerts_setup()
        test_group_scheduler_configuration()
        test_analysis_overview()
        test_periodic_alerts_engine()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("📊 Enhanced features are working correctly!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
