"""
Trading Pipeline Instructions and Documentation

This module provides comprehensive documentation and instructions for using
the Finance Trade Assistant backend pipeline system.
"""

from typing import Dict, List, Any

def get_pipeline_overview() -> str:
    """Get an overview of the trading pipeline system."""
    return """
    FINANCE TRADE ASSISTANT - BACKEND PIPELINE SYSTEM
    =================================================
    
    The backend system is organized into modular pipeline components:
    
    1. DATA FETCHING PIPELINE (pipeline_fetching_data.py)
       - Fetches market data from multiple sources
       - Supports forex, stocks, indices, and cryptocurrency
       - Handles data cleaning and standardization
       - Maintains compatibility with original yfinance_data_loader.py
    
    2. INDICATOR APPLICATION PIPELINE (pipeline_applying_indicator.py)
       - Applies technical indicators to market data
       - Supports all original indicators (ADX, Stochastic, RSI, etc.)
       - Provides unified interface for indicator management
       - Maintains state for efficient incremental calculations
    
    3. STRATEGY DEFINITION PIPELINE (pipeline_defining_strategy.py)
       - Defines and executes trading strategies
       - Supports complex condition-based strategies
       - Provides backtesting capabilities
       - Includes library of predefined strategies
    
    4. MAIN PIPELINE ORCHESTRATOR (pipeline_main.py)
       - Coordinates all pipeline components
       - Provides high-level interface for complete analysis
       - Maintains backward compatibility with original code
       - Supports configuration and result export
    
    5. SYMBOL MANAGEMENT
       - forex_symbols.py: Forex pair mappings
       - indices_symbols.py: Market index mappings
       - crypto_symbols.py: Cryptocurrency mappings
       - stocks_symbols.py: Stock symbol mappings
    
    6. ORIGINAL CODE PRESERVATION
       - All original code is preserved and commented
       - Legacy functions provide exact compatibility
       - Incremental upgrade path available
    """

def get_quick_start_guide() -> str:
    """Get a quick start guide for using the pipeline."""
    return """
    QUICK START GUIDE
    =================
    
    1. BASIC USAGE (Legacy Compatibility):
       ```python
       from backend import run_eurusd_analysis
       results = run_eurusd_analysis()
       print(results['summary'])
       ```
    
    2. ANALYZE ANY SYMBOL:
       ```python
       from backend import run_symbol_analysis
       
       # Forex
       results = run_symbol_analysis('gbpusd', 'forex')
       
       # Stocks  
       results = run_symbol_analysis('AAPL', 'stocks')
       
       # Crypto
       results = run_symbol_analysis('btc', 'crypto')
       
       # Indices
       results = run_symbol_analysis('sp500', 'indices')
       ```
    
    3. CUSTOM PIPELINE:
       ```python
       from backend import TradingPipeline
       
       pipeline = TradingPipeline()
       pipeline.load_legacy_strategies()
       results = pipeline.run_full_pipeline('eurusd', 'forex')
       ```
    
    4. STEP-BY-STEP USAGE:
       ```python
       from backend import DataFetcher, IndicatorManager, StrategyLibrary
       
       # Fetch data
       fetcher = DataFetcher()
       data = fetcher.fetch_data('eurusd', period='7d', interval='1h')
       
       # Apply indicators
       manager = IndicatorManager()
       manager.setup_default_indicators()
       data_with_indicators = manager.apply_all_indicators(data)
       
       # Apply strategy
       strategy = StrategyLibrary.create_legacy_di_stoch_strategy()
       signals = strategy.generate_signals(data_with_indicators)
       ```
    
    5. CREATE CUSTOM STRATEGY:
       ```python
       from backend import StrategyBuilder, StrategyCondition
       
       builder = StrategyBuilder("My_RSI_Strategy")
       
       # Buy when RSI crosses above 30
       builder.add_buy_condition(StrategyCondition(
           name="rsi_oversold_exit",
           column1="rsi_default_rsi",
           operator="cross_above",
           value=30
       ))
       
       # Sell when RSI crosses below 70
       builder.add_sell_condition(StrategyCondition(
           name="rsi_overbought_exit", 
           column1="rsi_default_rsi",
           operator="cross_below",
           value=70
       ))
       
       strategy = builder.build()
       ```
    """

