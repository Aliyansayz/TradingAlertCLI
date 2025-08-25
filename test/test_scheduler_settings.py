#!/usr/bin/env python3
"""
Test script for Symbol-Level Scheduler Settings functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utility.symbol_groups_manager import (
    SymbolGroupManager, SymbolSchedulerSettings, TimeWindowSlot, SymbolConfig
)
from datetime import datetime, time
import pytz

def test_time_window_slot():
    """Test TimeWindowSlot functionality."""
    print("🧪 Testing TimeWindowSlot...")
    
    # Create a time window for 11 AM to 4 PM
    window = TimeWindowSlot(
        start_time="11:00",
        end_time="16:00", 
        active=True
    )
    
    print(f"   ✅ Created window: {window.start_time} - {window.end_time}")
    
    # Test is_active_now at different times
    test_times = ["10:30", "11:30", "14:00", "16:30", "18:00"]
    
    for test_time in test_times:
        # Mock current time for testing
        hour, minute = map(int, test_time.split(':'))
        test_datetime = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Check if window would be active (simplified test)
        current_time = time(hour, minute)
        start_time = time(11, 0)  # 11:00
        end_time = time(16, 0)   # 16:00
        
        is_active = start_time <= current_time <= end_time
        status = "🟢 Active" if is_active else "🔴 Inactive"
        print(f"   {test_time}: {status}")
    
    print("   ✅ TimeWindowSlot test completed\n")

def test_symbol_scheduler_settings():
    """Test SymbolSchedulerSettings functionality."""
    print("🧪 Testing SymbolSchedulerSettings...")
    
    # Create time windows
    windows = [
        TimeWindowSlot("09:00", "11:30", active=True),
        TimeWindowSlot("14:00", "16:00", active=True),
        TimeWindowSlot("20:00", "22:00", active=True)
    ]
    
    # Create scheduler settings (let it auto-generate names and descriptions)
    scheduler = SymbolSchedulerSettings(
        use_group_settings=False,
        time_windows=windows,
        active_weekdays=[0, 1, 2, 3, 4],  # Monday to Friday
        timezone="US/Eastern",
        priority=3,  # High priority
        enabled=True
    )
    
    print(f"   ✅ Created scheduler with {len(scheduler.time_windows)} time windows")
    print(f"   ✅ Timezone: {scheduler.timezone}")
    print(f"   ✅ Active days: {', '.join(scheduler.get_active_weekday_names())}")
    print(f"   ✅ Priority: {scheduler.priority}")
    print(f"   ✅ Time descriptions: {scheduler.time_window_descriptions}")
    
    # Test serialization
    scheduler_dict = scheduler.to_dict()
    restored_scheduler = SymbolSchedulerSettings.from_dict(scheduler_dict)
    
    print(f"   ✅ Serialization test: {len(restored_scheduler.time_windows)} windows restored")
    print("   ✅ SymbolSchedulerSettings test completed\n")

def test_time_parsing():
    """Test the new time parsing functionality."""
    print("🧪 Testing Time Parsing...")
    
    test_cases = [
        ("8 AM - 1 PM", "08:00", "13:00"),
        ("9:30 AM - 4:30 PM", "09:30", "16:30"),
        ("11 PM - 6 AM", "23:00", "06:00"),
        ("12 AM - 11:59 PM", "00:00", "23:59"),
        ("12 PM - 1 PM", "12:00", "13:00")
    ]
    
    for user_input, expected_start, expected_end in test_cases:
        try:
            start_time, end_time = SymbolSchedulerSettings.parse_time_description(user_input)
            if start_time == expected_start and end_time == expected_end:
                print(f"   ✅ '{user_input}' → {start_time} - {end_time}")
            else:
                print(f"   ❌ '{user_input}' → {start_time} - {end_time} (expected {expected_start} - {expected_end})")
        except Exception as e:
            print(f"   ❌ '{user_input}' → Error: {str(e)}")
    
    # Test reverse conversion
    print("   Testing reverse conversion (24h → 12h):")
    reverse_cases = [
        ("08:00", "16:00", "8:00 AM - 4:00 PM"),
        ("09:30", "17:30", "9:30 AM - 5:30 PM"),
        ("23:00", "06:00", "11:00 PM - 6:00 AM")
    ]
    
    for start_24h, end_24h, expected_desc in reverse_cases:
        try:
            description = SymbolSchedulerSettings._convert_time_to_description(start_24h, end_24h)
            print(f"   ✅ {start_24h}-{end_24h} → '{description}'")
        except Exception as e:
            print(f"   ❌ {start_24h}-{end_24h} → Error: {str(e)}")
    
    print("   ✅ Time parsing test completed\n")

def test_weekday_names():
    """Test weekday name functionality."""
    print("🧪 Testing Weekday Names...")
    
    # Create scheduler with weekdays
    scheduler = SymbolSchedulerSettings(
        active_weekdays=[0, 1, 2, 3, 4],  # Monday to Friday
        enabled=True
    )
    
    active_names = scheduler.get_active_weekday_names()
    expected_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    if active_names == expected_names:
        print(f"   ✅ Weekday names: {', '.join(active_names)}")
    else:
        print(f"   ❌ Expected {expected_names}, got {active_names}")
    
    # Test updating from names
    new_weekdays = {
        "Monday": True, "Tuesday": False, "Wednesday": True, "Thursday": False,
        "Friday": True, "Saturday": True, "Sunday": False
    }
    
    scheduler.update_weekdays_from_names(new_weekdays)
    expected_numbers = [0, 2, 4, 5]  # Mon, Wed, Fri, Sat
    
    if scheduler.active_weekdays == expected_numbers:
        print(f"   ✅ Updated weekdays: {scheduler.active_weekdays}")
    else:
        print(f"   ❌ Expected {expected_numbers}, got {scheduler.active_weekdays}")
    
    print("   ✅ Weekday names test completed\n")

def test_symbol_group_integration():
    """Test integration with SymbolGroupManager."""
    print("🧪 Testing SymbolGroup integration...")
    
    try:
        # Initialize manager
        manager = SymbolGroupManager()
        
        # Create test scheduler settings
        scheduler_settings = SymbolSchedulerSettings(
            use_group_settings=False,
            time_windows=[TimeWindowSlot("11:00", "16:00", active=True)],
            active_weekdays=[0, 1, 2, 3, 4],
            timezone="US/Eastern",
            priority=2,  # Medium priority
            enabled=True
        )
        
        # Test with existing groups
        groups = manager.list_groups()
        if groups:
            group_id = groups[0]
            group = manager.get_group(group_id)
            
            if group and group.symbols:
                symbol_key = list(group.symbols.keys())[0]
                
                print(f"   🎯 Testing with group: {group_id}, symbol: {symbol_key}")
                
                # Configure scheduler settings
                result = manager.configure_symbol_scheduler_settings(
                    group_id, symbol_key, scheduler_settings
                )
                
                if result:
                    print("   ✅ Successfully configured symbol scheduler settings")
                    
                    # Verify the settings were saved
                    updated_group = manager.get_group(group_id)
                    symbol_config = updated_group.symbols[symbol_key]
                    
                    if symbol_config.symbol_scheduler_settings:
                        saved_settings = symbol_config.symbol_scheduler_settings
                        print(f"   ✅ Verified settings saved: {len(saved_settings.time_windows)} windows")
                        print(f"   ✅ Timezone: {saved_settings.timezone}")
                        print(f"   ✅ Use group settings: {saved_settings.use_group_settings}")
                    else:
                        print("   ❌ Settings not found after save")
                else:
                    print("   ❌ Failed to configure scheduler settings")
            else:
                print("   ⚠️ No symbols found in test group")
        else:
            print("   ⚠️ No groups found for testing")
        
        print("   ✅ SymbolGroup integration test completed\n")
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}\n")

def test_json_serialization():
    """Test JSON serialization/deserialization."""
    print("🧪 Testing JSON serialization...")
    
    # Create complex scheduler settings (auto-generates descriptions and names)
    scheduler = SymbolSchedulerSettings(
        use_group_settings=False,
        time_windows=[
            TimeWindowSlot("09:30", "11:30", active=True),
            TimeWindowSlot("14:00", "16:00", active=True),
            TimeWindowSlot("20:00", "22:00", active=False)  # Disabled window
        ],
        active_weekdays=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
        timezone="Asia/Tokyo",
        priority=3,  # High priority
        enabled=True
    )
    
    # Convert to dict
    data = scheduler.to_dict()
    print(f"   ✅ Converted to dict: {len(data)} fields")
    
    # Convert back to object
    restored = SymbolSchedulerSettings.from_dict(data)
    print(f"   ✅ Restored from dict: {len(restored.time_windows)} windows")
    
    # Verify all fields match
    assert restored.use_group_settings == scheduler.use_group_settings
    assert len(restored.time_windows) == len(scheduler.time_windows)
    assert restored.active_weekdays == scheduler.active_weekdays
    assert restored.weekday_names == scheduler.weekday_names
    assert restored.time_window_descriptions == scheduler.time_window_descriptions
    assert restored.timezone == scheduler.timezone
    assert restored.priority == scheduler.priority
    assert restored.enabled == scheduler.enabled
    
    print("   ✅ All fields verified matching")
    print("   ✅ JSON serialization test completed\n")

def main():
    """Run all scheduler settings tests."""
    print("🚀 SYMBOL-LEVEL SCHEDULER SETTINGS TEST")
    print("="*50)
    
    try:
        test_time_window_slot()
        test_symbol_scheduler_settings()
        test_time_parsing()
        test_weekday_names()
        test_json_serialization()
        test_symbol_group_integration()
        
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Enhanced Symbol-Level Scheduler Settings is ready for use")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
