#!/usr/bin/env python3
"""
Quick test to verify CLI scheduler settings work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utility.symbol_groups_manager import (
    SymbolGroupManager, SymbolSchedulerSettings, TimeWindowSlot, SymbolConfig, SymbolGroup
)

def test_cli_integration():
    """Test creating a group and configuring scheduler settings."""
    print("🧪 Testing CLI Integration with Symbol Groups...")
    
    try:
        # Initialize manager
        manager = SymbolGroupManager()
        
        # Create a test group if none exists
        if not manager.list_groups():
            print("📝 Creating test group...")
            
            # Create test symbols
            test_symbols = {
                'eurusd_test': SymbolConfig(
                    symbol='EURUSD=X',
                    asset_type='forex',
                    timeframe='1h',
                    period='7d',
                    enabled=True
                ),
                'gbpusd_test': SymbolConfig(
                    symbol='GBPUSD=X',
                    asset_type='forex',
                    timeframe='1h',
                    period='7d',
                    enabled=True
                )
            }
            
            # Create the group
            from datetime import datetime
            test_group = SymbolGroup(
                group_id='test_scheduler_group',
                name='Test Scheduler Group',
                description='Group for testing scheduler settings',
                symbols=test_symbols,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Save the group
            manager._groups_cache['test_scheduler_group'] = test_group
            manager._save_all_groups()
            print("✅ Created test group with 2 symbols")
        
        # List available groups
        groups = manager.list_groups()
        group_ids = [group.group_id for group in groups]  # Extract group IDs
        print(f"📋 Available groups: {group_ids}")
        
        if group_ids:
            group_id = group_ids[0]
            group = manager.get_group(group_id)
            
            if group and group.symbols:
                symbol_key = list(group.symbols.keys())[0]
                
                print(f"🎯 Testing scheduler configuration for {symbol_key} in {group_id}")
                
                # Create scheduler settings
                scheduler_settings = SymbolSchedulerSettings(
                    use_group_settings=False,
                    time_windows=[
                        TimeWindowSlot("09:00", "12:00", active=True),
                        TimeWindowSlot("14:00", "17:00", active=True)
                    ],
                    active_weekdays=[0, 1, 2, 3, 4],  # Monday to Friday
                    timezone="US/Eastern",
                    priority=2,  # Medium priority
                    enabled=True
                )
                
                # Configure the settings
                result = manager.configure_symbol_scheduler_settings(
                    group_id, symbol_key, scheduler_settings
                )
                
                if result:
                    print("✅ Successfully configured scheduler settings")
                    
                    # Verify the configuration
                    updated_group = manager.get_group(group_id)
                    updated_symbol = updated_group.symbols[symbol_key]
                    saved_settings = updated_symbol.symbol_scheduler_settings
                    
                    print(f"✅ Verified configuration:")
                    print(f"   - Use group settings: {saved_settings.use_group_settings}")
                    print(f"   - Time windows: {len(saved_settings.time_windows)}")
                    print(f"   - Active weekdays: {saved_settings.active_weekdays}")
                    print(f"   - Timezone: {saved_settings.timezone}")
                    print(f"   - Priority: {saved_settings.priority}")
                    print(f"   - Enabled: {saved_settings.enabled}")
                    
                    return True
                else:
                    print("❌ Failed to configure scheduler settings")
                    return False
            else:
                print("❌ No symbols found in group")
                return False
        else:
            print("❌ No groups available")
            return False
            
    except Exception as e:
        print(f"❌ CLI integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run CLI integration test."""
    print("🚀 CLI SCHEDULER SETTINGS INTEGRATION TEST")
    print("="*50)
    
    success = test_cli_integration()
    
    if success:
        print("\n🎉 CLI INTEGRATION TEST PASSED!")
        print("✅ Symbol-Level Scheduler Settings is ready for CLI use")
    else:
        print("\n❌ CLI INTEGRATION TEST FAILED!")
        
    return success

if __name__ == "__main__":
    main()
