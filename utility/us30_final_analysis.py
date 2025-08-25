"""
US30 Comprehensive Analysis Script

This script runs a complete analysis of US30 (Dow Jones) with 30-minute timeframe,
including latest indicators, oscillator status, and trading signals.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# Import indicators and oscillators
from indicators_oscillators import Oscillator, Oscillator_Status

def fetch_us30_data_fixed(period='7d', interval='30m'):
    """Fetch and properly clean US30 data."""
    symbol = '^DJI'  # Dow Jones Industrial Average
    
    try:
        # Fetch data
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        
        if data.empty:
            return pd.DataFrame()
        
        # Handle MultiIndex columns properly
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten MultiIndex columns
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            # Remove trailing underscores and symbol suffixes
            data.columns = [col.replace(f'_{symbol}', '').rstrip('_') for col in data.columns]
        
        # Standardize column names
        column_mapping = {
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        
        data.rename(columns=column_mapping, inplace=True)
        data = data.dropna()
        
        return data
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def run_comprehensive_us30_analysis():
    """Run comprehensive US30 analysis with all indicators and status."""
    
    print("="*80)
    print("US30 (DOW JONES INDUSTRIAL AVERAGE) COMPREHENSIVE ANALYSIS")
    print("30-MINUTE TIMEFRAME | 7-DAY PERIOD")
    print("="*80)
    
    # Step 1: Fetch data
    print("📊 Fetching US30 data...")
    data = fetch_us30_data_fixed(period='7d', interval='30m')
    
    if data.empty:
        print("❌ Failed to fetch data.")
        return
    
    print(f"✅ Successfully fetched {len(data)} data points")
    print(f"📅 Data range: {data.index[0]} to {data.index[-1]}")
    
    # Step 2: Display last 7 close prices
    print(f"\n{'='*50}")
    print("📈 LAST 7 CLOSE PRICES")
    print(f"{'='*50}")
    
    last_7_closes = data['close'].tail(7)
    for i, (timestamp, close_price) in enumerate(last_7_closes.items(), 1):
        # Format timestamp to show date and time
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M UTC')
        print(f"{i:2d}. {formatted_time} | ${close_price:8,.2f}")
    
    # Calculate price change for last 7 periods
    price_changes = last_7_closes.diff().dropna()
    avg_change = price_changes.mean()
    total_change = last_7_closes.iloc[-1] - last_7_closes.iloc[0]
    
    print(f"\n📊 Price Movement Summary (Last 7 periods):")
    print(f"   Starting Price: ${last_7_closes.iloc[0]:8,.2f}")
    print(f"   Current Price:  ${last_7_closes.iloc[-1]:8,.2f}")
    print(f"   Total Change:   ${total_change:+8,.2f} ({total_change/last_7_closes.iloc[0]*100:+.2f}%)")
    print(f"   Average Change: ${avg_change:+8,.2f}")
    
    # Step 3: Apply oscillators and get comprehensive data
    print(f"\n{'='*50}")
    print("🔧 APPLYING TECHNICAL INDICATORS")
    print(f"{'='*50}")
    
    try:
        oscillator = Oscillator(data)
        
        # Apply all oscillators
        indicators_applied = []
        
        # RSI
        data['RSI_14'] = oscillator.rsi_14()
        indicators_applied.append('RSI_14')
        
        # Stochastic
        stoch_data = oscillator.stochastic_k_14_3_3()
        data['Stoch_K'] = stoch_data['%K']
        data['Stoch_D'] = stoch_data['%D']
        indicators_applied.extend(['Stoch_K', 'Stoch_D'])
        
        # CCI
        data['CCI_20'] = oscillator.cci_20()
        indicators_applied.append('CCI_20')
        
        # ADX
        data['ADX_14'] = oscillator.adx_14()
        indicators_applied.append('ADX_14')
        
        # DMI
        data['DMI'] = oscillator.calculate_dmi()
        indicators_applied.append('DMI')
        
        # Awesome Oscillator
        data['AO'] = oscillator.awesome_oscillator()
        indicators_applied.append('AO')
        
        # Momentum
        data['Momentum_10'] = oscillator.momentum_10()
        indicators_applied.append('Momentum_10')
        
        # MACD
        macd_data = oscillator.macd_12_26()
        data['MACD'] = macd_data['MACD']
        data['MACD_Signal'] = macd_data['Signal_Line']
        indicators_applied.extend(['MACD', 'MACD_Signal'])
        
        # Stochastic RSI
        data['Stoch_RSI'] = oscillator.stochastic_rsi()
        indicators_applied.append('Stoch_RSI')
        
        # Williams %R
        data['Williams_R'] = oscillator.williams_percent_r()
        indicators_applied.append('Williams_R')
        
        # Bull/Bear Power
        bull_bear = oscillator.bull_bear_power()
        data['Bull_Power'] = bull_bear['Bull_Power']
        data['Bear_Power'] = bull_bear['Bear_Power']
        indicators_applied.extend(['Bull_Power', 'Bear_Power'])
        
        # Ultimate Oscillator
        data['Ultimate_Oscillator'] = oscillator.ultimate_oscillator()
        indicators_applied.append('Ultimate_Oscillator')
        
        print(f"✅ Applied {len(indicators_applied)} indicators successfully")
        
    except Exception as e:
        print(f"❌ Error applying indicators: {str(e)}")
        return
    
    # Step 4: Display latest indicator values
    print(f"\n{'='*50}")
    print("📊 LATEST INDICATOR VALUES")
    print(f"{'='*50}")
    
    latest_row = data.iloc[-1]
    
    # Group indicators by category
    momentum_indicators = {
        'RSI (14)': latest_row.get('RSI_14'),
        'Stochastic %K': latest_row.get('Stoch_K'),
        'Stochastic %D': latest_row.get('Stoch_D'),
        'Stochastic RSI': latest_row.get('Stoch_RSI'),
        'Williams %R': latest_row.get('Williams_R'),
        'CCI (20)': latest_row.get('CCI_20'),
        'Ultimate Oscillator': latest_row.get('Ultimate_Oscillator')
    }
    
    trend_indicators = {
        'ADX (14)': latest_row.get('ADX_14'),
        'DMI': latest_row.get('DMI'),
        'MACD': latest_row.get('MACD'),
        'MACD Signal': latest_row.get('MACD_Signal'),
        'Awesome Oscillator': latest_row.get('AO'),
        'Momentum (10)': latest_row.get('Momentum_10')
    }
    
    volume_indicators = {
        'Bull Power': latest_row.get('Bull_Power'),
        'Bear Power': latest_row.get('Bear_Power')
    }
    
    print("🎯 MOMENTUM INDICATORS:")
    for indicator, value in momentum_indicators.items():
        if isinstance(value, (int, float)) and not pd.isna(value):
            print(f"   {indicator:<20}: {value:8.4f}")
        else:
            print(f"   {indicator:<20}: {'N/A':>8}")
    
    print("\n📈 TREND INDICATORS:")
    for indicator, value in trend_indicators.items():
        if isinstance(value, (int, float)) and not pd.isna(value):
            print(f"   {indicator:<20}: {value:8.4f}")
        else:
            print(f"   {indicator:<20}: {'N/A':>8}")
    
    print("\n💪 VOLUME/POWER INDICATORS:")
    for indicator, value in volume_indicators.items():
        if isinstance(value, (int, float)) and not pd.isna(value):
            print(f"   {indicator:<20}: {value:8.4f}")
        else:
            print(f"   {indicator:<20}: {'N/A':>8}")
    
    # Step 5: Get oscillator status analysis
    print(f"\n{'='*50}")
    print("🎯 OSCILLATOR STATUS ANALYSIS")
    print(f"{'='*50}")
    
    latest_data = data.iloc[-1]
    prev_data = data.iloc[-2] if len(data) > 1 else latest_data
    
    # Define oscillators with their status mappings
    oscillator_configs = [
        ('RSI_14', 'RSI_14', 'Relative Strength Index'),
        ('Stoch_K', '%K', 'Stochastic %K'),
        ('CCI_20', 'CCI_20', 'Commodity Channel Index'),
        ('Stoch_RSI', 'Stoch_RSI', 'Stochastic RSI'),
        ('Williams_R', '%R', 'Williams %R'),
        ('Bull_Power', 'Bull_Power', 'Bull Power'),
        ('Bear_Power', 'Bear_Power', 'Bear Power'),
        ('Ultimate_Oscillator', 'UO', 'Ultimate Oscillator'),
        ('MACD', 'MACD', 'MACD')
    ]
    
    status_results = {}
    
    for col_name, status_key, display_name in oscillator_configs:
        if col_name in data.columns:
            try:
                current_value = latest_data[col_name]
                prev_value = prev_data[col_name] if col_name in prev_data else None
                
                status = Oscillator_Status.get_status(current_value, status_key, prev_value)
                
                status_results[display_name] = {
                    'value': current_value,
                    'status': status,
                    'previous_value': prev_value,
                    'column': col_name
                }
                
            except Exception as e:
                print(f"❌ Error processing {display_name}: {str(e)}")
    
    # Special handling for DMI
    if 'DMI' in data.columns and len(data) >= 2:
        try:
            dmi_data = data[['DMI']].tail(2)
            dmi_status = Oscillator_Status.dmi_status(dmi_data)
            status_results['Directional Movement Index'] = {
                'value': latest_data['DMI'],
                'status': dmi_status,
                'previous_value': prev_data['DMI'],
                'column': 'DMI'
            }
        except Exception as e:
            print(f"❌ Error processing DMI: {str(e)}")
    
    # Display status results
    for indicator_name, status_data in status_results.items():
        value = status_data['value']
        status = status_data['status']
        prev_value = status_data.get('previous_value')
        
        # Status emoji
        status_emoji = {"Buy": "🟢", "Sell": "🔴", "Neutral": "🟡"}.get(status, "❓")
        
        print(f"\n{status_emoji} {indicator_name}:")
        print(f"   Current Value: {value:8.4f}")
        
        if isinstance(prev_value, (int, float)) and not pd.isna(prev_value):
            change = value - prev_value
            change_direction = "↗️" if change > 0 else "↘️" if change < 0 else "➡️"
            print(f"   Previous Value: {prev_value:8.4f}")
            print(f"   Change: {change:+8.4f} {change_direction}")
        
        print(f"   Status: {status.upper()}")
    
    # Step 6: Summary and signals
    print(f"\n{'='*50}")
    print("📋 TRADING SIGNALS SUMMARY")
    print(f"{'='*50}")
    
    # Count signals
    buy_signals = sum(1 for data in status_results.values() if data['status'] == 'Buy')
    sell_signals = sum(1 for data in status_results.values() if data['status'] == 'Sell')
    neutral_signals = sum(1 for data in status_results.values() if data['status'] == 'Neutral')
    total_signals = len(status_results)
    
    print(f"📊 Signal Distribution:")
    print(f"   🟢 Buy Signals:     {buy_signals:2d} ({buy_signals/total_signals*100:5.1f}%)")
    print(f"   🔴 Sell Signals:    {sell_signals:2d} ({sell_signals/total_signals*100:5.1f}%)")
    print(f"   🟡 Neutral Signals: {neutral_signals:2d} ({neutral_signals/total_signals*100:5.1f}%)")
    print(f"   📈 Total Analyzed:  {total_signals:2d}")
    
    # Overall market sentiment
    if buy_signals > sell_signals:
        overall_sentiment = "BULLISH 🐂"
        sentiment_description = "More indicators suggest upward movement"
    elif sell_signals > buy_signals:
        overall_sentiment = "BEARISH 🐻"  
        sentiment_description = "More indicators suggest downward movement"
    else:
        overall_sentiment = "NEUTRAL ⚖️"
        sentiment_description = "Mixed signals from indicators"
    
    print(f"\n🎯 Overall Market Sentiment: {overall_sentiment}")
    print(f"   {sentiment_description}")
    
    # Signal strength
    signal_strength = abs(buy_signals - sell_signals) / total_signals
    strength_desc = "Strong" if signal_strength > 0.6 else "Moderate" if signal_strength > 0.3 else "Weak"
    print(f"   Signal Strength: {strength_desc} ({signal_strength:.1%})")
    
    # Key highlights
    print(f"\n💡 Key Highlights:")
    print(f"   📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   💰 Current Price: ${latest_row['close']:,.2f}")
    print(f"   📊 24h Change: ${total_change:+,.2f} ({total_change/last_7_closes.iloc[0]*100:+.2f}%)")
    print(f"   📈 Data Points: {len(data)} (30-min intervals over 7 days)")
    
    # Top signals
    buy_indicators = [name for name, data in status_results.items() if data['status'] == 'Buy']
    sell_indicators = [name for name, data in status_results.items() if data['status'] == 'Sell']
    
    if buy_indicators:
        print(f"   🟢 Strong Buy Signals: {', '.join(buy_indicators[:3])}{'...' if len(buy_indicators) > 3 else ''}")
    
    if sell_indicators:
        print(f"   🔴 Strong Sell Signals: {', '.join(sell_indicators[:3])}{'...' if len(sell_indicators) > 3 else ''}")
    
    print(f"\n{'='*80}")
    print("✅ US30 COMPREHENSIVE ANALYSIS COMPLETED")
    print(f"{'='*80}")
    
    return data

if __name__ == "__main__":
    try:
        result_data = run_comprehensive_us30_analysis()
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
