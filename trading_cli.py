#!/usr/bin/env python3
"""
Trading Analysis CLI Menu System

This module provides a comprehensive command-line interface for managing
symbol groups, running sentiment analysis, and configuring trading indicators.
Features:
- Arrow key navigation support
- Case-insensitive commands (ext/clr to exit)
- Periodic unit testing for symbols
- Directional indicators display
- Enhanced crossover status tracking
"""

import sys
import os
import json
import time
import pandas as pd
import yfinance as yf
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading

# Keyboard input handling
try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    import termios, tty  # Unix/Linux/Mac
    WINDOWS = False

# Install schedule if not available
try:
    import schedule
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule

# Add backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utility.symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig, IndicatorSettings as SGIndicatorSettings, PeriodicAlertConfig
from workflow.group_analysis_engine import GroupAnalysisEngine, GroupAnalysisReporter
from workflow.enhanced_forex_indices_analysis import enhanced_group_sentiment_analysis, detailed_individual_analysis
from workflow.periodic_alerts_engine import PeriodicAlertsEngine, AlertEvent

class KeyboardInput:
    """Enhanced keyboard input handling with arrow keys and special characters."""
    
    @staticmethod
    def get_char():
        """Get a single character from keyboard input."""
        if WINDOWS:
            return msvcrt.getch().decode('utf-8')
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.cbreak(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
    
    @staticmethod
    def get_arrow_key():
        """Detect arrow key presses."""
        if WINDOWS:
            key = msvcrt.getch()
            if key == b'\xe0':  # Arrow key prefix on Windows
                key = msvcrt.getch()
                if key == b'H':    # Up arrow
                    return 'UP'
                elif key == b'P':  # Down arrow
                    return 'DOWN'
                elif key == b'K':  # Left arrow
                    return 'LEFT'
                elif key == b'M':  # Right arrow
                    return 'RIGHT'
            return key.decode('utf-8', errors='ignore')
        else:
            key = sys.stdin.read(1)
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
                if key == '\x1b[A':    # Up arrow
                    return 'UP'
                elif key == '\x1b[B':  # Down arrow
                    return 'DOWN'
                elif key == '\x1b[C':  # Right arrow
                    return 'RIGHT'
                elif key == '\x1b[D':  # Left arrow
                    return 'LEFT'
            return key
    
    @staticmethod
    def enhanced_input(prompt: str, allow_special: bool = True) -> str:
        """Enhanced input with arrow key support and special commands."""
        print(prompt, end='', flush=True)
        
        if allow_special:
            print(" (Use +/- for enable/disable, arrow keys to navigate, 'ext'/'clr' to exit)")
        
        user_input = input().strip()
        
        # Handle case-insensitive exit commands
        if user_input.lower() in ['ext', 'clr', 'exit', 'clear', 'quit']:
            return 'EXIT'
        
        # Handle special characters
        if user_input in ['+', '-']:
            return user_input
        
        return user_input

class IndicatorSettings:
    """Manages indicator settings and crossover configurations."""
    
    def __init__(self):
        self.settings = {
            "timeframe_strategy": "default-check-single-timeframe",
            "crossover_enabled": True,
            "crossover_indicators": {
                "stochastic": True,
                "supertrend": True,
                "dmi": True,
                "rsi": False,
                "macd": False
            },
            "lookback_period": 7,
            "adx_volatility_filter": True,
            "adx_threshold": 18,
            "oscillator_indicators_active": True,
            "directional_analysis": True,  # Show direction of indicators
            "crossover_range": 7  # Can be set different for each symbol
        }
        
        # Per-symbol crossover range settings
        self.symbol_crossover_ranges = {}
    
    def set_symbol_crossover_range(self, symbol_key: str, range_value: int):
        """Set crossover range for specific symbol."""
        self.symbol_crossover_ranges[symbol_key] = range_value
    
    def get_symbol_crossover_range(self, symbol_key: str) -> int:
        """Get crossover range for specific symbol."""
        return self.symbol_crossover_ranges.get(symbol_key, self.settings["crossover_range"])
    
    def toggle_indicator(self, indicator_name: str) -> bool:
        """Toggle indicator activation using + or - keys."""
        if indicator_name in self.settings["crossover_indicators"]:
            current_state = self.settings["crossover_indicators"][indicator_name]
            self.settings["crossover_indicators"][indicator_name] = not current_state
            return self.settings["crossover_indicators"][indicator_name]
        return False
    
    def get_directional_analysis(self, symbol_data: pd.DataFrame, indicators: Dict) -> Dict[str, str]:
        """Analyze directional movement of indicators."""
        directions = {}
        
        if len(symbol_data) < 2:
            return directions
        
        try:
            # Supertrend direction
            if 'direction' in symbol_data.columns:
                current_trend = symbol_data['direction'].iloc[-1]
                prev_trend = symbol_data['direction'].iloc[-2] if len(symbol_data) > 1 else current_trend
                
                if current_trend and not prev_trend:
                    directions['Supertrend'] = "🟢 BULLISH (Trend Changed Up)"
                elif not current_trend and prev_trend:
                    directions['Supertrend'] = "🔴 BEARISH (Trend Changed Down)"
                elif current_trend:
                    directions['Supertrend'] = "🟢 BULLISH (Continuing)"
                else:
                    directions['Supertrend'] = "🔴 BEARISH (Continuing)"
            
            # Stochastic direction (%K vs %D)
            if '%K' in symbol_data.columns and '%D' in symbol_data.columns:
                k_current = symbol_data['%K'].iloc[-1]
                d_current = symbol_data['%D'].iloc[-1]
                k_prev = symbol_data['%K'].iloc[-2] if len(symbol_data) > 1 else k_current
                d_prev = symbol_data['%D'].iloc[-2] if len(symbol_data) > 1 else d_current
                
                if k_current > d_current:
                    if k_prev <= d_prev:
                        directions['Stochastic'] = "🟢 %K Above %D (Just Crossed Up)"
                    else:
                        directions['Stochastic'] = "🟢 %K Above %D (Continuing)"
                else:
                    if k_prev >= d_prev:
                        directions['Stochastic'] = "🔴 %K Below %D (Just Crossed Down)"
                    else:
                        directions['Stochastic'] = "🔴 %K Below %D (Continuing)"
            
            # DMI direction (+DI vs -DI)
            if '+DI' in symbol_data.columns and '-DI' in symbol_data.columns:
                pdi_current = symbol_data['+DI'].iloc[-1]
                ndi_current = symbol_data['-DI'].iloc[-1]
                pdi_prev = symbol_data['+DI'].iloc[-2] if len(symbol_data) > 1 else pdi_current
                ndi_prev = symbol_data['-DI'].iloc[-2] if len(symbol_data) > 1 else ndi_current
                
                if pdi_current > ndi_current:
                    if pdi_prev <= ndi_prev:
                        directions['DMI'] = "🟢 +DI Above -DI (Just Crossed Up)"
                    else:
                        directions['DMI'] = "🟢 +DI Above -DI (Continuing)"
                else:
                    if pdi_prev >= ndi_prev:
                        directions['DMI'] = "🔴 +DI Below -DI (Just Crossed Down)"
                    else:
                        directions['DMI'] = "🔴 +DI Below -DI (Continuing)"
                        
        except Exception as e:
            print(f"Error in directional analysis: {e}")
        
        return directions
    
    def get_crossover_status(self, symbol_data: pd.DataFrame, symbol_key: str) -> Dict[str, Any]:
        """Get crossover status for the last N periods (configurable per symbol)."""
        crossover_range = self.get_symbol_crossover_range(symbol_key)
        crossovers = {}
        
        if len(symbol_data) < crossover_range:
            return crossovers
        
        try:
            # Check for crossovers in the specified range
            recent_data = symbol_data.tail(crossover_range)
            
            # Stochastic crossovers
            if '%K' in recent_data.columns and '%D' in recent_data.columns:
                k_series = recent_data['%K']
                d_series = recent_data['%D']
                
                bullish_cross = ((k_series.shift(1) < d_series.shift(1)) & (k_series > d_series)).any()
                bearish_cross = ((k_series.shift(1) > d_series.shift(1)) & (k_series < d_series)).any()
                
                if bullish_cross:
                    crossovers['Stochastic'] = f"🟢 BULLISH Crossover (Last {crossover_range} periods)"
                elif bearish_cross:
                    crossovers['Stochastic'] = f"🔴 BEARISH Crossover (Last {crossover_range} periods)"
                else:
                    crossovers['Stochastic'] = f"⚪ No Crossover (Last {crossover_range} periods)"
            
            # DMI crossovers
            if '+DI' in recent_data.columns and '-DI' in recent_data.columns:
                pdi_series = recent_data['+DI']
                ndi_series = recent_data['-DI']
                
                bullish_cross = ((pdi_series.shift(1) < ndi_series.shift(1)) & (pdi_series > ndi_series)).any()
                bearish_cross = ((pdi_series.shift(1) > ndi_series.shift(1)) & (pdi_series < ndi_series)).any()
                
                if bullish_cross:
                    crossovers['DMI'] = f"🟢 BULLISH Crossover (Last {crossover_range} periods)"
                elif bearish_cross:
                    crossovers['DMI'] = f"🔴 BEARISH Crossover (Last {crossover_range} periods)"
                else:
                    crossovers['DMI'] = f"⚪ No Crossover (Last {crossover_range} periods)"
            
            # Supertrend direction changes
            if 'direction' in recent_data.columns:
                direction_series = recent_data['direction']
                
                bullish_change = ((direction_series.shift(1) == False) & (direction_series == True)).any()
                bearish_change = ((direction_series.shift(1) == True) & (direction_series == False)).any()
                
                if bullish_change:
                    crossovers['Supertrend'] = f"🟢 BULLISH Trend Change (Last {crossover_range} periods)"
                elif bearish_change:
                    crossovers['Supertrend'] = f"🔴 BEARISH Trend Change (Last {crossover_range} periods)"
                else:
                    crossovers['Supertrend'] = f"⚪ No Trend Change (Last {crossover_range} periods)"
                    
        except Exception as e:
            print(f"Error in crossover analysis: {e}")
        
        return crossovers

class PeriodicUnitTester:
    """Handles periodic unit testing of individual symbols in groups."""
    
    def __init__(self, manager: 'SymbolGroupManager', engine: 'GroupAnalysisEngine'):
        self.manager = manager
        self.engine = engine
        self.test_results = {}
        self.test_schedule = {}
        
    def schedule_symbol_test(self, group_id: str, symbol_key: str, interval_minutes: int):
        """Schedule periodic testing for a specific symbol."""
        test_key = f"{group_id}_{symbol_key}"
        
        def run_test():
            self.run_symbol_unit_test(group_id, symbol_key)
        
        # Clear existing schedule for this symbol
        if test_key in self.test_schedule:
            schedule.cancel_job(self.test_schedule[test_key])
        
        # Schedule new test
        job = schedule.every(interval_minutes).minutes.do(run_test)
        self.test_schedule[test_key] = job
        
        print(f"✅ Scheduled unit test for {symbol_key} every {interval_minutes} minutes")
    
    def run_symbol_unit_test(self, group_id: str, symbol_key: str):
        """Run unit test for a specific symbol."""
        try:
            group = self.manager.get_group(group_id)
            if not group or symbol_key not in group.symbols:
                print(f"❌ Symbol {symbol_key} not found in group {group_id}")
                return
            
            config = group.symbols[symbol_key]
            if not config.enabled:
                print(f"⚠️ Symbol {symbol_key} is disabled, skipping test")
                return
            
            print(f"🔍 Running unit test for {symbol_key} in {group.name}")
            
            # Run analysis
            from workflow.group_analysis_engine import SymbolAnalyzer
            result = SymbolAnalyzer.analyze_symbol(symbol_key, config)
            
            # Store result
            test_key = f"{group_id}_{symbol_key}"
            self.test_results[test_key] = {
                'timestamp': datetime.now().isoformat(),
                'result': result,
                'success': result.success
            }
            
            # Display quick summary
            if result.success:
                print(f"✅ {symbol_key}: ${result.latest_price:.4f} ({result.price_change_pct:+.1f}%) - {result.overall_sentiment}")
            else:
                print(f"❌ {symbol_key}: Test failed - {result.error_message}")
                
        except Exception as e:
            print(f"❌ Error in unit test for {symbol_key}: {e}")
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all unit test results."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r['success'])
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def stop_all_tests(self):
        """Stop all scheduled unit tests."""
        for job in self.test_schedule.values():
            schedule.cancel_job(job)
        self.test_schedule.clear()
        print("🛑 All unit tests stopped")

class SchedulerSettings:
    """Manages default scheduler settings for new groups."""
    
    def __init__(self):
        self.settings = {
            "auto_run_enabled": False,
            "schedule_interval": 15,  # minutes
            "schedule_weekdays": [0, 1, 2, 3, 4],  # Monday to Friday
            "periodic_alerts": True,
            "alert_summary": True
        }
    
    def to_dict(self):
        return self.settings.copy()

class PeriodicRunner:
    """Handles periodic analysis runs and alerts."""
    
    def __init__(self, manager: SymbolGroupManager, engine: GroupAnalysisEngine):
        self.manager = manager
        self.engine = engine
        self.running = False
        self.scheduler_thread = None
        self.last_run_results = {}
    
    def start_scheduler(self):
        """Start the periodic scheduler."""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            print("📅 Periodic scheduler started")
    
    def stop_scheduler(self):
        """Stop the periodic scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        print("📅 Periodic scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def schedule_group_analysis(self, group_id: str, interval_minutes: int, weekdays: List[int]):
        """Schedule periodic analysis for a specific group."""
        def run_analysis():
            if datetime.now().weekday() in weekdays:
                try:
                    group = self.manager.get_group(group_id)
                    if group and group.enabled:
                        result = self.engine.analyze_group(group)
                        self.last_run_results[group_id] = result
                        self._send_alert(group_id, result)
                except Exception as e:
                    print(f"❌ Error in scheduled analysis for {group_id}: {str(e)}")
        
        # Clear existing jobs for this group
        schedule.clear(group_id)
        
        # Schedule new job
        schedule.every(interval_minutes).minutes.do(run_analysis).tag(group_id)
        print(f"📅 Scheduled {group_id} analysis every {interval_minutes} minutes")
    
    def _send_alert(self, group_id: str, result):
        """Send alert with analysis results."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔔 PERIODIC ALERT [{timestamp}] - Group: {result.group_name}")
        print(f"   Success: {result.successful_analyses}/{result.total_symbols}")
        print(f"   Sentiment: {result.group_sentiment}")
        print(f"   Signals: Buy={result.group_signals_summary['Buy']}, Sell={result.group_signals_summary['Sell']}")

