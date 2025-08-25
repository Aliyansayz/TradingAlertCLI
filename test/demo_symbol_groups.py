"""
Demo script for Symbol Groups Management System

This script demonstrates the complete symbol groups management system:
- Creating symbol groups
- Running analysis on groups
- Managing groups (CRUD operations)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig
from group_analysis_engine import GroupAnalysisEngine, GroupAnalysisReporter
from datetime import datetime

def create_demo_groups(manager: SymbolGroupManager):
    """Create demonstration groups with various configurations."""
    
    print("🏗️  Creating demonstration groups...")
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    # Group 1: Major Forex Pairs - Multiple timeframes
    forex_group = SymbolGroup(
        group_id="major_forex",
        name="Major Forex Pairs",
        description="Major currency pairs with different timeframes for scalping and swing trading",
        symbols={
            "eurusd_1m": SymbolConfig(
                symbol="EURUSD",
                asset_type="forex",
                timeframe="1m",
                period="1d",
                enabled=True
            ),
            "eurusd_15m": SymbolConfig(
                symbol="EURUSD",
                asset_type="forex", 
                timeframe="15m",
                period="5d",
                enabled=True
            ),
            "gbpusd_15m": SymbolConfig(
                symbol="GBPUSD",
                asset_type="forex",
                timeframe="15m",
                period="5d",
                enabled=True
            ),
            "usdjpy_15m": SymbolConfig(
                symbol="USDJPY",
                asset_type="forex",
                timeframe="15m",
                period="5d",
                enabled=True
            ),
            "audusd_1h": SymbolConfig(
                symbol="AUDUSD",
                asset_type="forex",
                timeframe="1h",
                period="1mo",
                enabled=True
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["forex", "major_pairs", "scalping", "swing"]
    )
    
    # Group 2: US Indices - Different periods
    indices_group = SymbolGroup(
        group_id="us_indices",
        name="US Stock Indices", 
        description="Major US stock market indices for trend analysis",
        symbols={
            "us30_30m": SymbolConfig(
                symbol="US30",
                asset_type="indices",
                timeframe="30m",
                period="5d",
                enabled=True
            ),
            "us500_30m": SymbolConfig(
                symbol="US500",
                asset_type="indices",
                timeframe="30m", 
                period="5d",
                enabled=True
            ),
            "nasdaq_1h": SymbolConfig(
                symbol="NASDAQ",
                asset_type="indices",
                timeframe="1h",
                period="1mo",
                enabled=True
            ),
            "russell_1h": SymbolConfig(
                symbol="RUSSELL",
                asset_type="indices",
                timeframe="1h",
                period="1mo",
                enabled=False  # Disabled for demo
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["indices", "us_market", "trend_analysis"]
    )
    
    # Group 3: Cryptocurrency Portfolio
    crypto_group = SymbolGroup(
        group_id="crypto_portfolio",
        name="Crypto Portfolio",
        description="Major cryptocurrencies for portfolio analysis",
        symbols={
            "btc_1h": SymbolConfig(
                symbol="BTC",
                asset_type="crypto",
                timeframe="1h",
                period="1mo",
                enabled=True
            ),
            "eth_1h": SymbolConfig(
                symbol="ETH",
                asset_type="crypto",
                timeframe="1h",
                period="1mo",
                enabled=True
            ),
            "ada_4h": SymbolConfig(
                symbol="ADA",
                asset_type="crypto",
                timeframe="4h",
                period="2mo",
                enabled=True
            ),
            "sol_4h": SymbolConfig(
                symbol="SOL",
                asset_type="crypto",
                timeframe="4h",
                period="2mo",
                enabled=False  # Disabled for demo
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["crypto", "portfolio", "digital_assets"]
    )
    
    # Group 4: Tech Stocks
    tech_stocks_group = SymbolGroup(
        group_id="tech_stocks",
        name="Technology Stocks",
        description="Major technology company stocks",
        symbols={
            "aapl_1d": SymbolConfig(
                symbol="AAPL",
                asset_type="stocks",
                timeframe="1d",
                period="3mo",
                enabled=True
            ),
            "msft_1d": SymbolConfig(
                symbol="MSFT",
                asset_type="stocks",
                timeframe="1d",
                period="3mo",
                enabled=True
            ),
            "googl_1d": SymbolConfig(
                symbol="GOOGL",
                asset_type="stocks",
                timeframe="1d",
                period="3mo",
                enabled=True
            ),
            "tsla_1d": SymbolConfig(
                symbol="TSLA",
                asset_type="stocks",
                timeframe="1d",
                period="3mo",
                enabled=False  # Disabled for demo
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["stocks", "technology", "large_cap"]
    )
    
    # Save all groups
    groups = [forex_group, indices_group, crypto_group, tech_stocks_group]
    for group in groups:
        success = manager.save_group(group)
        status = "✅" if success else "❌"
        print(f"   {status} {group.name} ({group.group_id})")
    
    print(f"✅ Created {len(groups)} demonstration groups")
    return groups

def demonstrate_crud_operations(manager: SymbolGroupManager):
    """Demonstrate CRUD operations on groups."""
    
    print("\n📝 Demonstrating CRUD Operations...")
    
    # READ - List all groups
    print("\n1️⃣ LIST GROUPS:")
    groups = manager.list_groups()
    for group in groups:
        enabled_count = len(group.get_enabled_symbols())
        total_count = len(group.symbols)
        status = "🟢" if group.enabled else "🔴"
        print(f"   {status} {group.group_id:<15} | {group.name:<25} | {enabled_count}/{total_count} symbols")
    
    # UPDATE - Modify a group
    print("\n2️⃣ UPDATE GROUP:")
    tech_group = manager.get_group("tech_stocks")
    if tech_group:
        # Enable TSLA symbol
        if "tsla_1d" in tech_group.symbols:
            tech_group.symbols["tsla_1d"].enabled = True
            tech_group.description += " (Updated to include TSLA)"
            tech_group.metadata["last_updated"] = datetime.now().isoformat()
            
            success = manager.save_group(tech_group)
            status = "✅" if success else "❌"
            print(f"   {status} Updated tech_stocks group - enabled TSLA")
    
    # CREATE - Add a new symbol to existing group
    print("\n3️⃣ ADD SYMBOL TO GROUP:")
    forex_group = manager.get_group("major_forex")
    if forex_group:
        # Add USDCAD
        forex_group.symbols["usdcad_15m"] = SymbolConfig(
            symbol="USDCAD",
            asset_type="forex",
            timeframe="15m",
            period="5d",
            enabled=True
        )
        
        success = manager.save_group(forex_group)
        status = "✅" if success else "❌"
        print(f"   {status} Added USDCAD to major_forex group")
    
    # DELETE - Remove a symbol (not the whole group)
    print("\n4️⃣ REMOVE SYMBOL FROM GROUP:")
    crypto_group = manager.get_group("crypto_portfolio")
    if crypto_group and "sol_4h" in crypto_group.symbols:
        del crypto_group.symbols["sol_4h"]
        
        success = manager.save_group(crypto_group)
        status = "✅" if success else "❌"
        print(f"   {status} Removed SOL from crypto_portfolio group")

def demonstrate_analysis(manager: SymbolGroupManager, engine: GroupAnalysisEngine):
    """Demonstrate group analysis capabilities."""
    
    print("\n🔍 Demonstrating Group Analysis...")
    
    # Single group analysis
    print("\n1️⃣ SINGLE GROUP ANALYSIS:")
    indices_group = manager.get_group("us_indices")
    if indices_group:
        print(f"Analyzing: {indices_group.name}")
        result = engine.analyze_group(indices_group)
        GroupAnalysisReporter.print_group_result(result, detailed=False)
    
    # Multiple groups analysis
    print("\n2️⃣ MULTIPLE GROUPS ANALYSIS:")
    group_ids = ["major_forex", "crypto_portfolio"]
    results = engine.analyze_multiple_groups(group_ids, manager)
    GroupAnalysisReporter.print_multiple_groups_summary(results)
    
    # Detailed analysis for one group
    print("\n3️⃣ DETAILED ANALYSIS EXAMPLE:")
    forex_group = manager.get_group("major_forex")
    if forex_group:
        print(f"Detailed analysis for: {forex_group.name}")
        result = engine.analyze_group(forex_group)
        
        # Show detailed results for one symbol
        if result.symbol_results:
            symbol_key = list(result.symbol_results.keys())[0]
            symbol_result = result.symbol_results[symbol_key]
            
            print(f"\n📊 Detailed results for {symbol_key}:")
            print(f"   Symbol: {symbol_result.symbol} ({symbol_result.asset_type})")
            print(f"   Timeframe: {symbol_result.timeframe}, Period: {symbol_result.period}")
            print(f"   Success: {symbol_result.success}")
            print(f"   Data Points: {symbol_result.data_points}")
            print(f"   Latest Price: ${symbol_result.latest_price:.4f}")
            print(f"   Price Change: {symbol_result.price_change:+.4f} ({symbol_result.price_change_pct:+.2f}%)")
            print(f"   Overall Sentiment: {symbol_result.overall_sentiment}")
            
            if symbol_result.indicators:
                print(f"   Key Indicators:")
                for indicator, value in list(symbol_result.indicators.items())[:5]:  # Show first 5
                    print(f"     {indicator}: {value:.4f}")
            
            if symbol_result.oscillator_status:
                print(f"   Oscillator Signals:")
                for oscillator, status_data in list(symbol_result.oscillator_status.items())[:3]:  # Show first 3
                    status = status_data.get('status', 'Unknown')
                    value = status_data.get('value', 0)
                    print(f"     {oscillator}: {status} (Value: {value:.4f})")

def main():
    """Main demonstration function."""
    
    print("🚀 Symbol Groups Management System Demo")
    print("="*80)
    
    # Initialize components
    manager = SymbolGroupManager()
    engine = GroupAnalysisEngine(max_workers=3)
    
    try:
        # Step 1: Create demo groups
        demo_groups = create_demo_groups(manager)
        
        # Step 2: Demonstrate CRUD operations
        demonstrate_crud_operations(manager)
        
        # Step 3: Demonstrate analysis
        demonstrate_analysis(manager, engine)
        
        print("\n" + "="*80)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("="*80)
        
        # Show final summary
        print("\n📋 Final Groups Summary:")
        groups = manager.list_groups()
        for group in groups:
            enabled_symbols = group.get_enabled_symbols()
            status = "🟢" if group.enabled else "🔴"
            print(f"   {status} {group.group_id:<15} | {group.name:<25} | {len(enabled_symbols)} enabled symbols")
            
            # Show enabled symbols
            for symbol_key, config in list(enabled_symbols.items())[:3]:  # Show first 3
                print(f"      └─ {symbol_key}: {config.symbol} ({config.timeframe})")
            if len(enabled_symbols) > 3:
                print(f"      └─ ... and {len(enabled_symbols) - 3} more")
        
        print(f"\n💾 All group data stored in: {manager.storage_path}")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