def get_migration_guide() -> str:
    """Get a guide for migrating from original code to pipeline system."""
    return """
    MIGRATION GUIDE
    ===============
    
    The pipeline system is designed for seamless migration from existing code:
    
    1. IMMEDIATE COMPATIBILITY:
       - All original functions still work exactly as before
       - No changes needed to existing code
       - Original imports continue to work
    
    2. GRADUAL MIGRATION:
       
       OLD WAY:
       ```python
       # Original approach from yfinance_data_loader.py + strategy.py
       import yfinance as yf
       from indicators import ADX, Stochastic_Oscillator
       
       eurusd_data = yf.download('EURUSD=X', period='7d', interval='1h')
       # ... data cleaning ...
       
       adx = ADX()
       stoch = Stochastic_Oscillator()
       eurusd_data['+DI'], eurusd_data['-DI'], eurusd_data['ADX'] = adx.calculate(eurusd_data)
       eurusd_data['%K'], eurusd_data['%D'] = stoch.calculate(eurusd_data)
       
       # Signal generation
       eurusd_data['di_buy'] = (eurusd_data['+DI'].shift(1) < eurusd_data['-DI'].shift(1)) & (eurusd_data['+DI'] > eurusd_data['-DI'])
       # ... more signal logic ...
       ```
       
       NEW WAY (Equivalent):
       ```python
       from backend import run_eurusd_analysis
       results = run_eurusd_analysis()  # Exact same result as above
       ```
       
       NEW WAY (Extended):
       ```python
       from backend import TradingPipeline, StrategyLibrary
       
       pipeline = TradingPipeline()
       
       # Add the exact same strategy as original
       legacy_strategy = StrategyLibrary.create_legacy_di_stoch_strategy()
       pipeline.add_strategy(legacy_strategy)
       
       # Run with same parameters
       results = pipeline.run_full_pipeline('eurusd', 'forex', '7d', '1h')
       
       # Access the same data
       data_with_indicators = results['data_with_indicators']
       signals = results['strategy_results']['Legacy_DI_Stoch']['signals']
       ```
    
    3. BENEFITS OF MIGRATION:
       - Use any symbol, not just EURUSD
       - Add multiple strategies easily
       - Automatic backtesting
       - Better error handling and logging
       - Configuration management
       - Result export capabilities
       - Extensible architecture
    
    4. BACKWARD COMPATIBILITY GUARANTEE:
       - Original functions preserved with 'legacy' prefix
       - Original file behavior maintained
       - No breaking changes to existing workflows
    """

def get_api_reference() -> Dict[str, List[str]]:
    """Get API reference for all pipeline components."""
    return {
        "DataFetcher": [
            "fetch_data(symbol, period, interval, asset_type)",
            "fetch_multiple_assets(assets, period, interval)",
            "get_symbol_for_asset(asset_key, asset_type)"
        ],
        "IndicatorManager": [
            "setup_default_indicators()",
            "setup_forex_indicators()",
            "apply_all_indicators(df)"
        ],
        "IndicatorPipeline": [
            "add_indicator(name, indicator_class, **kwargs)",
            "remove_indicator(name)",
            "apply_indicators(df, indicator_names)",
            "reset_indicators()"
        ],
        "StrategyBuilder": [
            "add_buy_condition(condition)",
            "add_sell_condition(condition)",
            "set_buy_operator(operator)",
            "set_sell_operator(operator)",
            "build()"
        ],
        "TradingStrategy": [
            "evaluate_condition(df, condition)",
            "generate_signals(df)",
            "backtest(df, initial_balance)"
        ],
        "TradingPipeline": [
            "add_data_source(symbol, asset_type, period, interval)",
            "add_strategy(strategy)",
            "run_full_pipeline(symbol, asset_type, period, interval)",
            "run_legacy_pipeline(symbol)",
            "get_pipeline_status()",
            "export_results(results, filename)"
        ],
        "StrategyLibrary": [
            "create_legacy_di_stoch_strategy()",
            "create_rsi_oversold_strategy()",
            "create_supertrend_strategy()"
        ]
    }

