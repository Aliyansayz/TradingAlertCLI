"""
Group Analysis Engine

This module provides analysis capabilities for symbol groups,
allowing batch processing of multiple symbols with different timeframes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import concurrent.futures
import threading
from dataclasses import dataclass

# Import our modules
from utility.symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig
from utility.indicators_oscillators import Oscillator, Oscillator_Status
from strategy import get_strategy

@dataclass
class SymbolAnalysisResult:
    """Result of analysis for a single symbol."""
    symbol_key: str
    symbol: str
    asset_type: str
    timeframe: str
    period: str
    success: bool
    error_message: str = ""
    data_points: int = 0
    latest_price: float = 0.0
    price_change: float = 0.0
    price_change_pct: float = 0.0
    last_7_prices: List[float] = None
    indicators: Dict[str, float] = None
    oscillator_status: Dict[str, Dict[str, Any]] = None
    signals_summary: Dict[str, int] = None
    overall_sentiment: str = "NEUTRAL"
    atr_bands: Dict[str, float] = None  # ATR-based stop loss/take profit levels
    analysis_timestamp: str = ""
    
    def __post_init__(self):
        if self.last_7_prices is None:
            self.last_7_prices = []
        if self.indicators is None:
            self.indicators = {}
        if self.oscillator_status is None:
            self.oscillator_status = {}
        if self.signals_summary is None:
            self.signals_summary = {"Buy": 0, "Sell": 0, "Neutral": 0}
        if self.atr_bands is None:
            self.atr_bands = {}
        if not self.analysis_timestamp:
            self.analysis_timestamp = datetime.now().isoformat()

@dataclass
class GroupAnalysisResult:
    """Result of analysis for an entire group."""
    group_id: str
    group_name: str
    total_symbols: int
    successful_analyses: int
    failed_analyses: int
    symbol_results: Dict[str, SymbolAnalysisResult]
    group_sentiment: str = "NEUTRAL"
    group_signals_summary: Dict[str, int] = None
    analysis_timestamp: str = ""
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.group_signals_summary is None:
            self.group_signals_summary = {"Buy": 0, "Sell": 0, "Neutral": 0}
        if not self.analysis_timestamp:
            self.analysis_timestamp = datetime.now().isoformat()

class SymbolDataFetcher:
    """Handles data fetching for individual symbols."""
    
    @staticmethod
    def fetch_symbol_data(config: SymbolConfig) -> pd.DataFrame:
        """Fetch data for a single symbol configuration."""
        try:
            # Import here to avoid circular imports
            # Import symbol mappings
            from utility.forex_symbols import get_forex_symbols
            from utility.crypto_symbols import get_crypto_symbols
            from utility.stocks_symbols import get_popular_stocks
            from utility.indices_symbols import get_indices_symbols
            
            # Get the correct yfinance symbol using the functions
            symbol_map = {
                'forex': get_forex_symbols(),
                'crypto': get_crypto_symbols(),
                'stocks': get_popular_stocks(),
                'indices': get_indices_symbols()
            }
            
            asset_map = symbol_map.get(config.asset_type, {})
            yf_symbol = asset_map.get(config.symbol.lower(), config.symbol)
            
            # Fetch data
            data = yf.download(yf_symbol, period=config.period, interval=config.timeframe, progress=False)
            
            if data.empty:
                return pd.DataFrame()
            
            # Clean data
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = ['_'.join(col).strip() for col in data.columns.values]
                data.columns = [col.replace(f'_{yf_symbol}', '').rstrip('_') for col in data.columns]
            
            # Standardize column names
            column_mapping = {
                'Open': 'open', 'High': 'high', 'Low': 'low',
                'Close': 'close', 'Volume': 'volume', 'Adj Close': 'adj_close'
            }
            data.rename(columns=column_mapping, inplace=True)
            data = data.dropna()
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {config.symbol}: {str(e)}")
            return pd.DataFrame()

class SymbolAnalyzer:
    """Handles analysis of individual symbols."""
    
    @staticmethod
    def analyze_symbol(symbol_key: str, config: SymbolConfig) -> SymbolAnalysisResult:
        """Perform complete analysis on a single symbol."""
        try:
            # Fetch data
            data = SymbolDataFetcher.fetch_symbol_data(config)
            
            if data.empty:
                return SymbolAnalysisResult(
                    symbol_key=symbol_key,
                    symbol=config.symbol,
                    asset_type=config.asset_type,
                    timeframe=config.timeframe,
                    period=config.period,
                    success=False,
                    error_message="No data available"
                )
            
            # Get the strategy to use (default to "default-check-single-timeframe")
            # This could be made configurable per symbol in the future
            strategy_name = getattr(config, 'strategy', 'default-check-single-timeframe')
            if strategy_name == 'single-check':  # Legacy name mapping
                strategy_name = 'default-check-single-timeframe'
            
            try:
                strategy = get_strategy(strategy_name)
            except ValueError:
                # Fallback to default strategy if unknown strategy specified
                strategy = get_strategy('default-check-single-timeframe')
            
            # Run strategy analysis
            analysis_result = strategy.analyze_symbol_data(data, symbol_key, config)
            
            if not analysis_result['success']:
                return SymbolAnalysisResult(
                    symbol_key=symbol_key,
                    symbol=config.symbol,
                    asset_type=config.asset_type,
                    timeframe=config.timeframe,
                    period=config.period,
                    success=False,
                    error_message=analysis_result.get('error_message', 'Strategy analysis failed')
                )
            
            # Create successful result from strategy output
            return SymbolAnalysisResult(
                symbol_key=symbol_key,
                symbol=config.symbol,
                asset_type=config.asset_type,
                timeframe=config.timeframe,
                period=config.period,
                success=True,
                data_points=len(data),
                latest_price=analysis_result['latest_price'],
                price_change=analysis_result['price_change'],
                price_change_pct=analysis_result['price_change_pct'],
                last_7_prices=analysis_result['last_7_prices'],
                indicators=analysis_result['indicators'],
                oscillator_status=analysis_result['oscillator_status'],
                signals_summary=analysis_result['signals_summary'],
                overall_sentiment=analysis_result['overall_sentiment'],
                atr_bands=analysis_result['atr_bands']
            )
            
        except Exception as e:
            return SymbolAnalysisResult(
                symbol_key=symbol_key,
                symbol=config.symbol,
                asset_type=config.asset_type,
                timeframe=config.timeframe,
                period=config.period,
                success=False,
                error_message=str(e)
            )

class GroupAnalysisEngine:
    """Main engine for analyzing symbol groups."""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
    
    def analyze_group(self, group: SymbolGroup, parallel: bool = True) -> GroupAnalysisResult:
        """Analyze all symbols in a group."""
        start_time = datetime.now()
        
        symbol_results = {}
        enabled_symbols = group.get_enabled_symbols()
        
        if parallel and len(enabled_symbols) > 1:
            # Parallel processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_symbol = {
                    executor.submit(SymbolAnalyzer.analyze_symbol, symbol_key, config): symbol_key
                    for symbol_key, config in enabled_symbols.items()
                }
                
                for future in concurrent.futures.as_completed(future_to_symbol):
                    symbol_key = future_to_symbol[future]
                    try:
                        result = future.result()
                        symbol_results[symbol_key] = result
                    except Exception as e:
                        print(f"Error analyzing {symbol_key}: {str(e)}")
                        symbol_results[symbol_key] = SymbolAnalysisResult(
                            symbol_key=symbol_key,
                            symbol=enabled_symbols[symbol_key].symbol,
                            asset_type=enabled_symbols[symbol_key].asset_type,
                            timeframe=enabled_symbols[symbol_key].timeframe,
                            period=enabled_symbols[symbol_key].period,
                            success=False,
                            error_message=str(e)
                        )
        else:
            # Sequential processing
            for symbol_key, config in enabled_symbols.items():
                result = SymbolAnalyzer.analyze_symbol(symbol_key, config)
                symbol_results[symbol_key] = result
        
        # Calculate group-level statistics
        successful_analyses = sum(1 for result in symbol_results.values() if result.success)
        failed_analyses = len(symbol_results) - successful_analyses
        
        # Aggregate signals
        group_signals_summary = {"Buy": 0, "Sell": 0, "Neutral": 0}
        for result in symbol_results.values():
            if result.success:
                for signal, count in result.signals_summary.items():
                    group_signals_summary[signal] += count
        
        # Determine group sentiment
        if group_signals_summary["Buy"] > group_signals_summary["Sell"]:
            group_sentiment = "BULLISH"
        elif group_signals_summary["Sell"] > group_signals_summary["Buy"]:
            group_sentiment = "BEARISH"
        else:
            group_sentiment = "NEUTRAL"
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return GroupAnalysisResult(
            group_id=group.group_id,
            group_name=group.name,
            total_symbols=len(enabled_symbols),
            successful_analyses=successful_analyses,
            failed_analyses=failed_analyses,
            symbol_results=symbol_results,
            group_sentiment=group_sentiment,
            group_signals_summary=group_signals_summary,
            execution_time=execution_time
        )
    
    def analyze_multiple_groups(self, 
                               group_ids: List[str], 
                               manager: SymbolGroupManager,
                               parallel: bool = True) -> Dict[str, GroupAnalysisResult]:
        """Analyze multiple groups."""
        results = {}
        
        for group_id in group_ids:
            group = manager.get_group(group_id)
            if group and group.enabled:
                print(f"Analyzing group: {group.name} ({group_id})...")
                result = self.analyze_group(group, parallel)
                results[group_id] = result
                print(f"✅ Completed {group.name}: {result.successful_analyses}/{result.total_symbols} symbols analyzed")
            else:
                print(f"❌ Group {group_id} not found or disabled")
        
        return results

class GroupAnalysisReporter:
    """Generates reports for group analysis results."""
    
    @staticmethod
    def print_symbol_result(result: SymbolAnalysisResult, detailed: bool = False) -> None:
        """Print results for a single symbol."""
        status_emoji = "✅" if result.success else "❌"
        sentiment_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}.get(result.overall_sentiment, "❓")
        
        price_change_str = f"{result.price_change:+.2f} ({result.price_change_pct:+.1f}%)"
        
        print(f"{status_emoji} {result.symbol_key:<12} | {result.symbol:<8} | {result.timeframe:<4} | "
              f"${result.latest_price:>8,.4f} | {price_change_str:>12} | {sentiment_emoji} {result.overall_sentiment}")
        
        if detailed and result.success:
            # Show signals breakdown
            print(f"    📊 Signals: Buy={result.signals_summary['Buy']}, Sell={result.signals_summary['Sell']}, Neutral={result.signals_summary['Neutral']}")
            print(f"    📈 Data Points: {result.data_points}")
            
            # Show last 7 prices
            if result.last_7_prices:
                prices_str = ", ".join([f"${p:.4f}" for p in result.last_7_prices])
                print(f"    💰 Last 7 Prices: {prices_str}")
            
            # Show key indicators
            if result.indicators:
                key_indicators = ['RSI_14', 'MACD', 'CCI_20', 'Williams_R']
                indicator_str = ", ".join([f"{k}={result.indicators.get(k, 0):.2f}" for k in key_indicators if k in result.indicators])
                print(f"    📋 Key Indicators: {indicator_str}")
            
            # Show oscillator status details
            if result.oscillator_status:
                print(f"    🎯 Oscillator Status:")
                for oscillator, status_data in result.oscillator_status.items():
                    status = status_data.get('status', 'Unknown')
                    value = status_data.get('value', 0)
                    prev_value = status_data.get('previous_value')
                    trend = ""
                    if prev_value is not None:
                        if value > prev_value:
                            trend = " ↗️"
                        elif value < prev_value:
                            trend = " ↘️"
                        else:
                            trend = " ➡️"
                    
                    print(f"       {oscillator}: {status} (Value: {value:.2f}{trend})")
            
            # Show ATR bands for stop loss/take profit
            if result.atr_bands and result.overall_sentiment != "NEUTRAL":
                print(f"    🎯 ATR Trading Levels:")
                atr_value = result.atr_bands.get('atr_value', 0)
                print(f"       ATR(14): {atr_value:.4f}")
                
                if result.overall_sentiment == "BULLISH":
                    stop_loss = result.atr_bands.get('stop_loss_long', 0)
                    take_profit = result.atr_bands.get('take_profit_long', 0)
                    print(f"       🟢 LONG Setup: SL=${stop_loss:.4f}, TP=${take_profit:.4f}")
                elif result.overall_sentiment == "BEARISH":
                    stop_loss = result.atr_bands.get('stop_loss_short', 0)
                    take_profit = result.atr_bands.get('take_profit_short', 0)
                    print(f"       🔴 SHORT Setup: SL=${stop_loss:.4f}, TP=${take_profit:.4f}")
        
        if not result.success:
            print(f"    ❌ Error: {result.error_message}")
    
    @staticmethod
    def print_group_result(result: GroupAnalysisResult, detailed: bool = True) -> None:
        """Print results for an entire group."""
        print(f"\n{'='*100}")
        print(f"GROUP ANALYSIS: {result.group_name} ({result.group_id})")
        print(f"{'='*100}")
        
        # Summary statistics
        success_rate = (result.successful_analyses / result.total_symbols * 100) if result.total_symbols > 0 else 0
        sentiment_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}.get(result.group_sentiment, "❓")
        
        print(f"📊 Summary:")
        print(f"   Total Symbols: {result.total_symbols}")
        print(f"   Successful: {result.successful_analyses} ({success_rate:.1f}%)")
        print(f"   Failed: {result.failed_analyses}")
        print(f"   Execution Time: {result.execution_time:.2f}s")
        print(f"   Group Sentiment: {sentiment_emoji} {result.group_sentiment}")
        print(f"   Group Signals: Buy={result.group_signals_summary['Buy']}, Sell={result.group_signals_summary['Sell']}, Neutral={result.group_signals_summary['Neutral']}")
        
        # Symbol results
        print(f"\n📈 Symbol Results:")
        print(f"{'Status':<2} {'Key':<12} | {'Symbol':<8} | {'TF':<4} | {'Price':<12} | {'Change':<12} | {'Sentiment'}")
        print("-" * 100)
        
        # Sort by success first, then by sentiment
        sorted_results = sorted(result.symbol_results.values(), 
                              key=lambda x: (x.success, x.overall_sentiment == "BULLISH", -x.price_change_pct))
        
        for symbol_result in sorted_results:
            GroupAnalysisReporter.print_symbol_result(symbol_result, detailed=detailed)
    
    @staticmethod
    def print_multiple_groups_summary(results: Dict[str, GroupAnalysisResult]) -> None:
        """Print summary for multiple groups."""
        print(f"\n{'='*120}")
        print(f"MULTIPLE GROUPS ANALYSIS SUMMARY")
        print(f"{'='*120}")
        
        total_groups = len(results)
        total_symbols = sum(r.total_symbols for r in results.values())
        total_successful = sum(r.successful_analyses for r in results.values())
        total_execution_time = sum(r.execution_time for r in results.values())
        
        print(f"📊 Overall Summary:")
        print(f"   Groups Analyzed: {total_groups}")
        print(f"   Total Symbols: {total_symbols}")
        print(f"   Successful Analyses: {total_successful} ({total_successful/total_symbols*100:.1f}%)")
        print(f"   Total Execution Time: {total_execution_time:.2f}s")
        
        print(f"\n📈 Group Results:")
        print(f"{'Group ID':<15} | {'Name':<25} | {'Symbols':<8} | {'Success':<8} | {'Sentiment':<10} | {'Time':<8}")
        print("-" * 120)
        
        for group_id, result in results.items():
            success_rate = f"{result.successful_analyses}/{result.total_symbols}"
            sentiment_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}.get(result.group_sentiment, "❓")
            sentiment_str = f"{sentiment_emoji} {result.group_sentiment}"
            
            print(f"{group_id:<15} | {result.group_name:<25} | {success_rate:<8} | "
                  f"{result.successful_analyses/result.total_symbols*100:>6.1f}% | {sentiment_str:<15} | {result.execution_time:>6.2f}s")

# Example usage and testing
if __name__ == "__main__":
    # Initialize components
    manager = SymbolGroupManager()
    engine = GroupAnalysisEngine(max_workers=3)
    
    print("🚀 Starting Group Analysis Engine Test")
    print("="*60)
    
    # List available groups
    groups = manager.list_groups(enabled_only=True)
    if not groups:
        print("❌ No groups found. Creating predefined groups...")
        from utility.symbol_groups_manager import create_predefined_groups
        create_predefined_groups(manager)
        groups = manager.list_groups(enabled_only=True)
    
    print(f"📋 Available groups: {[g.group_id for g in groups]}")
    
    # Analyze first group as example
    if groups:
        first_group = groups[0]
        print(f"\n🔍 Analyzing group: {first_group.name}")
        
        result = engine.analyze_group(first_group)
        GroupAnalysisReporter.print_group_result(result)
        
        print(f"\n{'='*60}")
        print("GROUP ANALYSIS ENGINE READY")
        print(f"{'='*60}")
    else:
        print("❌ No groups available for testing")
