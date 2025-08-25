"""
Main Trading Pipeline Orchestrator

This module ties together all the pipeline components (data fetching, 
indicator application, and strategy execution) into a unified trading system.
It preserves all existing functionality while providing a clean, modular interface.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime
import json

# Import pipeline components
from .pipeline_fetching_data import DataFetcher, get_legacy_eurusd_data
from .pipeline_applying_indicator import IndicatorManager, apply_legacy_indicators
from .pipeline_defining_strategy import StrategyLibrary, TradingStrategy, apply_legacy_strategy_signals

class TradingPipeline:
    """
    Main orchestrator for the complete trading pipeline.
    Integrates data fetching, indicator application, and strategy execution.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.data_fetcher = DataFetcher()
        self.indicator_manager = IndicatorManager()
        self.strategies = {}
        self.results_history = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize with default configurations
        self._setup_default_configuration()
    
    def _setup_default_configuration(self):
        """Setup default pipeline configuration."""
        default_config = {
            'data': {
                'default_period': '7d',
                'default_interval': '1h',
                'default_asset_type': 'forex'
            },
            'indicators': {
                'use_default_set': True,
                'forex_optimized': True
            },
            'strategies': {
                'include_legacy': True,
                'auto_backtest': False
            }
        }
        
        # Merge with provided config
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Setup indicators based on config
        if self.config['indicators']['use_default_set']:
            self.indicator_manager.setup_default_indicators()
        
        if self.config['indicators']['forex_optimized']:
            self.indicator_manager.setup_forex_indicators()
    
    def add_data_source(self, 
                       symbol: str, 
                       asset_type: str = "forex",
                       period: str = None,
                       interval: str = None) -> bool:
        """
        Add a data source to the pipeline.
        
        Args:
            symbol: The asset symbol or friendly key
            asset_type: Type of asset (forex, stocks, indices, crypto)
            period: Data period (defaults to config)
            interval: Data interval (defaults to config)
            
        Returns:
            Success boolean
        """
        try:
            period = period or self.config['data']['default_period']
            interval = interval or self.config['data']['default_interval']
            
            self.logger.info(f"Adding data source: {symbol} ({asset_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding data source {symbol}: {str(e)}")
            return False
    
    def add_strategy(self, strategy: TradingStrategy) -> bool:
        """
        Add a trading strategy to the pipeline.
        
        Args:
            strategy: The TradingStrategy instance
            
        Returns:
            Success boolean
        """
        try:
            self.strategies[strategy.name] = strategy
            self.logger.info(f"Added strategy: {strategy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding strategy {strategy.name}: {str(e)}")
            return False
    
    def load_legacy_strategies(self):
        """Load predefined strategies for backward compatibility."""
        # Load the legacy DI + Stochastic strategy
        legacy_strategy = StrategyLibrary.create_legacy_di_stoch_strategy()
        self.add_strategy(legacy_strategy)
        
        # Load other predefined strategies
        rsi_strategy = StrategyLibrary.create_rsi_oversold_strategy()
        self.add_strategy(rsi_strategy)
        
        supertrend_strategy = StrategyLibrary.create_supertrend_strategy()
        self.add_strategy(supertrend_strategy)
    
    def run_full_pipeline(self, 
                         symbol: str,
                         asset_type: str = "forex",
                         period: str = None,
                         interval: str = None,
                         strategies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the complete trading pipeline for a given asset.
        
        Args:
            symbol: Asset symbol to analyze
            asset_type: Type of asset
            period: Data period
            interval: Data interval  
            strategies: List of strategy names to apply (None = all)
            
        Returns:
            Dictionary containing all results
        """
        try:
            self.logger.info(f"Running full pipeline for {symbol}")
            
            # Step 1: Fetch data
            period = period or self.config['data']['default_period']
            interval = interval or self.config['data']['default_interval']
            
            data = self.data_fetcher.fetch_data(symbol, period, interval, asset_type)
            
            if data.empty:
                self.logger.error(f"No data retrieved for {symbol}")
                return {'error': 'No data available'}
            
            self.logger.info(f"Fetched {len(data)} data points for {symbol}")
            
            # Step 2: Apply indicators
            data_with_indicators = self.indicator_manager.apply_all_indicators(data)
            
            applied_indicators = self.indicator_manager.pipeline.get_applied_indicators()
            self.logger.info(f"Applied {len(applied_indicators)} indicators")
            
            # Step 3: Apply strategies
            strategy_results = {}
            strategies_to_run = strategies or list(self.strategies.keys())
            
            for strategy_name in strategies_to_run:
                if strategy_name in self.strategies:
                    strategy = self.strategies[strategy_name]
                    strategy_data = strategy.generate_signals(data_with_indicators)
                    
                    # Run backtest if configured
                    if self.config['strategies']['auto_backtest']:
                        backtest_results = strategy.backtest(strategy_data)
                        strategy_results[strategy_name] = {
                            'signals': strategy_data[[f'{strategy_name}_buy', f'{strategy_name}_sell']],
                            'backtest': backtest_results
                        }
                    else:
                        strategy_results[strategy_name] = {
                            'signals': strategy_data[[f'{strategy_name}_buy', f'{strategy_name}_sell']]
                        }
            
            # Compile results
            results = {
                'symbol': symbol,
                'asset_type': asset_type,
                'timestamp': datetime.now().isoformat(),
                'data_points': len(data),
                'raw_data': data,
                'indicators_applied': applied_indicators,
                'data_with_indicators': data_with_indicators,
                'strategy_results': strategy_results,
                'config': self.config
            }
            
            # Store in history
            self.results_history.append({
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'strategies_run': list(strategy_results.keys()),
                'data_points': len(data)
            })
            
            self.logger.info(f"Pipeline completed successfully for {symbol}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in full pipeline for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def run_legacy_pipeline(self, symbol: str = 'eurusd') -> Dict[str, Any]:
        """
        Run the pipeline using the original approach for backward compatibility.
        This replicates the exact functionality from the original files.
        """
        try:
            self.logger.info(f"Running legacy pipeline for {symbol}")
            
            # Step 1: Get data using legacy approach
            if symbol.lower() == 'eurusd':
                # Use the exact original data fetching approach
                data = get_legacy_eurusd_data()
            else:
                # Fallback to new approach
                data = self.data_fetcher.fetch_data(symbol, '7d', '1h', 'forex')
            
            if data.empty:
                return {'error': 'No data available'}
            
            # Step 2: Apply indicators using legacy approach
            data_with_indicators = apply_legacy_indicators(data)
            
            # Step 3: Apply legacy strategy signals
            data_with_signals = apply_legacy_strategy_signals(data_with_indicators)
            
            # Step 4: Create summary
            results = {
                'symbol': symbol,
                'method': 'legacy',
                'timestamp': datetime.now().isoformat(),
                'data': data_with_signals,
                'summary': {
                    'data_points': len(data),
                    'indicators': ['+DI', '-DI', 'ADX', '%K', '%D'],
                    'signals': ['di_buy', 'di_sell', 'stoc_buy', 'stoc_sell'],
                    'buy_signals': data_with_signals['combined_buy'].sum() if 'combined_buy' in data_with_signals.columns else 0,
                    'sell_signals': data_with_signals['combined_sell'].sum() if 'combined_sell' in data_with_signals.columns else 0
                }
            }
            
            self.logger.info("Legacy pipeline completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in legacy pipeline: {str(e)}")
            return {'error': str(e)}
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current status of the pipeline."""
        return {
            'configured_indicators': self.indicator_manager.pipeline.get_indicator_list(),
            'available_strategies': list(self.strategies.keys()),
            'results_history_count': len(self.results_history),
            'configuration': self.config
        }
    
    def export_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """
        Export pipeline results to a file.
        
        Args:
            results: Results dictionary from pipeline run
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Filename of exported results
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                symbol = results.get('symbol', 'unknown')
                filename = f"pipeline_results_{symbol}_{timestamp}.json"
            
            # Prepare data for export (convert DataFrames to dict)
            export_data = results.copy()
            
            if 'raw_data' in export_data:
                export_data['raw_data'] = export_data['raw_data'].to_dict('records')
            
            if 'data_with_indicators' in export_data:
                export_data['data_with_indicators'] = export_data['data_with_indicators'].to_dict('records')
            
            # Convert strategy signals DataFrames
            if 'strategy_results' in export_data:
                for strategy_name, strategy_data in export_data['strategy_results'].items():
                    if 'signals' in strategy_data:
                        export_data['strategy_results'][strategy_name]['signals'] = strategy_data['signals'].to_dict('records')
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Results exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting results: {str(e)}")
            return ""

# Convenience functions for backward compatibility
def create_default_pipeline() -> TradingPipeline:
    """Create a pipeline with default configuration."""
    pipeline = TradingPipeline()
    pipeline.load_legacy_strategies()
    return pipeline

def run_eurusd_analysis() -> Dict[str, Any]:
    """
    Run analysis on EURUSD using the legacy approach.
    This maintains exact compatibility with the original code.
    """
    pipeline = create_default_pipeline()
    return pipeline.run_legacy_pipeline('eurusd')

def run_symbol_analysis(symbol: str, asset_type: str = 'forex') -> Dict[str, Any]:
    """
    Run analysis on any symbol using the new pipeline.
    
    Args:
        symbol: Asset symbol to analyze
        asset_type: Type of asset
        
    Returns:
        Analysis results
    """
    pipeline = create_default_pipeline()
    return pipeline.run_full_pipeline(symbol, asset_type)

# Preserve original functionality - commented for reference
"""
Original file integration:

yfinance_data_loader.py:
- EURUSD data fetching with 7d period, 1h interval
- Column cleaning and renaming

indicators.py:  
- ADX, Stochastic_Oscillator, ATRBands, SupertrendIndicator, RSI classes
- Each with calculate() method and state management

strategy.py:
- ADX and Stochastic indicator application
- Signal generation for buy/sell based on DI crossovers and Stochastic crossovers

All original functionality is preserved through the legacy methods and
compatibility functions.
"""

# Example usage and testing
if __name__ == "__main__":
    # Test the complete pipeline
    print("Testing Trading Pipeline...")
    
    # Test legacy functionality
    print("\n1. Testing legacy EURUSD analysis...")
    legacy_results = run_eurusd_analysis()
    print(f"Legacy analysis completed: {legacy_results.get('summary', {})}")
    
    # Test new pipeline functionality
    print("\n2. Testing new pipeline...")
    pipeline = create_default_pipeline()
    status = pipeline.get_pipeline_status()
    print(f"Pipeline status: {status}")
    
    # Test with different symbol
    print("\n3. Testing with GBPUSD...")
    gbpusd_results = run_symbol_analysis('gbpusd', 'forex')
    if 'error' not in gbpusd_results:
        print(f"GBPUSD analysis completed: {len(gbpusd_results.get('strategy_results', {}))} strategies applied")
    else:
        print(f"Error: {gbpusd_results['error']}")
