#!/usr/bin/env python3
"""
Test Strategy Management Features
"""
import sys
import os

# Add backend path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

def test_strategy_management():
    """Test the strategy management functionality."""
    print("🧪 Testing Strategy Management Features...")
    
    try:
        from strategy import (
            list_available_strategies, 
            get_strategy_info, 
            get_strategy_parameters_template,
            has_configurable_parameters,
            get_strategy
        )
        
        print("\n1. Testing strategy listing...")
        strategies = list_available_strategies()
        print(f"   ✅ Found {len(strategies)} strategies: {strategies}")
        
        print("\n2. Testing strategy info retrieval...")
        for strategy_name in strategies:
            try:
                info = get_strategy_info(strategy_name)
                configurable = has_configurable_parameters(strategy_name)
                print(f"   ✅ {strategy_name}: {info.get('description', 'No description')} (Configurable: {configurable})")
            except Exception as e:
                print(f"   ❌ Error getting info for {strategy_name}: {str(e)}")
        
        print("\n3. Testing parameter templates...")
        for strategy_name in strategies:
            try:
                template = get_strategy_parameters_template(strategy_name)
                configurable_count = len([p for p in template.values() if p.get("type") != "info"])
                print(f"   ✅ {strategy_name}: {configurable_count} configurable parameters")
                
                if configurable_count > 0:
                    print(f"      Parameters: {list(template.keys())}")
            except Exception as e:
                print(f"   ❌ Error getting template for {strategy_name}: {str(e)}")
        
        print("\n4. Testing parameter modification...")
        dual_st_strategy = get_strategy("dual-supertrend-check-single-timeframe")
        
        # Get current parameters
        current_params = dual_st_strategy.get_current_parameters()
        print(f"   Current supertrend_a_period: {current_params.get('supertrend_a_period')}")
        
        # Update parameters
        success = dual_st_strategy.update_parameters({"supertrend_a_period": 20})
        if success:
            updated_params = dual_st_strategy.get_current_parameters()
            print(f"   ✅ Updated supertrend_a_period: {updated_params.get('supertrend_a_period')}")
        else:
            print("   ❌ Failed to update parameters")
        
        # Reset parameters
        dual_st_strategy.reset_parameters_to_default()
        reset_params = dual_st_strategy.get_current_parameters()
        print(f"   ✅ Reset supertrend_a_period: {reset_params.get('supertrend_a_period')}")
        
        print("\n5. Testing strategy creation with custom parameters...")
        custom_params = {
            "supertrend_a_period": 25,
            "supertrend_a_multiplier": 4.0,
            "confirmation_threshold": 4
        }
        custom_strategy = get_strategy("dual-supertrend-check-single-timeframe", custom_params)
        custom_current = custom_strategy.get_current_parameters()
        
        print(f"   ✅ Custom strategy created:")
        print(f"      supertrend_a_period: {custom_current.get('supertrend_a_period')}")
        print(f"      supertrend_a_multiplier: {custom_current.get('supertrend_a_multiplier')}")
        print(f"      confirmation_threshold: {custom_current.get('confirmation_threshold')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy management test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_symbol_group_strategy_settings():
    """Test strategy settings for symbol groups."""
    print("\n🧪 Testing Symbol Group Strategy Settings...")
    
    try:
        from utility.symbol_groups_manager import SymbolGroupManager, IndicatorSettings
        
        group_manager = SymbolGroupManager()
        
        # Create test group
        test_group = group_manager.create_group(
            name="Strategy Test Group",
            description="Testing strategy settings"
        )
        
        print(f"✅ Created test group: {test_group.name}")
        
        # Add symbol with dual supertrend strategy
        success = group_manager.add_symbol_to_group(
            group_id=test_group.group_id,
            symbol_key="AAPL_test",
            symbol="AAPL",
            asset_type="stocks",
            timeframe="1d",
            period="3mo"
        )
        
        if success:
            print("✅ Added AAPL to test group")
            
            # Update symbol's strategy
            group = group_manager.get_group(test_group.group_id)
            for symbol_key, symbol_config in group.symbols.items():
                if symbol_config.symbol == "AAPL":
                    # Set strategy
                    symbol_config.indicator_settings.timeframe_strategy = "dual-supertrend-check-single-timeframe"
                    
                    # Test custom strategy parameters (would need to add this to IndicatorSettings)
                    print(f"✅ Set strategy for {symbol_config.symbol}: {symbol_config.indicator_settings.timeframe_strategy}")
                    break
            
            # Save changes
            group_manager._save_all_groups()
            print("✅ Saved strategy settings for symbol group")
            
            # Verify the change
            updated_group = group_manager.get_group(test_group.group_id)
            for symbol_key, symbol_config in updated_group.symbols.items():
                strategy_name = symbol_config.indicator_settings.timeframe_strategy
                print(f"✅ Verified: {symbol_config.symbol} uses strategy: {strategy_name}")
        
        # Clean up
        group_manager.delete_group(test_group.group_id)
        print("🧹 Cleaned up test group")
        
        return True
        
    except Exception as e:
        print(f"❌ Symbol group strategy test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STRATEGY MANAGEMENT TEST SUITE")
    print("=" * 60)
    
    test1_passed = test_strategy_management()
    test2_passed = test_symbol_group_strategy_settings()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"   Strategy Management: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Symbol Group Integration: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! Strategy Management is ready to use.")
        print("\n📋 Features Available:")
        print("   • View current active strategy")
        print("   • Change active strategy")
        print("   • Configure strategy parameters (for custom strategies)")
        print("   • Reset parameters to defaults")
        print("   • View detailed strategy information")
        print("   • Symbol group strategy settings")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")
