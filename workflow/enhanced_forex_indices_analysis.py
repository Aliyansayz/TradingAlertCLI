"""
Enhanced Forex and Indices Analysis Demo

This script focuses on analyzing forex and indices groups with:
- Individual element detailed analysis
- Last 7 prices tracking
- Complete indicator and oscillator status
- ATR-based stop loss/take profit levels
- Cumulative group sentiment analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig
from workflow.group_analysis_engine import GroupAnalysisEngine, GroupAnalysisReporter
from datetime import datetime

def create_focused_groups(manager: SymbolGroupManager):
    """Create focused groups for forex and indices analysis."""
    
    print("🏗️  Creating focused forex and indices groups...")
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    # Group 1: Major Forex Pairs - Multiple timeframes
    forex_group = SymbolGroup(
        group_id="forex_analysis",
        name="Forex Analysis Group",
        description="Major forex pairs for detailed technical analysis",
        symbols={
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
            ),
            "usdjpy_30m": SymbolConfig(
                symbol="usdjpy",
                asset_type="forex",
                timeframe="30m",
                period="1mo",
                enabled=True
            ),
            "audusd_1h": SymbolConfig(
                symbol="audusd",
                asset_type="forex",
                timeframe="1h",
                period="1mo",
                enabled=True
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["forex", "major_pairs", "technical_analysis"]
    )
    
    # Group 2: Major Indices
    indices_group = SymbolGroup(
        group_id="indices_analysis",
        name="Indices Analysis Group", 
        description="Major stock indices for trend and momentum analysis",
        symbols={
            "dow30": SymbolConfig(
                symbol="dow30",
                asset_type="indices",
                timeframe="30m",
                period="5d",
                enabled=True
            ),
            "sp500": SymbolConfig(
                symbol="sp500",
                asset_type="indices",
                timeframe="30m", 
                period="5d",
                enabled=True
            ),
            "nasdaq": SymbolConfig(
                symbol="nasdaq",
                asset_type="indices",
                timeframe="1h",
                period="1mo",
                enabled=True
            )
        },
        created_at=now,
        updated_at=now,
        enabled=True,
        tags=["indices", "trend_analysis", "momentum"]
    )
    
    # Save groups
    groups = [forex_group, indices_group]
    for group in groups:
        success = manager.save_group(group)
        status = "✅" if success else "❌"
        print(f"   {status} {group.name} ({group.group_id})")
    
    print(f"✅ Created {len(groups)} focused analysis groups")
    return groups

def detailed_individual_analysis(result, symbol_result):
    """Show detailed individual element analysis."""
    
    print(f"\n{'='*80}")
    print(f"🔍 DETAILED INDIVIDUAL ANALYSIS: {symbol_result.symbol_key}")
    print(f"{'='*80}")
    
    # Basic Information
    print(f"📋 Basic Information:")
    print(f"   Symbol: {symbol_result.symbol} ({symbol_result.asset_type.upper()})")
    print(f"   Timeframe: {symbol_result.timeframe}")
    print(f"   Period: {symbol_result.period}")
    print(f"   Data Points: {symbol_result.data_points}")
    print(f"   Analysis Time: {symbol_result.analysis_timestamp}")
    
    # Price Analysis
    print(f"\n💰 Price Analysis:")
    print(f"   Current Price: ${symbol_result.latest_price:.4f}")
    print(f"   Price Change: {symbol_result.price_change:+.4f} ({symbol_result.price_change_pct:+.2f}%)")
    
    # Last 7 Prices
    if symbol_result.last_7_prices:
        print(f"\n📈 Last 7 Prices History:")
        for i, price in enumerate(reversed(symbol_result.last_7_prices), 1):
            change_from_current = price - symbol_result.latest_price
            change_pct = (change_from_current / symbol_result.latest_price) * 100
            print(f"   -{i}: ${price:.4f} ({change_from_current:+.4f}, {change_pct:+.1f}%)")
    
    # Technical Indicators
    if symbol_result.indicators:
        print(f"\n📊 Technical Indicators:")
        for indicator, value in symbol_result.indicators.items():
            print(f"   {indicator}: {value:.4f}")
    
    # Oscillator Status Details
    if symbol_result.oscillator_status:
        print(f"\n🎯 Oscillator Status (Individual Elements):")
        buy_signals = 0
        sell_signals = 0
        neutral_signals = 0
        
        for oscillator, status_data in symbol_result.oscillator_status.items():
            status = status_data.get('status', 'Unknown')
            value = status_data.get('value', 0)
            prev_value = status_data.get('previous_value')
            
            # Count signals
            if status == 'Buy':
                buy_signals += 1
                signal_emoji = "🟢"
            elif status == 'Sell':
                sell_signals += 1
                signal_emoji = "🔴"
            else:
                neutral_signals += 1
                signal_emoji = "🟡"
            
            # Trend analysis
            trend = ""
            if prev_value is not None:
                if value > prev_value:
                    trend = " ↗️ Rising"
                elif value < prev_value:
                    trend = " ↘️ Falling"
                else:
                    trend = " ➡️ Stable"
            
            print(f"   {signal_emoji} {oscillator}:")
            print(f"      Status: {status}")
            print(f"      Value: {value:.4f}{trend}")
            if prev_value is not None:
                print(f"      Previous: {prev_value:.4f}")
        
        # Cumulative Status Summary
        total_signals = buy_signals + sell_signals + neutral_signals
        print(f"\n📊 Cumulative Oscillator Status:")
        print(f"   🟢 Buy Signals: {buy_signals}/{total_signals} ({buy_signals/total_signals*100:.1f}%)")
        print(f"   🔴 Sell Signals: {sell_signals}/{total_signals} ({sell_signals/total_signals*100:.1f}%)")
        print(f"   🟡 Neutral Signals: {neutral_signals}/{total_signals} ({neutral_signals/total_signals*100:.1f}%)")
        
        # Overall sentiment determination
        if buy_signals > sell_signals:
            overall_sentiment = "BULLISH"
            sentiment_emoji = "🟢"
        elif sell_signals > buy_signals:
            overall_sentiment = "BEARISH" 
            sentiment_emoji = "🔴"
        else:
            overall_sentiment = "NEUTRAL"
            sentiment_emoji = "🟡"
        
        print(f"   {sentiment_emoji} Overall Sentiment: {overall_sentiment}")
    
    # ATR Trading Levels
    if symbol_result.atr_bands:
        print(f"\n🎯 ATR Trading Levels:")
        atr_value = symbol_result.atr_bands.get('atr_value', 0)
        print(f"   ATR(14): {atr_value:.4f}")
        
        print(f"\n   📊 ATR Bands:")
        print(f"   Upper Band (2.0x): ${symbol_result.atr_bands.get('upper_band_2x', 0):.4f}")
        print(f"   Upper Band (1.5x): ${symbol_result.atr_bands.get('upper_band_1.5x', 0):.4f}")
        print(f"   Current Price:     ${symbol_result.latest_price:.4f}")
        print(f"   Lower Band (1.5x): ${symbol_result.atr_bands.get('lower_band_1.5x', 0):.4f}")
        print(f"   Lower Band (2.0x): ${symbol_result.atr_bands.get('lower_band_2x', 0):.4f}")
        
        # Trading recommendations based on sentiment
        if symbol_result.overall_sentiment == "BULLISH":
            stop_loss = symbol_result.atr_bands.get('stop_loss_long', 0)
            take_profit = symbol_result.atr_bands.get('take_profit_long', 0)
            risk = symbol_result.latest_price - stop_loss
            reward = take_profit - symbol_result.latest_price
            risk_reward = reward / risk if risk > 0 else 0
            
            print(f"\n   🟢 LONG Trading Setup:")
            print(f"   Entry: ${symbol_result.latest_price:.4f}")
            print(f"   Stop Loss: ${stop_loss:.4f} (Risk: ${risk:.4f})")
            print(f"   Take Profit: ${take_profit:.4f} (Reward: ${reward:.4f})")
            print(f"   Risk/Reward Ratio: 1:{risk_reward:.1f}")
            
        elif symbol_result.overall_sentiment == "BEARISH":
            stop_loss = symbol_result.atr_bands.get('stop_loss_short', 0)
            take_profit = symbol_result.atr_bands.get('take_profit_short', 0)
            risk = stop_loss - symbol_result.latest_price
            reward = symbol_result.latest_price - take_profit
            risk_reward = reward / risk if risk > 0 else 0
            
            print(f"\n   🔴 SHORT Trading Setup:")
            print(f"   Entry: ${symbol_result.latest_price:.4f}")
            print(f"   Stop Loss: ${stop_loss:.4f} (Risk: ${risk:.4f})")
            print(f"   Take Profit: ${take_profit:.4f} (Reward: ${reward:.4f})")
            print(f"   Risk/Reward Ratio: 1:{risk_reward:.1f}")

def enhanced_group_sentiment_analysis(result):
    """Show enhanced group sentiment with individual element breakdown."""
    
    print(f"\n{'='*80}")
    print(f"🎯 ENHANCED GROUP SENTIMENT ANALYSIS: {result.group_name}")
    print(f"{'='*80}")
    
    # Group overview
    print(f"📊 Group Overview:")
    print(f"   Total Symbols: {result.total_symbols}")
    print(f"   Successful Analyses: {result.successful_analyses}")
    print(f"   Failed Analyses: {result.failed_analyses}")
    print(f"   Success Rate: {result.successful_analyses/result.total_symbols*100:.1f}%")
    
    # Individual element sentiments
    print(f"\n🔍 Individual Element Sentiments:")
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    
    for symbol_key, symbol_result in result.symbol_results.items():
        if symbol_result.success:
            sentiment = symbol_result.overall_sentiment
            if sentiment == "BULLISH":
                bullish_count += 1
                emoji = "🟢"
            elif sentiment == "BEARISH":
                bearish_count += 1
                emoji = "🔴"
            else:
                neutral_count += 1
                emoji = "🟡"
            
            print(f"   {emoji} {symbol_key:<15}: {sentiment:<8} (Buy:{symbol_result.signals_summary['Buy']}, "
                  f"Sell:{symbol_result.signals_summary['Sell']}, Neutral:{symbol_result.signals_summary['Neutral']})")
    
    # Group sentiment summary
    total_successful = bullish_count + bearish_count + neutral_count
    if total_successful > 0:
        print(f"\n📈 Group Sentiment Breakdown:")
        print(f"   🟢 Bullish Elements: {bullish_count}/{total_successful} ({bullish_count/total_successful*100:.1f}%)")
        print(f"   🔴 Bearish Elements: {bearish_count}/{total_successful} ({bearish_count/total_successful*100:.1f}%)")
        print(f"   🟡 Neutral Elements: {neutral_count}/{total_successful} ({neutral_count/total_successful*100:.1f}%)")
        
        # Overall group sentiment
        if bullish_count > bearish_count:
            group_sentiment = "BULLISH"
            sentiment_emoji = "🟢"
        elif bearish_count > bullish_count:
            group_sentiment = "BEARISH"
            sentiment_emoji = "🔴"
        else:
            group_sentiment = "NEUTRAL"
            sentiment_emoji = "🟡"
        
        print(f"\n   {sentiment_emoji} Overall Group Sentiment: {group_sentiment}")
        
        # Group signals aggregation
        total_buy = sum(r.signals_summary['Buy'] for r in result.symbol_results.values() if r.success)
        total_sell = sum(r.signals_summary['Sell'] for r in result.symbol_results.values() if r.success)
        total_neutral = sum(r.signals_summary['Neutral'] for r in result.symbol_results.values() if r.success)
        total_signals = total_buy + total_sell + total_neutral
        
        if total_signals > 0:
            print(f"\n📊 Cumulative Group Signals:")
            print(f"   🟢 Total Buy Signals: {total_buy}/{total_signals} ({total_buy/total_signals*100:.1f}%)")
            print(f"   🔴 Total Sell Signals: {total_sell}/{total_signals} ({total_sell/total_signals*100:.1f}%)")
            print(f"   🟡 Total Neutral Signals: {total_neutral}/{total_signals} ({total_neutral/total_signals*100:.1f}%)")

def main():
    """Main enhanced analysis function."""
    
    print("🚀 Enhanced Forex and Indices Analysis")
    print("="*80)
    
    # Initialize components
    manager = SymbolGroupManager()
    engine = GroupAnalysisEngine(max_workers=3)
    
    try:
        # Step 1: Create focused groups
        demo_groups = create_focused_groups(manager)
        
        # Step 2: Analyze forex group with detailed breakdown
        print(f"\n{'='*80}")
        print("🔍 FOREX GROUP ANALYSIS")
        print("="*80)
        
        forex_group = manager.get_group("forex_analysis")
        if forex_group:
            result = engine.analyze_group(forex_group)
            GroupAnalysisReporter.print_group_result(result, detailed=True)
            
            # Enhanced group sentiment analysis
            enhanced_group_sentiment_analysis(result)
            
            # Show detailed analysis for each successful symbol
            print(f"\n{'='*80}")
            print("📊 INDIVIDUAL FOREX ELEMENTS DETAILED ANALYSIS")
            print("="*80)
            
            for symbol_key, symbol_result in result.symbol_results.items():
                if symbol_result.success:
                    detailed_individual_analysis(result, symbol_result)
        
        # Step 3: Analyze indices group with detailed breakdown
        print(f"\n{'='*80}")
        print("🔍 INDICES GROUP ANALYSIS")
        print("="*80)
        
        indices_group = manager.get_group("indices_analysis")
        if indices_group:
            result = engine.analyze_group(indices_group)
            GroupAnalysisReporter.print_group_result(result, detailed=True)
            
            # Enhanced group sentiment analysis
            enhanced_group_sentiment_analysis(result)
            
            # Show detailed analysis for each successful symbol
            print(f"\n{'='*80}")
            print("📊 INDIVIDUAL INDICES ELEMENTS DETAILED ANALYSIS")
            print("="*80)
            
            for symbol_key, symbol_result in result.symbol_results.items():
                if symbol_result.success:
                    detailed_individual_analysis(result, symbol_result)
        
        print(f"\n{'='*80}")
        print("✅ ENHANCED ANALYSIS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Analysis failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