def get_configuration_guide() -> str:
    """Get guide for configuring the pipeline system."""
    return """
    CONFIGURATION GUIDE
    ===================
    
    The pipeline system supports comprehensive configuration:
    
    1. DEFAULT CONFIGURATION:
       ```python
       from backend import get_default_config
       config = get_default_config()
       print(config)
       ```
    
    2. CUSTOM CONFIGURATION:
       ```python
       from backend import TradingPipeline
       
       config = {
           'data': {
               'default_period': '30d',
               'default_interval': '4h',
               'default_asset_type': 'stocks'
           },
           'indicators': {
               'use_default_set': True,
               'forex_optimized': False
           },
           'strategies': {
               'include_legacy': True,
               'auto_backtest': True
           }
       }
       
       pipeline = TradingPipeline(config)
       ```
    
    3. CONFIGURATION OPTIONS:
       
       Data Settings:
       - default_period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
       - default_interval: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
       - default_asset_type: 'forex', 'stocks', 'indices', 'crypto'
       
       Indicator Settings:
       - use_default_set: True/False (includes ADX, Stochastic, RSI, ATR, Supertrend)
       - forex_optimized: True/False (adds forex-specific indicator parameters)
       
       Strategy Settings:
       - include_legacy: True/False (includes original strategy from strategy.py)
       - auto_backtest: True/False (automatically runs backtests on strategies)
    
    4. INDICATOR CONFIGURATION:
       ```python
       from backend import IndicatorManager
       
       manager = IndicatorManager()
       
       # Add custom indicator configurations
       manager.pipeline.add_indicator("custom_rsi", "RSI", rsi_period=21)
       manager.pipeline.add_indicator("custom_adx", "ADX", adx_period=10)
       manager.pipeline.add_indicator("custom_stoch", "Stochastic_Oscillator", 
                                     k_period=14, k_smooth=3, d_period=3)
       ```
    """

def get_troubleshooting_guide() -> str:
    """Get troubleshooting guide for common issues.""" 
    return """
    TROUBLESHOOTING GUIDE
    =====================
    
    Common issues and solutions:
    
    1. IMPORT ERRORS:
       Problem: "ModuleNotFoundError: No module named 'pandas'"
       Solution: Install required dependencies:
       ```bash
       pip install pandas numpy yfinance
       ```
    
    2. DATA FETCHING ISSUES:
       Problem: Empty dataframe returned
       Solutions:
       - Check internet connection
       - Verify symbol format (e.g., 'EURUSD=X' for forex)
       - Try different time periods
       - Check if market is open/data is available
    
    3. INDICATOR CALCULATION ERRORS:
       Problem: "KeyError: 'high'" or missing OHLC columns
       Solutions:
       - Ensure data has required columns: 'open', 'high', 'low', 'close'
       - Check data is not empty before applying indicators
       - Verify data types are numeric
    
    4. STRATEGY SIGNAL ISSUES:
       Problem: No buy/sell signals generated
       Solutions:
       - Check indicator columns exist in dataframe
       - Verify condition thresholds are appropriate
       - Ensure sufficient data history for conditions
       - Check for NaN values in indicator data
    
    5. BACKWARD COMPATIBILITY ISSUES:
       Problem: Original code not working
       Solutions:
       - Use legacy functions: run_eurusd_analysis(), apply_legacy_indicators()
       - Import from specific modules if needed
       - Check that all original files are preserved
    
    6. PERFORMANCE ISSUES:
       Problem: Slow execution
       Solutions:
       - Reduce data period or use larger intervals
       - Limit number of indicators applied
       - Use indicator reset_indicators() to clear state
       - Process smaller datasets for testing
    
    7. LOGGING AND DEBUGGING:
       ```python
       import logging
       logging.basicConfig(level=logging.DEBUG)
       
       from backend import TradingPipeline
       pipeline = TradingPipeline()
       # Now you'll see detailed logs
       ```
    
    8. MEMORY ISSUES:
       Problem: High memory usage
       Solutions:
       - Process data in chunks
       - Clear unnecessary dataframes
       - Use specific indicators instead of all
       - Reduce historical data period
    """