class TradingCLI:
    """Main CLI interface for trading analysis system."""
    
    def __init__(self):
        self.manager = SymbolGroupManager()
        self.engine = GroupAnalysisEngine(max_workers=3)
        self.indicator_settings = IndicatorSettings()
        self.scheduler_settings = SchedulerSettings()
        self.periodic_runner = PeriodicRunner(self.manager, self.engine)
        self.unit_tester = PeriodicUnitTester(self.manager, self.engine)  # Add unit tester
        self.alerts_engine = PeriodicAlertsEngine(self.manager, self._alert_notification_callback)  # Add alerts engine
        self.last_analyzed_group = None
        self.running = True
    
    def _supports_unicode(self):
        """Check if terminal supports Unicode emojis"""
        try:
            import sys
            # Test if we can encode Unicode emojis
            "🚀".encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, LookupError):
            return False
    
    def display_main_menu(self):
        """Display the main menu options."""
        print("\n" + "="*80)
        print("🚀 TRADING ANALYSIS CLI - MAIN MENU" if self._supports_unicode() else "TRADING ANALYSIS CLI - MAIN MENU")
        print("="*80)
        print("📊 ANALYSIS OPTIONS:" if self._supports_unicode() else "ANALYSIS OPTIONS:")
        print("  1. Run sentiment analysis of a symbol")
        print("  2. Run sentiment analysis of a symbol group")
        print("  3. Run sentiment analysis of last symbol group")
        print()
        print("⚙️  CONFIGURATION OPTIONS:" if self._supports_unicode() else "CONFIGURATION OPTIONS:")
        print("  4. Modify indicator settings of a symbol group")
        print("  5. Create a new symbol group")
        print("  6. Manage scheduler settings")
        print("  7. Manage indicator settings")
        print("  12. Configure symbol-specific settings")  # New option
        print("  13. Configure periodic alerts")  # New option
        print("  16. Configure symbol scheduler settings")  # New option
        print("  17. Strategy Management")  # New strategy management option
        print()
        print("📋 MANAGEMENT OPTIONS:" if self._supports_unicode() else "MANAGEMENT OPTIONS:")
        print("  8. List all symbol groups")
        print("  9. View periodic runner status")
        print("  10. Start/Stop periodic scheduler")
        print("  11. Manage periodic unit testing")  # Existing option
        print("  14. Manage periodic alerts")  # New option
        print("  15. View alerts history")  # New option
        print()
        print("  0. Exit (or type 'ext'/'clr')")
        print("="*80)
        print("💡 Tips: Use arrow keys to navigate, +/- to enable/disable, 'ext'/'clr' to exit" if self._supports_unicode() else "Tips: Use arrow keys to navigate, +/- to enable/disable, 'ext'/'clr' to exit")
        
        if self.last_analyzed_group:
            print(f"📌 Last analyzed group: {self.last_analyzed_group}")
        
        print("Select an option (0-17): ", end="")
    
    def run_single_symbol_analysis(self):
        """Run analysis for a single symbol with enhanced directional and crossover analysis."""
        print("\n📊 SINGLE SYMBOL ANALYSIS")
        print("-" * 40)
        
        symbol = KeyboardInput.enhanced_input("Enter symbol (e.g., EURUSD, AAPL, BTC): ", False).strip().upper()
        if symbol == 'EXIT':
            return
        if not symbol:
            print("❌ Invalid symbol")
            return
        
        print("\nAsset types:")
        print("1. Forex")
        print("2. Stocks") 
        print("3. Crypto")
        print("4. Indices")
        
        asset_choice = KeyboardInput.enhanced_input("Select asset type (1-4): ", False).strip()
        if asset_choice == 'EXIT':
            return
        
        asset_map = {"1": "forex", "2": "stocks", "3": "crypto", "4": "indices"}
        asset_type = asset_map.get(asset_choice)
        
        if not asset_type:
            print("❌ Invalid asset type")
            return
        
        timeframe = KeyboardInput.enhanced_input("Enter timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d): ", False).strip()
        if timeframe == 'EXIT':
            return
        
        period = KeyboardInput.enhanced_input("Enter period (1d, 5d, 1mo, 3mo, 6mo, 1y): ", False).strip()
        if period == 'EXIT':
            return
        
        # Create temporary symbol config
        config = SymbolConfig(
            symbol=symbol.lower(),
            asset_type=asset_type,
            timeframe=timeframe,
            period=period,
            enabled=True
        )
        
        print(f"\n🔍 Analyzing {symbol} ({asset_type})...")
        
        try:
            from workflow.group_analysis_engine import SymbolAnalyzer, SymbolDataFetcher
            result = SymbolAnalyzer.analyze_symbol(f"{symbol}_{timeframe}", config)
            
            if result.success:
                print(f"\n✅ Analysis completed successfully!")
                GroupAnalysisReporter.print_symbol_result(result, detailed=True)
                
                # Get raw data for directional and crossover analysis
                raw_data = SymbolDataFetcher.fetch_symbol_data(config)
                
                if not raw_data.empty:
                    # Apply indicators to get directional data
                    from indicators import ADX, Stochastic_Oscillator, SupertrendIndicator
                    
                    # Calculate indicators with the data
                    adx_indicator = ADX(adx_period=14)
                    stoch_indicator = Stochastic_Oscillator(k_period=14, k_smooth=3, d_period=3)
                    supertrend_indicator = SupertrendIndicator(period=10, multiplier=3.0)
                    
                    # Calculate indicator values
                    raw_data['+DI'], raw_data['-DI'], raw_data['ADX'] = adx_indicator.calculate(raw_data)
                    raw_data['%K'], raw_data['%D'] = stoch_indicator.calculate(raw_data)
                    raw_data['supetrend'], raw_data['direction'] = supertrend_indicator.calculate(raw_data)
                    
                    # Get directional analysis
                    directions = self.indicator_settings.get_directional_analysis(raw_data, result.indicators)
                    
                    # Get crossover status
                    symbol_key = f"{symbol}_{timeframe}"
                    crossover_status = self.indicator_settings.get_crossover_status(raw_data, symbol_key)
                    
                    # Display enhanced analysis
                    print(f"\n{'='*60}")
                    print(f"🎯 DIRECTIONAL INDICATOR ANALYSIS")
                    print(f"{'='*60}")
                    
                    if directions:
                        for indicator, direction in directions.items():
                            print(f"   {indicator:<15}: {direction}")
                    else:
                        print("   No directional data available")
                    
                    print(f"\n{'='*60}")
                    print(f"⚡ CROSSOVER STATUS (Last {self.indicator_settings.get_symbol_crossover_range(symbol_key)} periods)")
                    print(f"{'='*60}")
                    
                    if crossover_status:
                        for indicator, status in crossover_status.items():
                            print(f"   {indicator:<15}: {status}")
                    else:
                        print("   No crossover data available")
                    
                    # Show detailed analysis
                    print(f"\n{'='*60}")
                    print(f"📊 DETAILED ANALYSIS: {symbol}")
                    print(f"{'='*60}")
                    detailed_individual_analysis(None, result)
                
            else:
                print(f"❌ Analysis failed: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def run_group_analysis(self):
        """Run analysis for a symbol group."""
        print("\n📊 SYMBOL GROUP ANALYSIS")
        print("-" * 40)
        
        groups = self.manager.list_groups()
        if not groups:
            print("❌ No symbol groups found. Create a group first.")
            input("Press Enter to continue...")
            return
        
        print("Available groups:")
        for i, group in enumerate(groups, 1):
            enabled_count = len(group.get_enabled_symbols())
            status = "🟢" if group.enabled else "🔴"
            print(f"  {i}. {status} {group.name} ({group.group_id}) - {enabled_count} symbols")
        
        try:
            choice = int(input(f"\nSelect group (1-{len(groups)}): "))
            if 1 <= choice <= len(groups):
                selected_group = groups[choice - 1]
                self.last_analyzed_group = f"{selected_group.name} ({selected_group.group_id})"
                
                print(f"\n🔍 Analyzing group: {selected_group.name}...")
                result = self.engine.analyze_group(selected_group)
                
                GroupAnalysisReporter.print_group_result(result, detailed=True)
                enhanced_group_sentiment_analysis(result)
                
                # Ask if user wants detailed individual analysis
                show_detailed = input("\nShow detailed individual analysis? (y/n): ").strip().lower()
                if show_detailed == 'y':
                    for symbol_key, symbol_result in result.symbol_results.items():
                        if symbol_result.success:
                            detailed_individual_analysis(result, symbol_result)
                            input("\nPress Enter for next symbol...")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def run_last_group_analysis(self):
        """Re-run analysis for the last analyzed group."""
        if not self.last_analyzed_group:
            print("❌ No previous group analysis found")
            input("Press Enter to continue...")
            return
        
        print(f"\n📊 RE-ANALYZING LAST GROUP: {self.last_analyzed_group}")
        print("-" * 60)
        
        # Extract group_id from last_analyzed_group string
        group_id = self.last_analyzed_group.split("(")[-1].split(")")[0]
        group = self.manager.get_group(group_id)
        
        if not group:
            print("❌ Last analyzed group no longer exists")
            self.last_analyzed_group = None
            input("Press Enter to continue...")
            return
        
        print(f"🔍 Re-analyzing group: {group.name}...")
        result = self.engine.analyze_group(group)
        
        GroupAnalysisReporter.print_group_result(result, detailed=True)
        enhanced_group_sentiment_analysis(result)
        
        input("\nPress Enter to continue...")
    
    def modify_group_indicator_settings(self):
        """Modify indicator settings for a specific group."""
        print("\n⚙️ MODIFY GROUP INDICATOR SETTINGS")
        print("-" * 40)
        
        groups = self.manager.list_groups()
        if not groups:
            print("❌ No symbol groups found")
            input("Press Enter to continue...")
            return
        
        print("Available groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group.name} ({group.group_id})")
        
        try:
            choice = int(input(f"\nSelect group (1-{len(groups)}): "))
            if 1 <= choice <= len(groups):
                selected_group = groups[choice - 1]
                
                # Show current settings
                print(f"\n📋 Current indicator settings for {selected_group.name}:")
                current_settings = getattr(selected_group, 'indicator_settings', self.indicator_settings.to_dict())
                for key, value in current_settings.items():
                    print(f"  {key}: {value}")
                
                print("\nModification options:")
                print("1. Toggle crossover feature")
                print("2. Modify lookback period")
                print("3. Toggle ADX volatility filter")
                print("4. Change ADX threshold")
                print("5. Toggle specific indicator crossovers")
                
                mod_choice = input("Select option (1-5): ").strip()
                
                if mod_choice == "1":
                    current = current_settings.get("crossover_enabled", True)
                    new_value = not current
                    current_settings["crossover_enabled"] = new_value
                    print(f"✅ Crossover feature {'enabled' if new_value else 'disabled'}")
                
                elif mod_choice == "2":
                    current = current_settings.get("lookback_period", 7)
                    new_period = int(input(f"Enter new lookback period (current: {current}): "))
                    current_settings["lookback_period"] = new_period
                    print(f"✅ Lookback period set to {new_period}")
                
                elif mod_choice == "3":
                    current = current_settings.get("adx_volatility_filter", True)
                    new_value = not current
                    current_settings["adx_volatility_filter"] = new_value
                    print(f"✅ ADX volatility filter {'enabled' if new_value else 'disabled'}")
                
                elif mod_choice == "4":
                    current = current_settings.get("adx_threshold", 18)
                    new_threshold = float(input(f"Enter new ADX threshold (current: {current}): "))
                    current_settings["adx_threshold"] = new_threshold
                    print(f"✅ ADX threshold set to {new_threshold}")
                
                elif mod_choice == "5":
                    self._modify_indicator_crossovers(current_settings)
                
                # Save settings to group
                selected_group.metadata["indicator_settings"] = current_settings
                self.manager.save_group(selected_group)
                print("✅ Settings saved successfully")
            
        except (ValueError, KeyError) as e:
            print(f"❌ Error: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def _modify_indicator_crossovers(self, settings):
        """Modify crossover settings for specific indicators."""
        crossover_indicators = settings.get("crossover_indicators", {})
        
        print("\n📊 Indicator Crossover Settings:")
        indicators = ["stochastic", "supertrend", "dmi", "rsi", "macd"]
        
        for i, indicator in enumerate(indicators, 1):
            status = "+" if crossover_indicators.get(indicator, False) else "-"
            print(f"  {status} {i}. {indicator.upper()}")
        
        print("\nUse '+' to enable, '-' to disable, or number to toggle")
        choice = input("Enter choice: ").strip()
        
        if choice.startswith('+'):
            indicator_num = int(choice[1:]) - 1
            if 0 <= indicator_num < len(indicators):
                crossover_indicators[indicators[indicator_num]] = True
                print(f"✅ {indicators[indicator_num].upper()} crossover enabled")
        
        elif choice.startswith('-'):
            indicator_num = int(choice[1:]) - 1
            if 0 <= indicator_num < len(indicators):
                crossover_indicators[indicators[indicator_num]] = False
                print(f"❌ {indicators[indicator_num].upper()} crossover disabled")
        
        elif choice.isdigit():
            indicator_num = int(choice) - 1
            if 0 <= indicator_num < len(indicators):
                current = crossover_indicators.get(indicators[indicator_num], False)
                crossover_indicators[indicators[indicator_num]] = not current
                status = "enabled" if not current else "disabled"
                print(f"🔄 {indicators[indicator_num].upper()} crossover {status}")
        
        settings["crossover_indicators"] = crossover_indicators
    
    def create_symbol_group(self):
        """Create a new symbol group with all configuration options."""
        print("\n🏗️ CREATE NEW SYMBOL GROUP")
        print("-" * 40)
        
        # Basic group information
        group_name = input("Enter group name: ").strip()
        if not group_name:
            print("❌ Group name is required")
            return
        
        description = input("Enter description (optional): ").strip()
        
        # Generate group ID
        group_id = group_name.lower().replace(" ", "_").replace("-", "_")
        
        # Add symbols
        symbols = {}
        print("\n📊 Add symbols to the group:")
        print("Enter symbols one by one. Press Enter without input to finish.")
        
        while True:
            symbol = input(f"Symbol {len(symbols)+1} (or Enter to finish): ").strip()
            if not symbol:
                break
            
            print("Asset types: 1.Forex 2.Stocks 3.Crypto 4.Indices")
            asset_choice = input("Asset type (1-4): ").strip()
            asset_map = {"1": "forex", "2": "stocks", "3": "crypto", "4": "indices"}
            asset_type = asset_map.get(asset_choice, "forex")
            
            timeframe = input("Timeframe (15m, 30m, 1h, 4h, 1d): ").strip() or "15m"
            period = input("Period (1d, 5d, 1mo, 3mo): ").strip() or "5d"
            
            symbol_key = f"{symbol.lower()}_{timeframe}"
            symbols[symbol_key] = SymbolConfig(
                symbol=symbol.lower(),
                asset_type=asset_type,
                timeframe=timeframe,
                period=period,
                enabled=True
            )
            print(f"✅ Added {symbol} ({asset_type}) with {timeframe} timeframe")
        
        if not symbols:
            print("❌ At least one symbol is required")
            return
        
        # Periodic alert feature
        print("\n🔔 PERIODIC ALERT CONFIGURATION:")
        periodic_alerts = input("Enable periodic alerts? (y/n): ").strip().lower() == 'y'
        
        # Auto run scheduling
        print("\n📅 SCHEDULING CONFIGURATION:")
        auto_run = input("Enable auto run scheduling? (y/n): ").strip().lower() == 'y'
        schedule_interval = 15
        schedule_weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
        
        if auto_run:
            try:
                schedule_interval = int(input(f"Schedule interval in minutes (default {schedule_interval}): ") or schedule_interval)
                
                print("Weekdays: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday")
                weekdays_input = input("Enter weekdays (e.g., '0,1,2,3,4' for Mon-Fri): ").strip()
                if weekdays_input:
                    schedule_weekdays = [int(d.strip()) for d in weekdays_input.split(',')]
            except ValueError:
                print("❌ Invalid input, using defaults")
        
        # Create the group
        now = datetime.now().isoformat()
        group = SymbolGroup(
            group_id=group_id,
            name=group_name,
            description=description,
            symbols=symbols,
            created_at=now,
            updated_at=now,
            enabled=True,
            tags=["user_created"],
            metadata={
                "periodic_alerts": periodic_alerts,
                "auto_run_enabled": auto_run,
                "schedule_interval": schedule_interval,
                "schedule_weekdays": schedule_weekdays,
                "indicator_settings": self.indicator_settings.to_dict()
            }
        )
        
        # Save the group
        success = self.manager.save_group(group)
        if success:
            print(f"\n✅ Symbol group '{group_name}' created successfully!")
            print(f"   Group ID: {group_id}")
            print(f"   Symbols: {len(symbols)}")
            print(f"   Periodic alerts: {'Yes' if periodic_alerts else 'No'}")
            print(f"   Auto scheduling: {'Yes' if auto_run else 'No'}")
            
            if auto_run:
                self.periodic_runner.schedule_group_analysis(group_id, schedule_interval, schedule_weekdays)
                if not self.periodic_runner.running:
                    print("⚠️  Remember to start the periodic scheduler (option 10)")
        else:
            print("❌ Failed to create symbol group")
        
        input("\nPress Enter to continue...")
    
    def manage_scheduler_settings(self):
        """Manage default scheduler settings."""
        print("\n📅 SCHEDULER SETTINGS")
        print("-" * 40)
        
        print("Current default settings:")
        for key, value in self.scheduler_settings.settings.items():
            print(f"  {key}: {value}")
        
        print("\nOptions:")
        print("1. Toggle auto run enabled")
        print("2. Change default schedule interval")
        print("3. Change default weekdays")
        print("4. Toggle periodic alerts")
        print("5. Back to main menu")
        
        choice = input("Select option (1-5): ").strip()
        
        try:
            if choice == "1":
                current = self.scheduler_settings.settings["auto_run_enabled"]
                self.scheduler_settings.settings["auto_run_enabled"] = not current
                status = "enabled" if not current else "disabled"
                print(f"✅ Auto run {status}")
            
            elif choice == "2":
                current = self.scheduler_settings.settings["schedule_interval"]
                new_interval = int(input(f"Enter new interval in minutes (current: {current}): "))
                self.scheduler_settings.settings["schedule_interval"] = new_interval
                print(f"✅ Default interval set to {new_interval} minutes")
            
            elif choice == "3":
                print("Weekdays: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday")
                current = self.scheduler_settings.settings["schedule_weekdays"]
                weekdays_input = input(f"Enter weekdays (current: {current}): ").strip()
                if weekdays_input:
                    new_weekdays = [int(d.strip()) for d in weekdays_input.split(',')]
                    self.scheduler_settings.settings["schedule_weekdays"] = new_weekdays
                    print(f"✅ Default weekdays set to {new_weekdays}")
            
            elif choice == "4":
                current = self.scheduler_settings.settings["periodic_alerts"]
                self.scheduler_settings.settings["periodic_alerts"] = not current
                status = "enabled" if not current else "disabled"
                print(f"✅ Periodic alerts {status}")
        
        except ValueError:
            print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def manage_indicator_settings(self):
        """Manage global indicator settings with enhanced keyboard navigation."""
        while True:
            print("\n⚙️ INDICATOR SETTINGS")
            print("-" * 50)
            
            print("Current settings:")
            for key, value in self.indicator_settings.settings.items():
                if key == "crossover_indicators":
                    print(f"  {key}:")
                    for indicator, enabled in value.items():
                        status = "🟢 +" if enabled else "🔴 -"
                        print(f"    {status} {indicator}")
                else:
                    print(f"  {key}: {value}")
            
            print("\nOptions:")
            print("1. Change timeframe strategy")
            print("2. Toggle crossover feature") 
            print("3. Modify crossover indicators (Use +/- keys)")
            print("4. Change lookback period")
            print("5. Toggle ADX volatility filter")
            print("6. Change ADX threshold")
            print("7. Toggle oscillator indicators")
            print("8. Change crossover range for symbols")
            print("9. Back to main menu")
            
            choice = KeyboardInput.enhanced_input("Select option (1-9): ").strip()
            
            if choice == 'EXIT' or choice == "9":
                break
            
            try:
                if choice == "1":
                    # Import the strategy registry to get available strategies
                    from strategy import list_available_strategies, get_strategy_info
                    
                    available_strategies = list_available_strategies()
                    print("\nAvailable timeframe strategies:")
                    for i, strategy_name in enumerate(available_strategies, 1):
                        try:
                            info = get_strategy_info(strategy_name)
                            print(f"{i}. {strategy_name} - {info.get('description', 'No description')}")
                        except:
                            print(f"{i}. {strategy_name}")
                    
                    strategy_choice = KeyboardInput.enhanced_input(f"Select strategy (1-{len(available_strategies)}): ", False).strip()
                    if strategy_choice == 'EXIT':
                        continue
                    
                    try:
                        choice_index = int(strategy_choice) - 1
                        if 0 <= choice_index < len(available_strategies):
                            selected_strategy = available_strategies[choice_index]
                            self.indicator_settings.settings["timeframe_strategy"] = selected_strategy
                            print(f"✅ Timeframe strategy set to {selected_strategy}")
                        else:
                            print("❌ Invalid strategy choice")
                    except ValueError:
                        print("❌ Please enter a valid number")
                
                elif choice == "2":
                    current = self.indicator_settings.settings["crossover_enabled"]
                    self.indicator_settings.settings["crossover_enabled"] = not current
                    status = "enabled" if not current else "disabled"
                    print(f"✅ Crossover feature {status}")
                
                elif choice == "3":
                    self._modify_indicator_crossovers_enhanced()
                
                elif choice == "4":
                    current = self.indicator_settings.settings["lookback_period"]
                    new_period_str = KeyboardInput.enhanced_input(f"Enter new lookback period (current: {current}): ", False)
                    if new_period_str == 'EXIT':
                        continue
                    new_period = int(new_period_str)
                    self.indicator_settings.settings["lookback_period"] = new_period
                    print(f"✅ Lookback period set to {new_period}")
                
                elif choice == "5":
                    current = self.indicator_settings.settings["adx_volatility_filter"]
                    self.indicator_settings.settings["adx_volatility_filter"] = not current
                    status = "enabled" if not current else "disabled"
                    print(f"✅ ADX volatility filter {status}")
                
                elif choice == "6":
                    current = self.indicator_settings.settings["adx_threshold"]
                    new_threshold_str = KeyboardInput.enhanced_input(f"Enter new ADX threshold (current: {current}): ", False)
                    if new_threshold_str == 'EXIT':
                        continue
                    new_threshold = float(new_threshold_str)
                    self.indicator_settings.settings["adx_threshold"] = new_threshold
                    print(f"✅ ADX threshold set to {new_threshold}")
                
                elif choice == "7":
                    current = self.indicator_settings.settings["oscillator_indicators_active"]
                    self.indicator_settings.settings["oscillator_indicators_active"] = not current
                    status = "enabled" if not current else "disabled"
                    print(f"✅ Oscillator indicators {status}")
                
                elif choice == "8":
                    self._manage_symbol_crossover_ranges()
            
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            if choice not in ['3', '8']:  # Don't pause for sub-menus
                input("\nPress Enter to continue...")
    
    def _modify_indicator_crossovers_enhanced(self):
        """Enhanced indicator crossover modification with +/- key support."""
        while True:
            print("\n⚡ CROSSOVER INDICATORS CONFIGURATION")
            print("-" * 50)
            print("Use '+' to enable, '-' to disable indicators")
            print("Available indicators:")
            
            indicators = self.indicator_settings.settings["crossover_indicators"]
            for i, (indicator, enabled) in enumerate(indicators.items(), 1):
                status = "🟢 ENABLED" if enabled else "🔴 DISABLED"
                print(f"  {i}. {indicator:<15} - {status}")
            
            print("\nCommands:")
            print("  + <number> : Enable indicator")
            print("  - <number> : Disable indicator")
            print("  back      : Return to settings menu")
            
            command = KeyboardInput.enhanced_input("Enter command: ").strip().lower()
            
            if command == 'EXIT' or command == 'back':
                break
            
            if command.startswith('+') or command.startswith('-'):
                try:
                    action = command[0]
                    number = int(command[1:].strip()) if len(command) > 1 else None
                    
                    if number is None:
                        number_str = KeyboardInput.enhanced_input("Enter indicator number: ", False).strip()
                        if number_str == 'EXIT':
                            continue
                        number = int(number_str)
                    
                    indicator_list = list(indicators.keys())
                    if 1 <= number <= len(indicator_list):
                        indicator_name = indicator_list[number - 1]
                        
                        if action == '+':
                            indicators[indicator_name] = True
                            print(f"✅ {indicator_name} ENABLED")
                        else:  # action == '-'
                            indicators[indicator_name] = False
                            print(f"❌ {indicator_name} DISABLED")
                    else:
                        print(f"❌ Invalid indicator number. Use 1-{len(indicator_list)}")
                        
                except ValueError:
                    print("❌ Invalid command format. Use: +1, -2, etc.")
            
            elif command.isdigit():
                # Direct toggle by number
                number = int(command)
                indicator_list = list(indicators.keys())
                if 1 <= number <= len(indicator_list):
                    indicator_name = indicator_list[number - 1]
                    current_state = indicators[indicator_name]
                    indicators[indicator_name] = not current_state
                    status = "ENABLED" if not current_state else "DISABLED"
                    print(f"🔄 {indicator_name} {status}")
                else:
                    print(f"❌ Invalid indicator number. Use 1-{len(indicator_list)}")
            else:
                print("❌ Invalid command. Use +/- followed by number, or just a number to toggle.")
    
    def _manage_symbol_crossover_ranges(self):
        """Manage crossover ranges for individual symbols."""
        groups = self.manager.list_groups()
        if not groups:
            print("❌ No symbol groups found.")
            return
        
        print("\n📊 SYMBOL CROSSOVER RANGE SETTINGS")
        print("-" * 50)
        
        # Show current settings
        print("Current per-symbol settings:")
        if self.indicator_settings.symbol_crossover_ranges:
            for symbol_key, range_val in self.indicator_settings.symbol_crossover_ranges.items():
                print(f"  {symbol_key}: {range_val} periods")
        else:
            print("  No custom ranges set (using default: 7)")
        
        print(f"\nDefault crossover range: {self.indicator_settings.settings['crossover_range']}")
        
        print("\nOptions:")
        print("1. Set range for specific symbol")
        print("2. Set default range for all new symbols")
        print("3. Clear custom range for symbol")
        print("4. Back")
        
        choice = KeyboardInput.enhanced_input("Select option (1-4): ", False).strip()
        
        if choice == 'EXIT' or choice == "4":
            return
        
        try:
            if choice == "1":
                # List symbols from all groups
                print("\nAvailable symbols:")
                all_symbols = {}
                for group in groups:
                    for symbol_key, config in group.symbols.items():
                        all_symbols[symbol_key] = f"{group.name} - {config.symbol}"
                
                for i, (symbol_key, description) in enumerate(all_symbols.items(), 1):
                    current_range = self.indicator_settings.get_symbol_crossover_range(symbol_key)
                    print(f"  {i}. {symbol_key:<20} ({description}) - Range: {current_range}")
                
                symbol_choice = KeyboardInput.enhanced_input("Enter symbol number: ", False).strip()
                if symbol_choice == 'EXIT':
                    return
                
                symbol_index = int(symbol_choice) - 1
                if 0 <= symbol_index < len(all_symbols):
                    symbol_key = list(all_symbols.keys())[symbol_index]
                    
                    new_range_str = KeyboardInput.enhanced_input(f"Enter new crossover range for {symbol_key}: ", False)
                    if new_range_str == 'EXIT':
                        return
                    
                    new_range = int(new_range_str)
                    self.indicator_settings.set_symbol_crossover_range(symbol_key, new_range)
                    print(f"✅ Crossover range for {symbol_key} set to {new_range}")
                else:
                    print("❌ Invalid symbol number")
            
            elif choice == "2":
                current = self.indicator_settings.settings["crossover_range"]
                new_default_str = KeyboardInput.enhanced_input(f"Enter new default range (current: {current}): ", False)
                if new_default_str == 'EXIT':
                    return
                
                new_default = int(new_default_str)
                self.indicator_settings.settings["crossover_range"] = new_default
                print(f"✅ Default crossover range set to {new_default}")
            
            elif choice == "3":
                if not self.indicator_settings.symbol_crossover_ranges:
                    print("❌ No custom ranges to clear")
                    return
                
                print("\nSymbols with custom ranges:")
                custom_symbols = list(self.indicator_settings.symbol_crossover_ranges.keys())
                for i, symbol_key in enumerate(custom_symbols, 1):
                    range_val = self.indicator_settings.symbol_crossover_ranges[symbol_key]
                    print(f"  {i}. {symbol_key} - {range_val} periods")
                
                symbol_choice = KeyboardInput.enhanced_input("Enter symbol number to clear: ", False).strip()
                if symbol_choice == 'EXIT':
                    return
                
                symbol_index = int(symbol_choice) - 1
                if 0 <= symbol_index < len(custom_symbols):
                    symbol_key = custom_symbols[symbol_index]
                    del self.indicator_settings.symbol_crossover_ranges[symbol_key]
                    print(f"✅ Custom range cleared for {symbol_key}")
                else:
                    print("❌ Invalid symbol number")
        
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
        
        input("\nPress Enter to continue...")
    
    def list_symbol_groups(self):
        """List all available symbol groups."""
        print("\n📋 SYMBOL GROUPS LIST")
        print("-" * 40)
        
        groups = self.manager.list_groups()
        if not groups:
            print("❌ No symbol groups found")
            input("Press Enter to continue...")
            return
        
        for group in groups:
            enabled_symbols = group.get_enabled_symbols()
            status = "🟢" if group.enabled else "🔴"
            auto_run = group.metadata.get("auto_run_enabled", False)
            auto_status = "📅" if auto_run else "⏸️"
            
            print(f"{status} {auto_status} {group.name} ({group.group_id})")
            print(f"    Symbols: {len(enabled_symbols)}/{len(group.symbols)}")
            print(f"    Description: {group.description}")
            print(f"    Created: {group.created_at[:10]}")
            
            if auto_run:
                interval = group.metadata.get("schedule_interval", "N/A")
                weekdays = group.metadata.get("schedule_weekdays", [])
                print(f"    Scheduled: Every {interval}min on {weekdays}")
            
            print()
        
        input("Press Enter to continue...")
    
    def view_periodic_runner_status(self):
        """View the status of the periodic runner."""
        print("\n📊 PERIODIC RUNNER STATUS")
        print("-" * 40)
        
        print(f"Scheduler running: {'Yes' if self.periodic_runner.running else 'No'}")
        print(f"Active jobs: {len(schedule.jobs)}")
        
        if schedule.jobs:
            print("\nScheduled jobs:")
            for job in schedule.jobs:
                print(f"  - {job}")
        
        if self.periodic_runner.last_run_results:
            print(f"\nLast run results:")
            for group_id, result in self.periodic_runner.last_run_results.items():
                timestamp = result.analysis_timestamp[:16]
                print(f"  - {group_id}: {result.group_sentiment} ({timestamp})")
        
        input("\nPress Enter to continue...")
    
    def toggle_periodic_scheduler(self):
        """Start or stop the periodic scheduler."""
        print("\n📅 PERIODIC SCHEDULER CONTROL")
        print("-" * 40)
        
        if self.periodic_runner.running:
            print("Scheduler is currently RUNNING")
            choice = input("Stop scheduler? (y/n): ").strip().lower()
            if choice == 'y':
                self.periodic_runner.stop_scheduler()
        else:
            print("Scheduler is currently STOPPED")
            choice = input("Start scheduler? (y/n): ").strip().lower()
            if choice == 'y':
                # Schedule all auto-run enabled groups
                groups = self.manager.list_groups()
                scheduled_count = 0
                
                for group in groups:
                    if group.enabled and group.metadata.get("auto_run_enabled", False):
                        interval = group.metadata.get("schedule_interval", 15)
                        weekdays = group.metadata.get("schedule_weekdays", [0,1,2,3,4])
                        self.periodic_runner.schedule_group_analysis(group.group_id, interval, weekdays)
                        scheduled_count += 1
                
                if scheduled_count > 0:
                    self.periodic_runner.start_scheduler()
                    print(f"✅ Scheduler started with {scheduled_count} groups")
                else:
                    print("⚠️  No groups with auto-run enabled found")
        
        input("\nPress Enter to continue...")
    
    def manage_periodic_unit_testing(self):
        """Manage periodic unit testing for individual symbols."""
        while True:
            print("\n🧪 PERIODIC UNIT TESTING MANAGEMENT")
            print("-" * 50)
            
            # Show current status
            test_summary = self.unit_tester.get_test_summary()
            print(f"📊 Test Summary:")
            print(f"   Total Tests: {test_summary['total_tests']}")
            print(f"   Successful: {test_summary['successful_tests']}")
            print(f"   Success Rate: {test_summary['success_rate']:.1f}%")
            
            if self.unit_tester.test_schedule:
                print(f"\n⏰ Active Schedules:")
                for test_key, job in self.unit_tester.test_schedule.items():
                    group_id, symbol_key = test_key.split('_', 1)
                    print(f"   {symbol_key} (Group: {group_id})")
            else:
                print("\n⏰ No active unit test schedules")
            
            print("\nOptions:")
            print("1. Schedule unit test for symbol")
            print("2. Remove unit test schedule")
            print("3. Run manual unit test")
            print("4. View test results")
            print("5. Stop all unit tests")
            print("6. Back to main menu")
            
            choice = KeyboardInput.enhanced_input("Select option (1-6): ").strip()
            
            if choice == 'EXIT' or choice == "6":
                break
            
            try:
                if choice == "1":
                    self._schedule_symbol_unit_test()
                elif choice == "2":
                    self._remove_unit_test_schedule()
                elif choice == "3":
                    self._run_manual_unit_test()
                elif choice == "4":
                    self._view_test_results()
                elif choice == "5":
                    self.unit_tester.stop_all_tests()
                    print("✅ All unit tests stopped")
                    input("Press Enter to continue...")
                else:
                    print("❌ Invalid option")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")
    
    def _schedule_symbol_unit_test(self):
        """Schedule a unit test for a specific symbol."""
        groups = self.manager.list_groups()
        if not groups:
            print("❌ No symbol groups found.")
            return
        
        print("\nAvailable groups:")
        for i, group in enumerate(groups, 1):
            symbol_count = len(group.get_enabled_symbols())
            print(f"  {i}. {group.name} ({symbol_count} symbols)")
        
        group_choice = KeyboardInput.enhanced_input("Select group number: ", False).strip()
        if group_choice == 'EXIT':
            return
        
        try:
            group_index = int(group_choice) - 1
            if 0 <= group_index < len(groups):
                selected_group = groups[group_index]
                
                print(f"\nSymbols in {selected_group.name}:")
                enabled_symbols = selected_group.get_enabled_symbols()
                for i, (symbol_key, config) in enumerate(enabled_symbols.items(), 1):
                    print(f"  {i}. {symbol_key} ({config.symbol} - {config.timeframe})")
                
                symbol_choice = KeyboardInput.enhanced_input("Select symbol number: ", False).strip()
                if symbol_choice == 'EXIT':
                    return
                
                symbol_index = int(symbol_choice) - 1
                symbol_keys = list(enabled_symbols.keys())
                if 0 <= symbol_index < len(symbol_keys):
                    selected_symbol = symbol_keys[symbol_index]
                    
                    interval_str = KeyboardInput.enhanced_input("Enter test interval in minutes: ", False).strip()
                    if interval_str == 'EXIT':
                        return
                    
                    interval = int(interval_str)
                    
                    self.unit_tester.schedule_symbol_test(selected_group.group_id, selected_symbol, interval)
                    print(f"✅ Unit test scheduled for {selected_symbol} every {interval} minutes")
                else:
                    print("❌ Invalid symbol number")
            else:
                print("❌ Invalid group number")
                
        except ValueError:
            print("❌ Invalid input")
    
    def _remove_unit_test_schedule(self):
        """Remove a unit test schedule."""
        if not self.unit_tester.test_schedule:
            print("❌ No active unit test schedules")
            return
        
        print("\nActive schedules:")
        schedules = list(self.unit_tester.test_schedule.keys())
        for i, test_key in enumerate(schedules, 1):
            group_id, symbol_key = test_key.split('_', 1)
            print(f"  {i}. {symbol_key} (Group: {group_id})")
        
        choice = KeyboardInput.enhanced_input("Select schedule to remove: ", False).strip()
        if choice == 'EXIT':
            return
        
        try:
            schedule_index = int(choice) - 1
            if 0 <= schedule_index < len(schedules):
                test_key = schedules[schedule_index]
                job = self.unit_tester.test_schedule[test_key]
                schedule.cancel_job(job)
                del self.unit_tester.test_schedule[test_key]
                
                group_id, symbol_key = test_key.split('_', 1)
                print(f"✅ Unit test schedule removed for {symbol_key}")
            else:
                print("❌ Invalid schedule number")
        except ValueError:
            print("❌ Invalid input")
    
    def _run_manual_unit_test(self):
        """Run a manual unit test for a symbol."""
        groups = self.manager.list_groups()
        if not groups:
            print("❌ No symbol groups found.")
            return
        
        print("\nAvailable groups:")
        for i, group in enumerate(groups, 1):
            symbol_count = len(group.get_enabled_symbols())
            print(f"  {i}. {group.name} ({symbol_count} symbols)")
        
        group_choice = KeyboardInput.enhanced_input("Select group number: ", False).strip()
        if group_choice == 'EXIT':
            return
        
        try:
            group_index = int(group_choice) - 1
            if 0 <= group_index < len(groups):
                selected_group = groups[group_index]
                
                print(f"\nSymbols in {selected_group.name}:")
                enabled_symbols = selected_group.get_enabled_symbols()
                for i, (symbol_key, config) in enumerate(enabled_symbols.items(), 1):
                    print(f"  {i}. {symbol_key} ({config.symbol} - {config.timeframe})")
                
                symbol_choice = KeyboardInput.enhanced_input("Select symbol number: ", False).strip()
                if symbol_choice == 'EXIT':
                    return
                
                symbol_index = int(symbol_choice) - 1
                symbol_keys = list(enabled_symbols.keys())
                if 0 <= symbol_index < len(symbol_keys):
                    selected_symbol = symbol_keys[symbol_index]
                    
                    print(f"\n🔍 Running manual unit test for {selected_symbol}...")
                    self.unit_tester.run_symbol_unit_test(selected_group.group_id, selected_symbol)
                else:
                    print("❌ Invalid symbol number")
            else:
                print("❌ Invalid group number")
                
        except ValueError:
            print("❌ Invalid input")
    
    def _view_test_results(self):
        """View unit test results."""
        if not self.unit_tester.test_results:
            print("❌ No test results available")
            return
        
        print("\n📊 UNIT TEST RESULTS")
        print("-" * 50)
        
        for test_key, test_data in self.unit_tester.test_results.items():
            group_id, symbol_key = test_key.split('_', 1)
            result = test_data['result']
            timestamp = test_data['timestamp']
            
            status = "✅" if test_data['success'] else "❌"
            print(f"{status} {symbol_key} (Group: {group_id})")
            print(f"   Timestamp: {timestamp}")
            
            if test_data['success']:
                print(f"   Price: ${result.latest_price:.4f} ({result.price_change_pct:+.1f}%)")
                print(f"   Sentiment: {result.overall_sentiment}")
            else:
                print(f"   Error: {result.error_message}")
            print()
    
    def run(self):
        """Main CLI loop with enhanced keyboard support."""
        print("🚀 Trading Analysis CLI Started" if self._supports_unicode() else "Trading Analysis CLI Started")
        print("💡 Enhanced Features:" if self._supports_unicode() else "Enhanced Features:")
        print("   - Arrow key navigation support")
        print("   - Use +/- keys for enable/disable")
        print("   - Type 'ext' or 'clr' to exit")
        print("   - Ctrl+C for emergency exit")
        
        try:
            while self.running:
                self.display_main_menu()
                
                try:
                    choice = KeyboardInput.enhanced_input("", False).strip()
                    
                    if choice == 'EXIT' or choice == "0":
                        self.running = False
                        print("👋 Shutting down..." if self._supports_unicode() else "Shutting down...")
                        # Stop all periodic processes
                        self.periodic_runner.stop_scheduler()
                        self.unit_tester.stop_all_tests()
                        print("🛑 All periodic processes stopped")
                        print("Goodbye!")
                        break
                    elif choice == "1":
                        self.run_single_symbol_analysis()
                    elif choice == "2":
                        self.run_group_analysis()
                    elif choice == "3":
                        self.run_last_group_analysis()
                    elif choice == "4":
                        self.modify_group_indicator_settings()
                    elif choice == "5":
                        self.create_symbol_group()
                    elif choice == "6":
                        self.manage_scheduler_settings()
                    elif choice == "7":
                        self.manage_indicator_settings()
                    elif choice == "8":
                        self.list_symbol_groups()
                    elif choice == "9":
                        self.view_periodic_runner_status()
                    elif choice == "10":
                        self.toggle_periodic_scheduler()
                    elif choice == "11":
                        self.manage_periodic_unit_testing()
                    elif choice == "12":
                        self.configure_symbol_specific_settings()
                    elif choice == "13":
                        self.configure_periodic_alerts()
                    elif choice == "14":
                        self.manage_periodic_alerts()
                    elif choice == "15":
                        self.view_alerts_history()
                    elif choice == "16":
                        self.configure_symbol_scheduler_settings()
                    elif choice == "17":
                        self.strategy_management_menu()
                    else:
                        print("❌ Invalid option. Please try again.")
                        time.sleep(1)
                
                except KeyboardInterrupt:
                    print("\n🛑 Interrupted by user")
                    break
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n🛑 Emergency exit")
        except KeyboardInterrupt:
            print("\n🛑 Emergency exit")
        finally:
            # Cleanup
            try:
                self.periodic_runner.stop_scheduler()
                self.unit_tester.stop_all_tests()
                self.alerts_engine.stop_monitoring()
            except:
                pass
            print("👋 CLI terminated")

    def _alert_notification_callback(self, alert: AlertEvent) -> None:
        """Callback function for alert notifications."""
        print(f"\n🔔 ALERT: {alert.symbol} - {alert.message}")
        
        # Simple desktop notification (if available)
        try:
            import plyer
            plyer.notification.notify(
                title=f"TradeMaster Alert - {alert.symbol}",
                message=alert.message,
                timeout=10
            )
        except ImportError:
            pass  # Desktop notifications not available

    def configure_symbol_specific_settings(self):
        """Configure symbol-specific indicator settings and periodic alerts."""
        print("\n⚙️ SYMBOL-SPECIFIC CONFIGURATION")
        print("-" * 50)
        
        # Select group
        groups = self.manager.list_groups(enabled_only=True)
        if not groups:
            print("❌ No groups available")
            return
        
        print("Available groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group.name} ({group.group_id}) - {len(group.symbols)} symbols")
        
        try:
            group_choice = int(KeyboardInput.enhanced_input("Select group (number): ", False)) - 1
            if group_choice < 0 or group_choice >= len(groups):
                print("❌ Invalid group selection")
                return
        except (ValueError, IndexError):
            print("❌ Invalid input")
            return
        
        selected_group = groups[group_choice]
        
        # Select symbol
        symbols = list(selected_group.symbols.items())
        if not symbols:
            print("❌ No symbols in group")
            return
        
        print(f"\nSymbols in {selected_group.name}:")
        for i, (symbol_key, symbol_config) in enumerate(symbols, 1):
            status = "✅" if symbol_config.enabled else "❌"
            alerts_status = "🔔" if symbol_config.periodic_alerts and symbol_config.periodic_alerts.enabled else "🔕"
            print(f"  {i}. {status} {alerts_status} {symbol_config.symbol} ({symbol_key})")
        
        try:
            symbol_choice = int(KeyboardInput.enhanced_input("Select symbol (number): ", False)) - 1
            if symbol_choice < 0 or symbol_choice >= len(symbols):
                print("❌ Invalid symbol selection")
                return
        except (ValueError, IndexError):
            print("❌ Invalid input")
            return
        
        symbol_key, symbol_config = symbols[symbol_choice]
        
        # Configuration menu
        while True:
            print(f"\n📊 CONFIGURING: {symbol_config.symbol}")
            print("1. Configure indicator settings")
            print("2. Configure periodic alerts")
            print("3. Configure trading session")
            print("4. Configure risk management")
            print("5. Apply group defaults")
            print("0. Back to main menu")
            
            choice = KeyboardInput.enhanced_input("Select option (0-5): ", False).strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._configure_symbol_indicators(selected_group.group_id, symbol_key, symbol_config)
            elif choice == "2":
                self._configure_symbol_alerts(selected_group.group_id, symbol_key, symbol_config)
            elif choice == "3":
                self._configure_trading_session(selected_group.group_id, symbol_key, symbol_config)
            elif choice == "4":
                self._configure_risk_management(selected_group.group_id, symbol_key, symbol_config)
            elif choice == "5":
                self._apply_group_defaults(selected_group.group_id, symbol_key)
            else:
                print("❌ Invalid option")

    def _configure_symbol_indicators(self, group_id: str, symbol_key: str, symbol_config: SymbolConfig):
        """Configure indicator settings for a specific symbol."""
        print(f"\n📈 INDICATOR SETTINGS: {symbol_config.symbol}")
        
        if not symbol_config.indicator_settings:
            symbol_config.indicator_settings = SGIndicatorSettings()
        
        settings = symbol_config.indicator_settings
        
        while True:
            print("\nCurrent Settings:")
            print(f"  RSI Period: {settings.rsi_period}")
            print(f"  RSI Overbought: {settings.rsi_overbought}")
            print(f"  RSI Oversold: {settings.rsi_oversold}")
            print(f"  MACD Fast: {settings.macd_fast}")
            print(f"  MACD Slow: {settings.macd_slow}")
            print(f"  MACD Signal: {settings.macd_signal}")
            print(f"  Bollinger Bands Period: {settings.bb_period}")
            print(f"  Bollinger Bands Std: {settings.bb_std}")
            print(f"  SMA Periods: {settings.sma_periods}")
            print(f"  EMA Periods: {settings.ema_periods}")
            
            print("\nModify:")
            print("1. RSI settings")
            print("2. MACD settings")
            print("3. Bollinger Bands settings")
            print("4. Moving averages")
            print("5. Save and back")
            print("0. Cancel")
            
            choice = KeyboardInput.enhanced_input("Select option (0-5): ", False).strip()
            
            if choice == "0":
                return
            elif choice == "1":
                try:
                    settings.rsi_period = int(KeyboardInput.enhanced_input(f"RSI Period (current: {settings.rsi_period}): ", False) or settings.rsi_period)
                    settings.rsi_overbought = float(KeyboardInput.enhanced_input(f"RSI Overbought (current: {settings.rsi_overbought}): ", False) or settings.rsi_overbought)
                    settings.rsi_oversold = float(KeyboardInput.enhanced_input(f"RSI Oversold (current: {settings.rsi_oversold}): ", False) or settings.rsi_oversold)
                except ValueError:
                    print("❌ Invalid input")
            elif choice == "2":
                try:
                    settings.macd_fast = int(KeyboardInput.enhanced_input(f"MACD Fast (current: {settings.macd_fast}): ", False) or settings.macd_fast)
                    settings.macd_slow = int(KeyboardInput.enhanced_input(f"MACD Slow (current: {settings.macd_slow}): ", False) or settings.macd_slow)
                    settings.macd_signal = int(KeyboardInput.enhanced_input(f"MACD Signal (current: {settings.macd_signal}): ", False) or settings.macd_signal)
                except ValueError:
                    print("❌ Invalid input")
            elif choice == "3":
                try:
                    settings.bb_period = int(KeyboardInput.enhanced_input(f"BB Period (current: {settings.bb_period}): ", False) or settings.bb_period)
                    settings.bb_std = float(KeyboardInput.enhanced_input(f"BB Std Dev (current: {settings.bb_std}): ", False) or settings.bb_std)
                except ValueError:
                    print("❌ Invalid input")
            elif choice == "4":
                sma_input = KeyboardInput.enhanced_input(f"SMA Periods (comma-separated, current: {','.join(map(str, settings.sma_periods))}): ", False).strip()
                if sma_input:
                    try:
                        settings.sma_periods = [int(x.strip()) for x in sma_input.split(',')]
                    except ValueError:
                        print("❌ Invalid input")
                
                ema_input = KeyboardInput.enhanced_input(f"EMA Periods (comma-separated, current: {','.join(map(str, settings.ema_periods))}): ", False).strip()
                if ema_input:
                    try:
                        settings.ema_periods = [int(x.strip()) for x in ema_input.split(',')]
                    except ValueError:
                        print("❌ Invalid input")
            elif choice == "5":
                if self.manager.configure_symbol_indicators(group_id, symbol_key, settings):
                    print("✅ Indicator settings saved")
                    return
                else:
                    print("❌ Failed to save settings")

    def _configure_symbol_alerts(self, group_id: str, symbol_key: str, symbol_config: SymbolConfig):
        """Configure periodic alerts for a specific symbol."""
        print(f"\n🔔 PERIODIC ALERTS: {symbol_config.symbol}")
        
        if not symbol_config.periodic_alerts:
            symbol_config.periodic_alerts = PeriodicAlertConfig()
        
        alerts = symbol_config.periodic_alerts
        
        while True:
            print(f"\nAlert Status: {'✅ ENABLED' if alerts.enabled else '❌ DISABLED'}")
            print(f"Alert Interval: {alerts.alert_interval} minutes")
            print(f"Alert Weekdays: {alerts.alert_weekdays}")
            print(f"Alert Hours: {alerts.alert_hours}")
            print(f"Alert Count: {alerts.alert_count}")
            if alerts.last_triggered:
                print(f"Last Triggered: {alerts.last_triggered}")
            
            print("\nAlert Conditions:")
            for condition, enabled in alerts.conditions.items():
                status = "✅" if enabled else "❌"
                print(f"  {status} {condition}")
            
            print("\nOptions:")
            print("1. Toggle alert enabled/disabled")
            print("2. Change alert interval")
            print("3. Configure alert conditions")
            print("4. Configure alert schedule")
            print("5. Save and back")
            print("0. Cancel")
            
            choice = KeyboardInput.enhanced_input("Select option (0-5): ", False).strip()
            
            if choice == "0":
                return
            elif choice == "1":
                alerts.enabled = not alerts.enabled
                print(f"✅ Alerts {'enabled' if alerts.enabled else 'disabled'}")
            elif choice == "2":
                try:
                    new_interval = int(KeyboardInput.enhanced_input(f"Alert interval in minutes (current: {alerts.alert_interval}): ", False))
                    if new_interval > 0:
                        alerts.alert_interval = new_interval
                        print(f"✅ Alert interval set to {new_interval} minutes")
                except ValueError:
                    print("❌ Invalid input")
            elif choice == "3":
                self._configure_alert_conditions(alerts)
            elif choice == "4":
                self._configure_alert_schedule(alerts)
            elif choice == "5":
                if self.manager.configure_symbol_periodic_alerts(group_id, symbol_key, alerts):
                    print("✅ Alert settings saved")
                    return
                else:
                    print("❌ Failed to save settings")

    def _configure_alert_conditions(self, alerts: PeriodicAlertConfig):
        """Configure alert conditions."""
        print("\n🎯 ALERT CONDITIONS")
        
        conditions_list = list(alerts.conditions.items())
        
        while True:
            print("\nCurrent Conditions:")
            for i, (condition, enabled) in enumerate(conditions_list, 1):
                status = "✅" if enabled else "❌"
                print(f"  {i}. {status} {condition}")
            
            print("\n0. Done")
            
            choice = KeyboardInput.enhanced_input("Toggle condition (number) or 0 to finish: ", False).strip()
            
            if choice == "0":
                break
            
            try:
                condition_idx = int(choice) - 1
                if 0 <= condition_idx < len(conditions_list):
                    condition_name = conditions_list[condition_idx][0]
                    alerts.conditions[condition_name] = not alerts.conditions[condition_name]
                    status = "enabled" if alerts.conditions[condition_name] else "disabled"
                    print(f"✅ {condition_name} {status}")
            except ValueError:
                print("❌ Invalid input")

    def _configure_alert_schedule(self, alerts: PeriodicAlertConfig):
        """Configure alert schedule."""
        print("\n📅 ALERT SCHEDULE")
        
        print("1. Configure weekdays")
        print("2. Configure hours")
        print("0. Done")
        
        choice = KeyboardInput.enhanced_input("Select option (0-2): ", False).strip()
        
        if choice == "1":
            print("\nWeekdays (0=Monday, 6=Sunday):")
            print(f"Current: {alerts.alert_weekdays}")
            weekdays_input = KeyboardInput.enhanced_input("Enter weekdays (comma-separated, e.g., 0,1,2,3,4): ", False).strip()
            if weekdays_input:
                try:
                    alerts.alert_weekdays = [int(x.strip()) for x in weekdays_input.split(',')]
                    print(f"✅ Weekdays set to {alerts.alert_weekdays}")
                except ValueError:
                    print("❌ Invalid input")
        
        elif choice == "2":
            print(f"\nCurrent hours: {alerts.alert_hours}")
            hours_input = KeyboardInput.enhanced_input("Enter hours (comma-separated, e.g., 9,10,11,12,13,14,15,16): ", False).strip()
            if hours_input:
                try:
                    alerts.alert_hours = [int(x.strip()) for x in hours_input.split(',')]
                    print(f"✅ Hours set to {alerts.alert_hours}")
                except ValueError:
                    print("❌ Invalid input")

    def _configure_trading_session(self, group_id: str, symbol_key: str, symbol_config: SymbolConfig):
        """Configure trading session for a symbol."""
        print(f"\n⏰ TRADING SESSION: {symbol_config.symbol}")
        
        session = symbol_config.trading_session or {}
        
        print(f"Current timezone: {session.get('timezone', 'UTC')}")
        print(f"Market hours: {session.get('market_hours', {}).get('start', '09:00')} - {session.get('market_hours', {}).get('end', '17:00')}")
        print(f"After hours enabled: {session.get('enable_after_hours', False)}")
        
        new_timezone = KeyboardInput.enhanced_input(f"Timezone (current: {session.get('timezone', 'UTC')}): ", False).strip()
        if new_timezone:
            session['timezone'] = new_timezone
        
        start_time = KeyboardInput.enhanced_input(f"Market start time (current: {session.get('market_hours', {}).get('start', '09:00')}): ", False).strip()
        if start_time:
            if 'market_hours' not in session:
                session['market_hours'] = {}
            session['market_hours']['start'] = start_time
        
        end_time = KeyboardInput.enhanced_input(f"Market end time (current: {session.get('market_hours', {}).get('end', '17:00')}): ", False).strip()
        if end_time:
            if 'market_hours' not in session:
                session['market_hours'] = {}
            session['market_hours']['end'] = end_time
        
        symbol_config.trading_session = session
        group = self.manager.get_group(group_id)
        if group:
            self.manager.save_group(group)
            print("✅ Trading session updated")

    def _configure_risk_management(self, group_id: str, symbol_key: str, symbol_config: SymbolConfig):
        """Configure risk management for a symbol."""
        print(f"\n⚠️ RISK MANAGEMENT: {symbol_config.symbol}")
        
        risk = symbol_config.risk_management or {}
        
        print(f"Max position size: {risk.get('max_position_size', 1.0)}")
        print(f"Stop loss %: {risk.get('stop_loss_pct', 2.0)}")
        print(f"Take profit %: {risk.get('take_profit_pct', 6.0)}")
        print(f"Risk/Reward ratio: {risk.get('risk_reward_ratio', 3.0)}")
        
        try:
            max_pos = KeyboardInput.enhanced_input(f"Max position size (current: {risk.get('max_position_size', 1.0)}): ", False).strip()
            if max_pos:
                risk['max_position_size'] = float(max_pos)
            
            stop_loss = KeyboardInput.enhanced_input(f"Stop loss % (current: {risk.get('stop_loss_pct', 2.0)}): ", False).strip()
            if stop_loss:
                risk['stop_loss_pct'] = float(stop_loss)
            
            take_profit = KeyboardInput.enhanced_input(f"Take profit % (current: {risk.get('take_profit_pct', 6.0)}): ", False).strip()
            if take_profit:
                risk['take_profit_pct'] = float(take_profit)
            
            risk_reward = KeyboardInput.enhanced_input(f"Risk/Reward ratio (current: {risk.get('risk_reward_ratio', 3.0)}): ", False).strip()
            if risk_reward:
                risk['risk_reward_ratio'] = float(risk_reward)
            
            symbol_config.risk_management = risk
            group = self.manager.get_group(group_id)
            if group:
                self.manager.save_group(group)
                print("✅ Risk management updated")
        
        except ValueError:
            print("❌ Invalid input")

    def _apply_group_defaults(self, group_id: str, symbol_key: str):
        """Apply group-level defaults to a symbol."""
        if self.manager.apply_group_defaults_to_symbol(group_id, symbol_key, override_existing=True):
            print("✅ Group defaults applied to symbol")
        else:
            print("❌ Failed to apply group defaults")

    def configure_periodic_alerts(self):
        """Configure periodic alerts at the group level."""
        print("\n🔔 PERIODIC ALERTS CONFIGURATION")
        print("-" * 50)
        
        # Select group
        groups = self.manager.list_groups(enabled_only=True)
        if not groups:
            print("❌ No groups available")
            return
        
        print("Available groups:")
        for i, group in enumerate(groups, 1):
            alerts_count = len(group.get_symbols_with_alerts_enabled())
            scheduler_status = "📅" if group.group_settings.scheduler_settings.get("enabled", False) else "📅❌"
            print(f"  {i}. {group.name} - {alerts_count} symbols with alerts {scheduler_status}")
        
        try:
            group_choice = int(KeyboardInput.enhanced_input("Select group (number): ", False)) - 1
            if group_choice < 0 or group_choice >= len(groups):
                print("❌ Invalid group selection")
                return
        except (ValueError, IndexError):
            print("❌ Invalid input")
            return
        
        selected_group = groups[group_choice]
        
        # Group-level configuration
        while True:
            print(f"\n🔔 GROUP ALERTS: {selected_group.name}")
            print(f"Scheduler enabled: {'✅' if selected_group.group_settings.scheduler_settings.get('enabled', False) else '❌'}")
            print(f"Auto analysis: {'✅' if selected_group.group_settings.auto_analysis else '❌'}")
            print(f"Analysis interval: {selected_group.group_settings.analysis_interval} minutes")
            
            symbols_with_alerts = selected_group.get_symbols_with_alerts_enabled()
            print(f"Symbols with alerts: {len(symbols_with_alerts)}")
            
            print("\nOptions:")
            print("1. Enable/disable group scheduler")
            print("2. Configure scheduler settings")
            print("3. Setup first-time alerts for symbols")
            print("4. View symbols with alerts")
            print("0. Back")
            
            choice = KeyboardInput.enhanced_input("Select option (0-4): ", False).strip()
            
            if choice == "0":
                break
            elif choice == "1":
                current_status = selected_group.group_settings.scheduler_settings.get("enabled", False)
                new_status = not current_status
                if self.manager.configure_group_scheduler(selected_group.group_id, new_status):
                    print(f"✅ Group scheduler {'enabled' if new_status else 'disabled'}")
            elif choice == "2":
                self._configure_group_scheduler_settings(selected_group)
            elif choice == "3":
                self._setup_first_time_alerts(selected_group)
            elif choice == "4":
                self._view_symbols_with_alerts(selected_group)

    def _configure_group_scheduler_settings(self, group: SymbolGroup):
        """Configure scheduler settings for a group."""
        settings = group.group_settings.scheduler_settings
        
        print(f"\nCurrent scheduler settings:")
        print(f"  Enabled: {settings.get('enabled', False)}")
        print(f"  Run interval: {settings.get('run_interval', 15)} minutes")
        print(f"  Run weekdays: {settings.get('run_weekdays', [0, 1, 2, 3, 4])}")
        print(f"  Run hours: {settings.get('run_hours', list(range(9, 17)))}")
        
        try:
            interval = KeyboardInput.enhanced_input(f"Run interval in minutes (current: {settings.get('run_interval', 15)}): ", False).strip()
            if interval:
                settings['run_interval'] = int(interval)
            
            weekdays = KeyboardInput.enhanced_input(f"Weekdays (comma-separated, current: {settings.get('run_weekdays', [0, 1, 2, 3, 4])}): ", False).strip()
            if weekdays:
                settings['run_weekdays'] = [int(x.strip()) for x in weekdays.split(',')]
            
            hours = KeyboardInput.enhanced_input(f"Hours (comma-separated, current: {settings.get('run_hours', list(range(9, 17)))}): ", False).strip()
            if hours:
                settings['run_hours'] = [int(x.strip()) for x in hours.split(',')]
            
            if self.manager.save_group(group):
                print("✅ Scheduler settings updated")
        
        except ValueError:
            print("❌ Invalid input")

    def _setup_first_time_alerts(self, group: SymbolGroup):
        """Setup periodic alerts for symbols during first-time configuration."""
        print(f"\n🔔 FIRST-TIME ALERTS SETUP: {group.name}")
        
        symbols_without_alerts = {
            k: v for k, v in group.symbols.items()
            if not v.periodic_alerts or not v.periodic_alerts.enabled
        }
        
        if not symbols_without_alerts:
            print("✅ All symbols already have alerts configured")
            return
        
        print(f"Found {len(symbols_without_alerts)} symbols without alerts:")
        for symbol_key, symbol_config in symbols_without_alerts.items():
            print(f"  - {symbol_config.symbol} ({symbol_key})")
        
        setup_all = KeyboardInput.enhanced_input("Setup alerts for all symbols? (y/n): ", False).strip().lower()
        
        if setup_all == 'y':
            try:
                interval = int(KeyboardInput.enhanced_input("Alert interval in minutes (default: 15): ", False) or "15")
                
                print("Select default alert conditions:")
                conditions = {
                    "rsi_overbought": KeyboardInput.enhanced_input("RSI Overbought alerts? (y/n): ", False).strip().lower() == 'y',
                    "rsi_oversold": KeyboardInput.enhanced_input("RSI Oversold alerts? (y/n): ", False).strip().lower() == 'y',
                    "macd_bullish_crossover": KeyboardInput.enhanced_input("MACD Bullish crossover alerts? (y/n): ", False).strip().lower() == 'y',
                    "macd_bearish_crossover": KeyboardInput.enhanced_input("MACD Bearish crossover alerts? (y/n): ", False).strip().lower() == 'y',
                    "volume_spike": KeyboardInput.enhanced_input("Volume spike alerts? (y/n): ", False).strip().lower() == 'y'
                }
                
                success_count = 0
                for symbol_key in symbols_without_alerts.keys():
                    if self.manager.setup_first_time_alerts(group.group_id, symbol_key, interval, conditions):
                        success_count += 1
                
                print(f"✅ Setup alerts for {success_count}/{len(symbols_without_alerts)} symbols")
            
            except ValueError:
                print("❌ Invalid input")

    def _view_symbols_with_alerts(self, group: SymbolGroup):
        """View symbols that have alerts enabled."""
        symbols_with_alerts = group.get_symbols_with_alerts_enabled()
        
        if not symbols_with_alerts:
            print("❌ No symbols have alerts enabled")
            return
        
        print(f"\n🔔 SYMBOLS WITH ALERTS ({len(symbols_with_alerts)}):")
        for symbol_key, symbol_config in symbols_with_alerts.items():
            alerts = symbol_config.periodic_alerts
            print(f"  📊 {symbol_config.symbol} ({symbol_key})")
            print(f"     Interval: {alerts.alert_interval}min, Count: {alerts.alert_count}")
            if alerts.last_triggered:
                print(f"     Last: {alerts.last_triggered}")

    def manage_periodic_alerts(self):
        """Manage the periodic alerts engine."""
        print("\n🔔 PERIODIC ALERTS MANAGEMENT")
        print("-" * 50)
        
        summary = self.alerts_engine.get_alert_summary()
        
        print(f"Alert monitoring: {'🟢 RUNNING' if summary['monitoring_status'] == 'running' else '🔴 STOPPED'}")
        print(f"Active threads: {summary['active_threads']}")
        print(f"Alerts (24h): {summary['total_alerts_24h']}")
        print(f"Total alerts: {summary['total_alerts_all_time']}")
        
        print("\nOptions:")
        print("1. Start alert monitoring")
        print("2. Stop alert monitoring")
        print("3. View alert summary")
        print("4. Save alert history")
        print("0. Back")
        
        choice = KeyboardInput.enhanced_input("Select option (0-4): ", False).strip()
        
        if choice == "1":
            self.alerts_engine.start_monitoring()
            print("✅ Alert monitoring started")
        elif choice == "2":
            self.alerts_engine.stop_monitoring()
            print("✅ Alert monitoring stopped")
        elif choice == "3":
            self._display_alert_summary()
        elif choice == "4":
            filename = self.alerts_engine.save_alert_history()
            print(f"✅ Alert history saved to {filename}")

    def _display_alert_summary(self):
        """Display detailed alert summary."""
        summary = self.alerts_engine.get_alert_summary()
        
        print("\n📊 ALERT SUMMARY")
        print("-" * 30)
        print(f"Status: {summary['monitoring_status']}")
        print(f"Active threads: {summary['active_threads']}")
        print(f"Alerts (24h): {summary['total_alerts_24h']}")
        print(f"Total alerts: {summary['total_alerts_all_time']}")
        
        if summary['alerts_by_symbol']:
            print("\nAlerts by Symbol:")
            for symbol, count in summary['alerts_by_symbol'].items():
                print(f"  {symbol}: {count}")
        
        if summary['alerts_by_condition']:
            print("\nAlerts by Condition:")
            for condition, count in summary['alerts_by_condition'].items():
                print(f"  {condition}: {count}")
        
        if summary['alerts_by_severity']:
            print("\nAlerts by Severity:")
            for severity, count in summary['alerts_by_severity'].items():
                print(f"  {severity}: {count}")

    def view_alerts_history(self):
        """View recent alerts history."""
        print("\n📜 ALERTS HISTORY")
        print("-" * 50)
        
        hours = KeyboardInput.enhanced_input("Show alerts from last N hours (default: 24): ", False).strip()
        try:
            hours = int(hours) if hours else 24
        except ValueError:
            hours = 24
        
        recent_alerts = self.alerts_engine.get_recent_alerts(hours)
        
        if not recent_alerts:
            print(f"❌ No alerts found in the last {hours} hours")
            return
        
        print(f"📊 Found {len(recent_alerts)} alerts in the last {hours} hours:")
        print()
        
        for alert in recent_alerts[-20:]:  # Show last 20 alerts
            timestamp = alert.timestamp[:19].replace('T', ' ')
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(alert.severity, "📊")
            print(f"{severity_icon} {timestamp} | {alert.symbol} | {alert.condition}")
            print(f"   {alert.message}")
            print()

    def configure_symbol_scheduler_settings(self):
        """Configure scheduler settings for a specific symbol."""
        print("\n" + "="*60)
        print("⏰ CONFIGURE SYMBOL SCHEDULER SETTINGS")
        print("="*60)
        
        # Select group
        groups = self.symbol_manager.list_groups()
        if not groups:
            print("❌ No symbol groups found. Create a group first.")
            return
        
        print("📋 Available groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group.group_id} ({len(group.symbols)} symbols)")
        
        try:
            group_choice = int(input("\nSelect group number: ")) - 1
            if group_choice < 0 or group_choice >= len(groups):
                print("❌ Invalid group selection")
                return
            
            selected_group = groups[group_choice]
            group_id = selected_group.group_id
            group = selected_group
            
            # Select symbol
            symbols = list(group.symbols.keys())
            if not symbols:
                print("❌ No symbols in the selected group")
                return
            
            print(f"\n📊 Symbols in {group_id}:")
            for i, symbol in enumerate(symbols, 1):
                symbol_config = group.symbols[symbol]
                scheduler = symbol_config.symbol_scheduler_settings
                if scheduler and not scheduler.use_group_settings:
                    # Show human-readable format
                    active_days = scheduler.get_active_weekday_names()
                    time_descriptions = scheduler.time_window_descriptions or []
                    status = f"✅ Custom ({', '.join(active_days[:3])}{'...' if len(active_days) > 3 else ''}, {len(time_descriptions)} windows)"
                else:
                    status = "⚙️ Using group settings"
                print(f"  {i}. {symbol} - {status}")
            
            symbol_choice = int(input("\nSelect symbol number: ")) - 1
            if symbol_choice < 0 or symbol_choice >= len(symbols):
                print("❌ Invalid symbol selection")
                return
            
            symbol_key = symbols[symbol_choice]
            current_settings = group.symbols[symbol_key].symbol_scheduler_settings
            
            print(f"\n⏰ Configuring scheduler for {symbol_key}")
            print("="*50)
            
            # Configure scheduler settings
            print("1. Use group-level settings")
            print("2. Configure custom settings")
            
            settings_choice = input("\nChoice (1-2): ").strip()
            
            if settings_choice == "1":
                # Use group settings
                from backend.symbol_groups_manager import SymbolSchedulerSettings
                scheduler_settings = SymbolSchedulerSettings(use_group_settings=True)
                
            elif settings_choice == "2":
                # Configure custom settings
                scheduler_settings = self._configure_custom_scheduler_settings()
                if not scheduler_settings:
                    return
                    
            else:
                print("❌ Invalid choice")
                return
            
            # Save settings
            success = self.symbol_manager.configure_symbol_scheduler_settings(
                group_id, symbol_key, scheduler_settings
            )
            
            if success:
                print(f"✅ Scheduler settings configured for {symbol_key}")
            else:
                print(f"❌ Failed to configure scheduler settings for {symbol_key}")
                
        except (ValueError, IndexError):
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def _configure_custom_scheduler_settings(self):
        """Helper method to configure custom scheduler settings."""
        from backend.symbol_groups_manager import SymbolSchedulerSettings, TimeWindowSlot
        import pytz
        
        print("\n⏰ Custom Scheduler Configuration")
        print("="*40)
        
        # Configure timezone
        print(f"Current timezone: {SymbolSchedulerSettings().timezone}")
        change_tz = input("Change timezone? (y/n): ").lower().strip()
        
        timezone = "UTC"
        if change_tz == "y":
            print("Common timezones:")
            print("  1. UTC")
            print("  2. US/Eastern")
            print("  3. US/Central") 
            print("  4. US/Mountain")
            print("  5. US/Pacific")
            print("  6. Europe/London")
            print("  7. Asia/Tokyo")
            
            tz_choice = input("Select timezone (1-7) or enter custom: ").strip()
            
            timezone_map = {
                "1": "UTC",
                "2": "US/Eastern", 
                "3": "US/Central",
                "4": "US/Mountain",
                "5": "US/Pacific",
                "6": "Europe/London",
                "7": "Asia/Tokyo"
            }
            
            timezone = timezone_map.get(tz_choice, tz_choice)
            
            # Validate timezone
            try:
                pytz.timezone(timezone)
            except:
                print(f"❌ Invalid timezone: {timezone}")
                timezone = "UTC"
        
        # Configure time windows
        time_windows = []
        time_descriptions = []
        print(f"\n⏰ Configure time windows (timezone: {timezone})")
        print("Format examples:")
        print("  • '8 AM - 1 PM' (business hours)")
        print("  • '9:30 AM - 4 PM' (trading hours)")
        print("  • '11 PM - 6 AM' (overnight)")
        
        while True:
            print(f"\nTime Window #{len(time_windows) + 1}")
            time_input = input("Enter time window (e.g., '8 AM - 1 PM') or 'done' to finish: ").strip()
            
            if time_input.lower() == 'done':
                break
            
            try:
                # Parse user-friendly time format
                start_time, end_time = SymbolSchedulerSettings.parse_time_description(time_input)
                
                window = TimeWindowSlot(
                    start_time=start_time,
                    end_time=end_time,
                    active=True
                )
                
                # Generate description for display
                description = SymbolSchedulerSettings._convert_time_to_description(start_time, end_time)
                
                time_windows.append(window)
                time_descriptions.append(description)
                print(f"✅ Added time window: {description}")
                
            except ValueError as e:
                print(f"❌ {str(e)}")
                print("   Try formats like: '8 AM - 1 PM', '9:30 AM - 4:30 PM', '11 PM - 6 AM'")
                continue
            except Exception as e:
                print(f"❌ Invalid time format: {str(e)}")
                continue
        
        if not time_windows:
            print("❌ No time windows configured")
            return None
        
        # Configure weekdays using names
        print("\n📅 Configure active days:")
        print("Select days when the symbol should be active:")
        
        weekday_options = {
            "Monday": False, "Tuesday": False, "Wednesday": False, "Thursday": False,
            "Friday": False, "Saturday": False, "Sunday": False
        }
        
        # Default selection - weekdays
        default_choice = input("Use default weekdays (Mon-Fri)? (y/n): ").lower().strip()
        
        if default_choice == 'y' or default_choice == '':
            weekday_options.update({
                "Monday": True, "Tuesday": True, "Wednesday": True, 
                "Thursday": True, "Friday": True
            })
        else:
            print("\nSelect individual days (type 'y' for yes, 'n' for no, or press Enter to skip):")
            for day in weekday_options.keys():
                choice = input(f"  {day}: ").lower().strip()
                if choice == 'y':
                    weekday_options[day] = True
        
        # Convert to number format for backend
        name_to_number = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        weekdays = [name_to_number[day] for day, active in weekday_options.items() if active]
        
        if not weekdays:
            print("❌ No days selected, using default weekdays")
            weekdays = [0, 1, 2, 3, 4]
            weekday_options.update({
                "Monday": True, "Tuesday": True, "Wednesday": True, 
                "Thursday": True, "Friday": True
            })
        
        active_day_names = [day for day, active in weekday_options.items() if active]
        print(f"✅ Selected days: {', '.join(active_day_names)}")
        
        # Configure priority
        print("\n🎯 Set priority level:")
        print("1. Low")
        print("2. Medium (default)")
        print("3. High")
        
        priority_choice = input("Priority (1-3): ").strip()
        priority_map = {"1": 1, "2": 2, "3": 3}  # Use integers for priority
        priority = priority_map.get(priority_choice, 2)  # Default to medium (2)
        
        # Create scheduler settings
        scheduler_settings = SymbolSchedulerSettings(
            use_group_settings=False,
            time_windows=time_windows,
            active_weekdays=weekdays,
            timezone=timezone,
            priority=priority,
            enabled=True
        )
        
        print(f"\n✅ Custom scheduler settings configured:")
        print(f"   Timezone: {timezone}")
        print(f"   Time windows: {', '.join(scheduler_settings.time_window_descriptions)}")
        print(f"   Active days: {', '.join(active_day_names)}")
        print(f"   Priority: {['Low', 'Medium', 'High'][priority-1]}")
        
        return scheduler_settings

    def strategy_management_menu(self):
        """Strategy management submenu."""
        while True:
            print("\n" + "="*60)
            print("🎯 STRATEGY MANAGEMENT" if self._supports_unicode() else "STRATEGY MANAGEMENT")
            print("="*60)
            
            # Get current active strategy
            current_strategy = self.indicator_settings.settings.get("timeframe_strategy", "default-check-single-timeframe")
            
            # Import strategy functions
            from strategy import list_available_strategies, get_strategy_info, has_configurable_parameters
            
            print(f"📊 Current Active Strategy: {current_strategy}" if self._supports_unicode() else f"Current Active Strategy: {current_strategy}")
            try:
                info = get_strategy_info(current_strategy)
                print(f"   Description: {info.get('description', 'No description')}")
                configurable = has_configurable_parameters(current_strategy)
                print(f"   Configurable Parameters: {'Yes' if configurable else 'No'}")
            except:
                print("   (Unable to load strategy info)")
            
            print(f"\n⚙️  STRATEGY OPTIONS:" if self._supports_unicode() else f"\nSTRATEGY OPTIONS:")
            print("  1. Change Active Strategy")
            print("  2. View Available Strategies")
            print("  3. Configure Current Strategy Parameters")
            print("  4. View Current Strategy Details")
            print("  5. Reset Strategy Parameters to Default")
            print()
            print("  0. Back to main menu")
            print("="*60)
            
            choice = KeyboardInput.enhanced_input("Select option (0-5): ", False).strip()
            if choice == 'EXIT' or choice == '0':
                break
                
            try:
                if choice == "1":
                    self.change_active_strategy()
                elif choice == "2":
                    self.view_available_strategies()
                elif choice == "3":
                    self.configure_strategy_parameters()
                elif choice == "4":
                    self.view_strategy_details()
                elif choice == "5":
                    self.reset_strategy_parameters()
                else:
                    print("❌ Invalid option. Please try again.")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in strategy management: {str(e)}")
                input("Press Enter to continue...")

    def change_active_strategy(self):
        """Change the active strategy."""
        print("\n🔄 CHANGE ACTIVE STRATEGY")
        print("-" * 40)
        
        try:
            from strategy import list_available_strategies, get_strategy_info
            
            available_strategies = list_available_strategies()
            current_strategy = self.indicator_settings.settings.get("timeframe_strategy", "default-check-single-timeframe")
            
            print("Available strategies:")
            for i, strategy_name in enumerate(available_strategies, 1):
                try:
                    info = get_strategy_info(strategy_name)
                    current_marker = " (CURRENT)" if strategy_name == current_strategy else ""
                    print(f"  {i}. {strategy_name}{current_marker}")
                    print(f"     {info.get('description', 'No description')}")
                except:
                    print(f"  {i}. {strategy_name}")
            
            choice = KeyboardInput.enhanced_input(f"\nSelect strategy (1-{len(available_strategies)}) or 0 to cancel: ", False).strip()
            
            if choice == 'EXIT' or choice == '0':
                return
                
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(available_strategies):
                    selected_strategy = available_strategies[choice_index]
                    
                    if selected_strategy == current_strategy:
                        print(f"✅ {selected_strategy} is already the active strategy")
                    else:
                        self.indicator_settings.settings["timeframe_strategy"] = selected_strategy
                        print(f"✅ Active strategy changed to: {selected_strategy}")
                        
                        # Save settings
                        self.save_indicator_settings()
                        
                        # Show info about new strategy
                        try:
                            info = get_strategy_info(selected_strategy)
                            print(f"\nℹ️  Strategy Info:")
                            print(f"   Type: {info.get('type', 'Unknown')}")
                            print(f"   Version: {info.get('version', 'Unknown')}")
                            if 'primary_indicators' in info:
                                print(f"   Primary Indicators: {', '.join(info['primary_indicators'])}")
                        except:
                            pass
                else:
                    print("❌ Invalid strategy choice")
            except ValueError:
                print("❌ Please enter a valid number")
                
        except Exception as e:
            print(f"❌ Error changing strategy: {str(e)}")

    def view_available_strategies(self):
        """View all available strategies with details."""
        print("\n📋 AVAILABLE STRATEGIES")
        print("-" * 50)
        
        try:
            from strategy import list_available_strategies, get_strategy_info, has_configurable_parameters
            
            available_strategies = list_available_strategies()
            current_strategy = self.indicator_settings.settings.get("timeframe_strategy", "default-check-single-timeframe")
            
            for i, strategy_name in enumerate(available_strategies, 1):
                current_marker = " ⭐ CURRENT" if strategy_name == current_strategy else ""
                configurable = has_configurable_parameters(strategy_name)
                config_marker = " 🔧 CONFIGURABLE" if configurable else ""
                
                print(f"\n{i}. {strategy_name}{current_marker}{config_marker}")
                print("-" * 40)
                
                try:
                    info = get_strategy_info(strategy_name)
                    print(f"   Description: {info.get('description', 'No description')}")
                    print(f"   Type: {info.get('type', 'Unknown')}")
                    print(f"   Version: {info.get('version', 'Unknown')}")
                    
                    if 'primary_indicators' in info:
                        print(f"   Primary Indicators: {', '.join(info['primary_indicators'])}")
                    
                    if 'confirmation_indicators' in info:
                        print(f"   Confirmation Indicators: {', '.join(info['confirmation_indicators'])}")
                        
                    if 'signal_generation' in info:
                        print(f"   Signal Logic: {info['signal_generation']}")
                        
                except Exception as e:
                    print(f"   (Error loading info: {str(e)})")
                    
        except Exception as e:
            print(f"❌ Error viewing strategies: {str(e)}")
        
        input("\nPress Enter to continue...")

    def configure_strategy_parameters(self):
        """Configure parameters for the current strategy."""
        print("\n⚙️  CONFIGURE STRATEGY PARAMETERS")
        print("-" * 45)
        
        try:
            from strategy import get_strategy, get_strategy_parameters_template, has_configurable_parameters
            
            current_strategy = self.indicator_settings.settings.get("timeframe_strategy", "default-check-single-timeframe")
            
            if not has_configurable_parameters(current_strategy):
                print(f"❌ Strategy '{current_strategy}' has no configurable parameters.")
                print("   This strategy uses global indicator settings.")
                input("\nPress Enter to continue...")
                return
            
            # Get parameter template
            template = get_strategy_parameters_template(current_strategy)
            strategy_instance = get_strategy(current_strategy)
            current_params = strategy_instance.get_current_parameters()
            
            print(f"Configuring parameters for: {current_strategy}")
            print("\nCurrent parameter values:")
            
            # Group parameters by category
            categories = {}
            for param_key, param_config in template.items():
                category = param_config.get("category", "General")
                if category not in categories:
                    categories[category] = []
                categories[category].append((param_key, param_config))
            
            # Display current values by category
            for category, params in categories.items():
                print(f"\n📊 {category}:")
                for param_key, param_config in params:
                    if param_config.get("type") == "info":
                        continue
                    current_value = current_params.get(param_key, param_config.get("default", "N/A"))
                    print(f"   {param_config['name']}: {current_value}")
                    print(f"      ({param_config.get('description', 'No description')})")
            
            print(f"\n🔧 PARAMETER CONFIGURATION:")
            print("  1. Modify specific parameter")
            print("  2. Reset all to defaults")
            print("  0. Back")
            
            choice = KeyboardInput.enhanced_input("Select option (0-2): ", False).strip()
            
            if choice == 'EXIT' or choice == '0':
                return
            elif choice == "1":
                self.modify_specific_parameter(current_strategy, template, current_params)
            elif choice == "2":
                self.reset_strategy_parameters()
            else:
                print("❌ Invalid option")
                
        except Exception as e:
            print(f"❌ Error configuring parameters: {str(e)}")
            input("Press Enter to continue...")

    def modify_specific_parameter(self, strategy_name, template, current_params):
        """Modify a specific parameter."""
        print("\n🔧 MODIFY PARAMETER")
        print("-" * 25)
        
        # List configurable parameters
        configurable_params = [(k, v) for k, v in template.items() if v.get("type") != "info"]
        
        if not configurable_params:
            print("❌ No configurable parameters found")
            return
        
        print("Select parameter to modify:")
        for i, (param_key, param_config) in enumerate(configurable_params, 1):
            current_value = current_params.get(param_key, param_config.get("default", "N/A"))
            print(f"  {i}. {param_config['name']}: {current_value}")
        
        choice = KeyboardInput.enhanced_input(f"Select parameter (1-{len(configurable_params)}) or 0 to cancel: ", False).strip()
        
        if choice == 'EXIT' or choice == '0':
            return
            
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(configurable_params):
                param_key, param_config = configurable_params[choice_index]
                
                print(f"\nModifying: {param_config['name']}")
                print(f"Description: {param_config.get('description', 'No description')}")
                print(f"Type: {param_config['type']}")
                print(f"Current value: {current_params.get(param_key, param_config.get('default', 'N/A'))}")
                
                if "min" in param_config and "max" in param_config:
                    print(f"Valid range: {param_config['min']} - {param_config['max']}")
                
                new_value = KeyboardInput.enhanced_input(f"Enter new value: ", False).strip()
                
                if new_value == 'EXIT':
                    return
                
                # Validate and convert value
                try:
                    if param_config["type"] == "int":
                        new_value = int(new_value)
                    elif param_config["type"] == "float":
                        new_value = float(new_value)
                    
                    # Validate range
                    if "min" in param_config and new_value < param_config["min"]:
                        print(f"❌ Value too small. Minimum: {param_config['min']}")
                        return
                    if "max" in param_config and new_value > param_config["max"]:
                        print(f"❌ Value too large. Maximum: {param_config['max']}")
                        return
                    
                    # Update parameter
                    from strategy import get_strategy
                    strategy_instance = get_strategy(strategy_name)
                    strategy_instance.update_parameters({param_key: new_value})
                    
                    print(f"✅ Parameter '{param_config['name']}' updated to: {new_value}")
                    
                    # TODO: Save strategy-specific parameters to file or database
                    print("⚠️  Note: Parameter changes are temporary and will reset when CLI restarts.")
                    print("   Strategy-specific parameter persistence will be added in a future update.")
                    
                except ValueError:
                    print(f"❌ Invalid value for {param_config['type']} parameter")
                except Exception as e:
                    print(f"❌ Error updating parameter: {str(e)}")
            else:
                print("❌ Invalid parameter choice")
        except ValueError:
            print("❌ Please enter a valid number")

    def view_strategy_details(self):
        """View detailed information about the current strategy."""
        print("\n📊 STRATEGY DETAILS")
        print("-" * 30)
        
        try:
            from strategy import get_strategy_info, get_strategy_parameters_template, has_configurable_parameters
            
            current_strategy = self.indicator_settings.settings.get("timeframe_strategy", "default-check-single-timeframe")
            
            print(f"Strategy: {current_strategy}")
            
            info = get_strategy_info(current_strategy)
            
            print(f"\n📋 Basic Information:")
            print(f"   Name: {info.get('name', 'Unknown')}")
            print(f"   Description: {info.get('description', 'No description')}")
            print(f"   Type: {info.get('type', 'Unknown')}")
            print(f"   Version: {info.get('version', 'Unknown')}")
            
            if 'primary_indicators' in info:
                print(f"\n🎯 Primary Indicators:")
                for indicator in info['primary_indicators']:
                    print(f"   • {indicator}")
            
            if 'confirmation_indicators' in info:
                print(f"\n✅ Confirmation Indicators:")
                for indicator in info['confirmation_indicators']:
                    print(f"   • {indicator}")
            
            if 'risk_management' in info:
                print(f"\n🛡️ Risk Management:")
                for feature in info['risk_management']:
                    print(f"   • {feature}")
            
            if 'signal_generation' in info:
                print(f"\n📈 Signal Generation Logic:")
                print(f"   {info['signal_generation']}")
            
            # Show parameter information if configurable
            if has_configurable_parameters(current_strategy):
                print(f"\n⚙️  Configurable Parameters:")
                try:
                    template = get_strategy_parameters_template(current_strategy)
                    
                    # Group by category
                    categories = {}
                    for param_key, param_config in template.items():
                        if param_config.get("type") == "info":
                            continue
                        category = param_config.get("category", "General")
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(param_config)
                    
                    for category, params in categories.items():
                        print(f"   📊 {category}:")
                        for param_config in params:
                            print(f"      • {param_config['name']}")
                            print(f"        {param_config.get('description', 'No description')}")
                            print(f"        Default: {param_config.get('default', 'N/A')}")
                            if "min" in param_config and "max" in param_config:
                                print(f"        Range: {param_config['min']} - {param_config['max']}")
                except Exception as e:
                    print(f"   (Error loading parameters: {str(e)})")
            else:
                print(f"\n⚙️  Configuration:")
                print("   This strategy uses global indicator settings")
                print("   No strategy-specific parameters available")
                
        except Exception as e:
            print(f"❌ Error viewing strategy details: {str(e)}")
        
        input("\nPress Enter to continue...")

    def reset_strategy_parameters(self):
        """Reset strategy parameters to default values."""
        print("\n🔄 RESET STRATEGY PARAMETERS")
        print("-" * 35)
        
        try:
            from strategy import get_strategy, has_configurable_parameters
            
            current_strategy = self.indicator_settings.settings.get("timeframe_strategy", "default-check-single-timeframe")
            
            if not has_configurable_parameters(current_strategy):
                print(f"❌ Strategy '{current_strategy}' has no configurable parameters to reset.")
                input("\nPress Enter to continue...")
                return
            
            print(f"This will reset all parameters for '{current_strategy}' to their default values.")
            confirm = KeyboardInput.enhanced_input("Are you sure? (y/N): ", False).strip().lower()
            
            if confirm in ['y', 'yes']:
                strategy_instance = get_strategy(current_strategy)
                strategy_instance.reset_parameters_to_default()
                print("✅ All strategy parameters reset to default values")
                
                # TODO: Save reset parameters to file or database
                print("⚠️  Note: Parameter changes are temporary and will reset when CLI restarts.")
            else:
                print("❌ Reset cancelled")
                
        except Exception as e:
            print(f"❌ Error resetting parameters: {str(e)}")
        
        input("\nPress Enter to continue...")

def main():
    """Entry point for the CLI application."""
    try:
        cli = TradingCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 CLI terminated by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
