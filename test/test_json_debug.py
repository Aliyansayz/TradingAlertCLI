#!/usr/bin/env python3
"""
Quick test for JSON serialization issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.symbol_groups_manager import SymbolSchedulerSettings, TimeWindowSlot

def test_json_issue():
    print("🧪 Testing JSON serialization issue...")
    
    # Create scheduler with specific settings
    print("Creating scheduler...")
    scheduler = SymbolSchedulerSettings(
        use_group_settings=False,
        time_windows=[
            TimeWindowSlot("09:30", "11:30", active=True),
            TimeWindowSlot("14:00", "16:00", active=True)
        ],
        active_weekdays=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
        timezone="Asia/Tokyo",
        priority=3,
        enabled=True
    )
    
    print(f"After creation - weekday_names: {scheduler.weekday_names}")
    print(f"After creation - time_descriptions: {scheduler.time_window_descriptions}")
    
    # Convert to dict
    data = scheduler.to_dict()
    print(f"Dict weekday_names: {data.get('weekday_names')}")
    print(f"Dict time_descriptions: {data.get('time_window_descriptions')}")
    
    # Convert back
    restored = SymbolSchedulerSettings.from_dict(data)
    print(f"Restored weekday_names: {restored.weekday_names}")
    print(f"Restored time_descriptions: {restored.time_window_descriptions}")
    
    # Check if they match
    if restored.weekday_names == scheduler.weekday_names:
        print("✅ Weekday names match!")
    else:
        print("❌ Weekday names don't match!")
        print(f"   Original: {scheduler.weekday_names}")
        print(f"   Restored: {restored.weekday_names}")

if __name__ == "__main__":
    test_json_issue()
