"""
US30 Analysis Script

This script runs the pipeline analysis for US30 index with 30-minute timeframe
and displays the latest indicators and oscillator status.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf

# Import the indicators and oscillators
from indicators import ADX, Stochastic_Oscillator, RSI, ATRBands, SupertrendIndicator
from indicators_oscillators import Oscillator, Oscillator_Status

def fetch_us30_data(period='7d', interval='30m'):
    """Fetch US30 data with specified parameters."""
    print(f"Fetching US30 data - Period: {period}, Interval: {interval}")
    
    # US30 symbol for yfinance
    symbol = '^DJI'  # Dow Jones Industrial Average
    
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        
        if data.empty:
            print("No data retrieved")
            return pd.DataFrame()
        
        # Clean up the data
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            data.columns = [col[:-1] if col.endswith('_') else col for col in data.columns]
        
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
        
        print(f"Successfully fetched {len(data)} data points")
        return data
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def apply_indicators(df):
    """Apply technical indicators to the dataframe."""
    print("Applying technical indicators...")
    
    result_df = df.copy()
    
    try:
        # Apply ADX
        adx_indicator = ADX(adx_period=14)
        result_df['+DI'], result_df['-DI'], result_df['ADX'] = adx_indicator.calculate(result_df)
        
        # Apply Stochastic
        stoch_indicator = Stochastic_Oscillator(k_period=14, k_smooth=3, d_period=3)
        result_df['%K'], result_df['%D'] = stoch_indicator.calculate(result_df)
        
        # Apply RSI
        rsi_indicator = RSI(rsi_period=14)
        result_df['RSI'] = rsi_indicator.calculate(result_df)
        
        # Apply ATR Bands
        atr_indicator = ATRBands(atr_period=14, atr_multiplier=2.0)
        result_df['ATR'], result_df['ATR_Upper'], result_df['ATR_Lower'] = atr_indicator.calculate(result_df)
        
        # Apply Supertrend
        supertrend_indicator = SupertrendIndicator(period=10, multiplier=3.0)
        result_df['Supertrend'], result_df['ST_Direction'] = supertrend_indicator.calculate(result_df)
        
        print("Successfully applied main indicators")
        
    except Exception as e:
        print(f"Error applying main indicators: {str(e)}")
    
    return result_df

def apply_oscillators(df):
    """Apply oscillator indicators and get their status."""
    print("Applying oscillator indicators...")
    
    try:
        # Create oscillator instance
        oscillator = Oscillator(df)
        
        # Apply oscillators
        df['RSI_14'] = oscillator.rsi_14()
        stoch_data = oscillator.stochastic_k_14_3_3()
        df['Stoch_K'] = stoch_data['%K']
        df['Stoch_D'] = stoch_data['%D']
        df['CCI_20'] = oscillator.cci_20()
        df['ADX_14'] = oscillator.adx_14()
        df['DMI'] = oscillator.calculate_dmi()
        df['AO'] = oscillator.awesome_oscillator()
        df['Momentum_10'] = oscillator.momentum_10()
        
        macd_data = oscillator.macd_12_26()
        df['MACD'] = macd_data['MACD']
        df['MACD_Signal'] = macd_data['Signal_Line']
        
        df['Stoch_RSI'] = oscillator.stochastic_rsi()
        df['Williams_R'] = oscillator.williams_percent_r()
        
        bull_bear = oscillator.bull_bear_power()
        df['Bull_Power'] = bull_bear['Bull_Power']
        df['Bear_Power'] = bull_bear['Bear_Power']
        
        df['Ultimate_Oscillator'] = oscillator.ultimate_oscillator()
        
        print("Successfully applied oscillator indicators")
        
    except Exception as e:
        print(f"Error applying oscillators: {str(e)}")
    
    return df

def get_oscillator_status(df):
    """Get the current status of all oscillators."""
    print("\nGetting oscillator status for latest data point...")
    
    if df.empty:
        print("No data available for status analysis")
        return {}
    
    latest_data = df.iloc[-1]
    prev_data = df.iloc[-2] if len(df) > 1 else latest_data
    
    status_results = {}
    
    # Define oscillators to check with their status
    oscillators_to_check = [
        ('RSI_14', 'RSI_14'),
        ('Stoch_K', '%K'),
        ('CCI_20', 'CCI_20'),
        ('Stoch_RSI', 'Stoch_RSI'),
        ('Williams_R', '%R'),
        ('Bull_Power', 'Bull_Power'),
        ('Bear_Power', 'Bear_Power'),
        ('Ultimate_Oscillator', 'UO'),
        ('MACD', 'MACD')
    ]
    
    for col_name, indicator_name in oscillators_to_check:
        if col_name in df.columns:
            try:
                current_value = latest_data[col_name]
                prev_value = prev_data[col_name] if col_name in prev_data else None
                
                status = Oscillator_Status.get_status(current_value, indicator_name, prev_value)
                status_results[col_name] = {
                    'value': current_value,
                    'status': status,
                    'previous_value': prev_value
                }
            except Exception as e:
                print(f"Error getting status for {col_name}: {str(e)}")
    
    # Special handling for DMI
    if 'DMI' in df.columns and len(df) >= 2:
        try:
            dmi_data = df[['DMI']].tail(2)
            dmi_status = Oscillator_Status.dmi_status(dmi_data)
            status_results['DMI'] = {
                'value': latest_data['DMI'],
                'status': dmi_status,
                'previous_value': prev_data['DMI']
            }
        except Exception as e:
            print(f"Error getting DMI status: {str(e)}")
    
    return status_results

def run_us30_analysis():
    """Run complete US30 analysis."""
    print("="*60)
    print("US30 (DOW JONES) ANALYSIS - 30 MINUTE TIMEFRAME")
    print("="*60)
    
    # Step 1: Fetch data
    data = fetch_us30_data(period='7d', interval='30m')
    
    if data.empty:
        print("Failed to fetch data. Exiting.")
        return
    
    # Step 2: Apply indicators
    data_with_indicators = apply_indicators(data)
    
    # Step 3: Apply oscillators
    data_with_oscillators = apply_oscillators(data_with_indicators)
    
    # Step 4: Display last 7 close prices
    print(f"\n{'='*40}")
    print("LAST 7 CLOSE PRICES")
    print(f"{'='*40}")
    
    last_7_closes = data_with_oscillators['close'].tail(7)
    for i, (timestamp, close_price) in enumerate(last_7_closes.items(), 1):
        print(f"{i}. {timestamp.strftime('%Y-%m-%d %H:%M'): <20} | Close: ${close_price:,.2f}")
    
    # Step 5: Display latest indicators data
    print(f"\n{'='*40}")
    print("LATEST INDICATORS DATA")
    print(f"{'='*40}")
    
    latest_row = data_with_oscillators.iloc[-1]
    
    # Main indicators
    main_indicators = {
        'ADX': latest_row.get('ADX', 'N/A'),
        '+DI': latest_row.get('+DI', 'N/A'),
        '-DI': latest_row.get('-DI', 'N/A'),
        'RSI': latest_row.get('RSI', 'N/A'),
        '%K': latest_row.get('%K', 'N/A'),
        '%D': latest_row.get('%D', 'N/A'),
        'ATR': latest_row.get('ATR', 'N/A'),
        'Supertrend': latest_row.get('Supertrend', 'N/A'),
        'ST_Direction': latest_row.get('ST_Direction', 'N/A')
    }
    
    print("Main Indicators:")
    for indicator, value in main_indicators.items():
        if isinstance(value, (int, float)) and not pd.isna(value):
            print(f"  {indicator: <15}: {value:.4f}")
        else:
            print(f"  {indicator: <15}: {value}")
    
    # Oscillator indicators
    oscillator_indicators = {
        'RSI_14': latest_row.get('RSI_14', 'N/A'),
        'CCI_20': latest_row.get('CCI_20', 'N/A'),
        'MACD': latest_row.get('MACD', 'N/A'),
        'MACD_Signal': latest_row.get('MACD_Signal', 'N/A'),
        'Stoch_RSI': latest_row.get('Stoch_RSI', 'N/A'),
        'Williams_R': latest_row.get('Williams_R', 'N/A'),
        'DMI': latest_row.get('DMI', 'N/A'),
        'AO': latest_row.get('AO', 'N/A'),
        'Momentum_10': latest_row.get('Momentum_10', 'N/A'),
        'Bull_Power': latest_row.get('Bull_Power', 'N/A'),
        'Bear_Power': latest_row.get('Bear_Power', 'N/A'),
        'Ultimate_Oscillator': latest_row.get('Ultimate_Oscillator', 'N/A')
    }
    
    print("\nOscillator Indicators:")
    for indicator, value in oscillator_indicators.items():
        if isinstance(value, (int, float)) and not pd.isna(value):
            print(f"  {indicator: <20}: {value:.4f}")
        else:
            print(f"  {indicator: <20}: {value}")
    
    # Step 6: Get oscillator status
    print(f"\n{'='*40}")
    print("OSCILLATOR STATUS ANALYSIS")
    print(f"{'='*40}")
    
    status_results = get_oscillator_status(data_with_oscillators)
    
    for oscillator, status_data in status_results.items():
        value = status_data['value']
        status = status_data['status']
        prev_value = status_data.get('previous_value', 'N/A')
        
        print(f"\n{oscillator}:")
        print(f"  Current Value : {value:.4f}")
        if isinstance(prev_value, (int, float)) and not pd.isna(prev_value):
            print(f"  Previous Value: {prev_value:.4f}")
            change = value - prev_value
            change_direction = "↑" if change > 0 else "↓" if change < 0 else "→"
            print(f"  Change        : {change:+.4f} {change_direction}")
        print(f"  Status        : {status}")
    
    # Step 7: Summary
    print(f"\n{'='*40}")
    print("SUMMARY")
    print(f"{'='*40}")
    
    buy_signals = sum(1 for status_data in status_results.values() if status_data['status'] == 'Buy')
    sell_signals = sum(1 for status_data in status_results.values() if status_data['status'] == 'Sell')
    neutral_signals = sum(1 for status_data in status_results.values() if status_data['status'] == 'Neutral')
    
    print(f"Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data Points Analyzed: {len(data_with_oscillators)}")
    print(f"Latest Close Price: ${latest_row['close']:,.2f}")
    print(f"\nSignal Distribution:")
    print(f"  Buy Signals   : {buy_signals}")
    print(f"  Sell Signals  : {sell_signals}")
    print(f"  Neutral       : {neutral_signals}")
    print(f"  Total Analyzed: {len(status_results)}")
    
    # Overall sentiment
    if buy_signals > sell_signals:
        overall_sentiment = "BULLISH"
    elif sell_signals > buy_signals:
        overall_sentiment = "BEARISH"
    else:
        overall_sentiment = "NEUTRAL"
    
    print(f"\nOverall Sentiment: {overall_sentiment}")
    
    return data_with_oscillators

if __name__ == "__main__":
    try:
        result_data = run_us30_analysis()
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