def get_examples() -> Dict[str, str]:
    """Get comprehensive examples for different use cases."""
    return {
        "basic_forex_analysis": """
# Basic forex analysis (EURUSD)
from backend import run_eurusd_analysis

results = run_eurusd_analysis()
print(f"Data points: {results['summary']['data_points']}")
print(f"Buy signals: {results['summary']['buy_signals']}")
print(f"Sell signals: {results['summary']['sell_signals']}")

# Access the data
data = results['data']
print(data[['open', 'high', 'low', 'close', '+DI', '-DI', 'ADX']].tail())
        """,
        
        "multi_symbol_analysis": """
# Analyze multiple symbols
from backend import run_symbol_analysis

symbols = [
    ('eurusd', 'forex'),
    ('AAPL', 'stocks'), 
    ('btc', 'crypto'),
    ('sp500', 'indices')
]

results = {}
for symbol, asset_type in symbols:
    result = run_symbol_analysis(symbol, asset_type)
    if 'error' not in result:
        results[symbol] = result
        print(f"{symbol}: {len(result['data_points'])} data points")
        """,
        
        "custom_strategy_creation": """
# Create a custom RSI + MACD strategy
from backend import StrategyBuilder, StrategyCondition, TradingPipeline

# Build the strategy
builder = StrategyBuilder("RSI_MACD_Strategy")

# Buy conditions: RSI > 30 AND MACD > 0
builder.add_buy_condition(StrategyCondition(
    name="rsi_above_30",
    column1="rsi_default_rsi",
    operator=">",
    value=30
))

builder.add_buy_condition(StrategyCondition(
    name="macd_positive",
    column1="oscillators_macd",
    operator=">", 
    value=0
))

# Sell conditions: RSI < 70 OR MACD < 0
builder.add_sell_condition(StrategyCondition(
    name="rsi_below_70",
    column1="rsi_default_rsi",
    operator="<",
    value=70
))

builder.set_sell_operator(ConditionOperator.OR)

strategy = builder.build()

# Apply to pipeline
pipeline = TradingPipeline()
pipeline.add_strategy(strategy)
results = pipeline.run_full_pipeline('eurusd', 'forex')
        """,
        
        "backtesting_example": """
# Run backtesting on strategies
from backend import StrategyLibrary, TradingPipeline

# Create pipeline with backtesting enabled
config = {'strategies': {'auto_backtest': True}}
pipeline = TradingPipeline(config)

# Add strategies
legacy_strategy = StrategyLibrary.create_legacy_di_stoch_strategy()
rsi_strategy = StrategyLibrary.create_rsi_oversold_strategy()

pipeline.add_strategy(legacy_strategy)
pipeline.add_strategy(rsi_strategy)

# Run analysis
results = pipeline.run_full_pipeline('eurusd', 'forex')

# Check backtest results
for strategy_name, strategy_data in results['strategy_results'].items():
    if 'backtest' in strategy_data:
        backtest = strategy_data['backtest']
        print(f"{strategy_name}:")
        print(f"  Total Return: {backtest['total_return_pct']:.2f}%")
        print(f"  Total Trades: {backtest['total_trades']}")
        """,
        
        "data_export_example": """
# Export results to file
from backend import TradingPipeline

pipeline = TradingPipeline()
results = pipeline.run_full_pipeline('eurusd', 'forex')

# Export to JSON
filename = pipeline.export_results(results)
print(f"Results exported to: {filename}")

# Export with custom filename
custom_filename = pipeline.export_results(results, "my_analysis.json")
print(f"Results exported to: {custom_filename}")
        """
    }

# Main instruction functions
def print_overview():
    """Print the pipeline overview."""
    print(get_pipeline_overview())

def print_quick_start():
    """Print the quick start guide."""
    print(get_quick_start_guide())

def print_migration_guide():
    """Print the migration guide."""
    print(get_migration_guide())

def print_api_reference():
    """Print the API reference."""
    api_ref = get_api_reference()
    print("API REFERENCE")
    print("=============")
    for class_name, methods in api_ref.items():
        print(f"\n{class_name}:")
        for method in methods:
            print(f"  - {method}")

def print_configuration_guide():
    """Print the configuration guide."""
    print(get_configuration_guide())

def print_troubleshooting():
    """Print the troubleshooting guide."""
    print(get_troubleshooting_guide())

def print_examples():
    """Print code examples."""
    examples = get_examples()
    print("CODE EXAMPLES")
    print("=============")
    for title, code in examples.items():
        print(f"\n{title.upper()}:")
        print(code)

def print_all_instructions():
    """Print all instruction sections."""
    print_overview()
    print("\n" + "="*60 + "\n")
    print_quick_start()
    print("\n" + "="*60 + "\n")
    print_migration_guide()
    print("\n" + "="*60 + "\n")
    print_api_reference()
    print("\n" + "="*60 + "\n")
    print_configuration_guide()
    print("\n" + "="*60 + "\n")
    print_troubleshooting()
    print("\n" + "="*60 + "\n")
    print_examples()

if __name__ == "__main__":
    print_all_instructions()