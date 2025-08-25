"""
Periodic Alerts Engine for TradeMaster Pro

This module provides a comprehensive periodic alert system that monitors symbols
based on technical indicators and triggers notifications when conditions are met.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import pandas as pd
import logging
from dataclasses import dataclass, asdict

from utility.symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig, PeriodicAlertConfig
from utility.indicators import RSI, ADX, Stochastic_Oscillator
import yfinance as yf

@dataclass
class AlertEvent:
    """Represents an alert event."""
    symbol: str
    group_id: str
    condition: str
    message: str
    timestamp: str
    severity: str  # 'info', 'warning', 'critical'
    indicator_values: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AlertConditionChecker:
    """Checks various technical indicator conditions for alerts."""
    
    def __init__(self):
        self.rsi = RSI()
        self.adx = ADX()
        self.stoch = Stochastic_Oscillator()
    
    def check_rsi_overbought(self, data: pd.DataFrame, threshold: float = 70.0) -> Optional[AlertEvent]:
        """Check if RSI is in overbought territory."""
        rsi_values = self.rsi.calculate(data)
        if len(rsi_values) > 0:
            current_rsi = rsi_values.iloc[-1]
            if current_rsi > threshold:
                return {
                    'condition': 'rsi_overbought',
                    'message': f'RSI overbought: {current_rsi:.2f} > {threshold}',
                    'severity': 'warning',
                    'indicator_values': {'rsi': current_rsi, 'threshold': threshold}
                }
        return None
    
    def check_rsi_oversold(self, data: pd.DataFrame, threshold: float = 30.0) -> Optional[AlertEvent]:
        """Check if RSI is in oversold territory."""
        rsi_values = self.rsi.calculate(data)
        if len(rsi_values) > 0:
            current_rsi = rsi_values.iloc[-1]
            if current_rsi < threshold:
                return {
                    'condition': 'rsi_oversold',
                    'message': f'RSI oversold: {current_rsi:.2f} < {threshold}',
                    'severity': 'warning',
                    'indicator_values': {'rsi': current_rsi, 'threshold': threshold}
                }
        return None
    
    def check_macd_bullish_crossover(self, data: pd.DataFrame) -> Optional[AlertEvent]:
        """Check for MACD bullish crossover."""
        # Simple MACD calculation since we don't have a MACD class
        try:
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            if len(macd) > 1:
                current_macd = macd.iloc[-1]
                current_signal = signal.iloc[-1]
                prev_macd = macd.iloc[-2]
                prev_signal = signal.iloc[-2]
                
                # Check if MACD crossed above signal line
                if prev_macd <= prev_signal and current_macd > current_signal:
                    return {
                        'condition': 'macd_bullish_crossover',
                        'message': f'MACD bullish crossover: MACD({current_macd:.4f}) > Signal({current_signal:.4f})',
                        'severity': 'info',
                        'indicator_values': {
                            'macd': current_macd,
                            'signal': current_signal,
                            'histogram': current_macd - current_signal
                        }
                    }
        except Exception:
            pass
        return None
    
    def check_macd_bearish_crossover(self, data: pd.DataFrame) -> Optional[AlertEvent]:
        """Check for MACD bearish crossover."""
        try:
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            if len(macd) > 1:
                current_macd = macd.iloc[-1]
                current_signal = signal.iloc[-1]
                prev_macd = macd.iloc[-2]
                prev_signal = signal.iloc[-2]
                
                # Check if MACD crossed below signal line
                if prev_macd >= prev_signal and current_macd < current_signal:
                    return {
                        'condition': 'macd_bearish_crossover',
                        'message': f'MACD bearish crossover: MACD({current_macd:.4f}) < Signal({current_signal:.4f})',
                        'severity': 'info',
                        'indicator_values': {
                            'macd': current_macd,
                            'signal': current_signal,
                            'histogram': current_macd - current_signal
                        }
                    }
        except Exception:
            pass
        return None
    
    def check_price_above_sma(self, data: pd.DataFrame, period: int = 20) -> Optional[AlertEvent]:
        """Check if price is above SMA."""
        try:
            sma = data['Close'].rolling(window=period).mean()
            if len(sma) > 0 and len(data) > 0:
                current_price = data['Close'].iloc[-1]
                current_sma = sma.iloc[-1]
                
                if current_price > current_sma:
                    return {
                        'condition': f'price_above_sma{period}',
                        'message': f'Price above SMA{period}: {current_price:.4f} > {current_sma:.4f}',
                        'severity': 'info',
                        'indicator_values': {
                            'price': current_price,
                            f'sma{period}': current_sma,
                            'difference_pct': ((current_price - current_sma) / current_sma) * 100
                        }
                    }
        except Exception:
            pass
        return None
    
    def check_price_below_sma(self, data: pd.DataFrame, period: int = 20) -> Optional[AlertEvent]:
        """Check if price is below SMA."""
        try:
            sma = data['Close'].rolling(window=period).mean()
            if len(sma) > 0 and len(data) > 0:
                current_price = data['Close'].iloc[-1]
                current_sma = sma.iloc[-1]
                
                if current_price < current_sma:
                    return {
                        'condition': f'price_below_sma{period}',
                        'message': f'Price below SMA{period}: {current_price:.4f} < {current_sma:.4f}',
                        'severity': 'warning',
                        'indicator_values': {
                            'price': current_price,
                            f'sma{period}': current_sma,
                            'difference_pct': ((current_price - current_sma) / current_sma) * 100
                        }
                    }
        except Exception:
            pass
        return None
    
    def check_volume_spike(self, data: pd.DataFrame, multiplier: float = 2.0) -> Optional[AlertEvent]:
        """Check for volume spike compared to average volume."""
        try:
            if 'Volume' in data.columns and len(data) > 20:
                current_volume = data['Volume'].iloc[-1]
                avg_volume = data['Volume'].iloc[-20:-1].mean()
                
                if current_volume > avg_volume * multiplier:
                    return {
                        'condition': 'volume_spike',
                        'message': f'Volume spike: {current_volume:,.0f} ({current_volume/avg_volume:.1f}x avg)',
                        'severity': 'info',
                        'indicator_values': {
                            'current_volume': current_volume,
                            'average_volume': avg_volume,
                            'multiplier': current_volume / avg_volume
                        }
                    }
        except Exception:
            pass
        return None

class SimpleDataLoader:
    """Simple data loader for fetching symbol data."""
    
    def fetch_symbol_data(self, symbol: str, asset_type: str, timeframe: str, period: str) -> pd.DataFrame:
        """Fetch data for a symbol."""
        try:
            # Map asset types to yfinance symbols
            if asset_type == 'forex':
                if symbol.upper() in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']:
                    yf_symbol = f"{symbol.upper()}=X"
                else:
                    yf_symbol = f"{symbol.lower()}=X"
            elif asset_type == 'crypto':
                yf_symbol = f"{symbol.upper()}-USD"
            elif asset_type == 'indices':
                # Map common index names
                index_map = {
                    'US30': '^DJI',
                    'US500': '^GSPC', 
                    'NASDAQ': '^IXIC',
                    'DOW30': '^DJI',
                    'SP500': '^GSPC'
                }
                yf_symbol = index_map.get(symbol.upper(), f"^{symbol.upper()}")
            else:  # stocks
                yf_symbol = symbol.upper()
            
            # Map timeframes
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '2h': '2h', '4h': '4h', '1d': '1d'
            }
            yf_interval = interval_map.get(timeframe, '1h')
            
            # Fetch data
            data = yf.download(yf_symbol, period=period, interval=yf_interval, progress=False)
            
            if data.empty:
                return None
            
            # Standardize column names
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

class PeriodicAlertsEngine:
    """Main engine for managing periodic alerts across all symbol groups."""
    
    def __init__(self, groups_manager: SymbolGroupManager, 
                 notification_callback: Callable[[AlertEvent], None] = None):
        self.groups_manager = groups_manager
        self.data_loader = SimpleDataLoader()
        self.condition_checker = AlertConditionChecker()
        self.notification_callback = notification_callback
        
        self.is_running = False
        self.alert_threads: Dict[str, threading.Thread] = {}
        self.alert_history: List[AlertEvent] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('periodic_alerts.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PeriodicAlertsEngine')
    
    def start_monitoring(self) -> None:
        """Start monitoring all groups with alerts enabled."""
        if self.is_running:
            self.logger.warning("Alert monitoring is already running")
            return
        
        self.is_running = True
        groups_with_alerts = self.groups_manager.get_groups_with_alerts()
        
        self.logger.info(f"Starting alert monitoring for {len(groups_with_alerts)} groups")
        
        for group in groups_with_alerts:
            thread = threading.Thread(
                target=self._monitor_group,
                args=(group,),
                daemon=True,
                name=f"AlertThread-{group.group_id}"
            )
            thread.start()
            self.alert_threads[group.group_id] = thread
    
    def stop_monitoring(self) -> None:
        """Stop all alert monitoring."""
        self.is_running = False
        self.logger.info("Stopping alert monitoring...")
        
        # Wait for threads to finish
        for group_id, thread in self.alert_threads.items():
            if thread.is_alive():
                thread.join(timeout=5)
        
        self.alert_threads.clear()
        self.logger.info("Alert monitoring stopped")
    
    def _monitor_group(self, group: SymbolGroup) -> None:
        """Monitor a single group for alert conditions."""
        self.logger.info(f"Starting monitoring for group: {group.name}")
        
        while self.is_running:
            try:
                symbols_with_alerts = group.get_symbols_with_alerts_enabled()
                
                for symbol_key, symbol_config in symbols_with_alerts.items():
                    if not self._should_check_alerts(symbol_config.periodic_alerts):
                        continue
                    
                    alerts = self._check_symbol_alerts(group.group_id, symbol_key, symbol_config)
                    
                    for alert in alerts:
                        self._trigger_alert(alert)
                        # Update last triggered time
                        symbol_config.periodic_alerts.last_triggered = datetime.now().isoformat()
                        symbol_config.periodic_alerts.alert_count += 1
                
                # Sleep for the alert interval (use minimum interval from all symbols)
                intervals = [
                    symbol.periodic_alerts.alert_interval 
                    for symbol in symbols_with_alerts.values()
                    if symbol.periodic_alerts
                ]
                sleep_time = min(intervals) * 60 if intervals else 15 * 60  # minutes to seconds
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error monitoring group {group.group_id}: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _should_check_alerts(self, alert_config: PeriodicAlertConfig) -> bool:
        """Check if alerts should be triggered based on schedule."""
        if not alert_config.enabled:
            return False
        
        now = datetime.now()
        
        # Check weekdays
        if now.weekday() not in alert_config.alert_weekdays:
            return False
        
        # Check hours
        if now.hour not in alert_config.alert_hours:
            return False
        
        # Check if enough time has passed since last alert
        if alert_config.last_triggered:
            last_triggered = datetime.fromisoformat(alert_config.last_triggered)
            time_diff = now - last_triggered
            if time_diff.total_seconds() < alert_config.alert_interval * 60:
                return False
        
        return True
    
    def _check_symbol_alerts(self, group_id: str, symbol_key: str, 
                           symbol_config: SymbolConfig) -> List[AlertEvent]:
        """Check alert conditions for a specific symbol."""
        alerts = []
        
        try:
            # Fetch data
            data = self.data_loader.fetch_symbol_data(
                symbol_config.symbol,
                symbol_config.asset_type,
                symbol_config.timeframe,
                symbol_config.period
            )
            
            if data is None or len(data) == 0:
                self.logger.warning(f"No data available for {symbol_config.symbol}")
                return alerts
            
            conditions = symbol_config.periodic_alerts.conditions
            
            # Check each enabled condition
            if conditions.get('rsi_overbought', False):
                alert = self.condition_checker.check_rsi_overbought(
                    data, symbol_config.indicator_settings.rsi_overbought
                )
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
            if conditions.get('rsi_oversold', False):
                alert = self.condition_checker.check_rsi_oversold(
                    data, symbol_config.indicator_settings.rsi_oversold
                )
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
            if conditions.get('macd_bullish_crossover', False):
                alert = self.condition_checker.check_macd_bullish_crossover(data)
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
            if conditions.get('macd_bearish_crossover', False):
                alert = self.condition_checker.check_macd_bearish_crossover(data)
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
            if conditions.get('price_above_sma20', False):
                alert = self.condition_checker.check_price_above_sma(data, 20)
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
            if conditions.get('price_below_sma20', False):
                alert = self.condition_checker.check_price_below_sma(data, 20)
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
            if conditions.get('volume_spike', False):
                alert = self.condition_checker.check_volume_spike(data)
                if alert:
                    alerts.append(self._create_alert_event(
                        symbol_config.symbol, group_id, alert
                    ))
            
        except Exception as e:
            self.logger.error(f"Error checking alerts for {symbol_config.symbol}: {str(e)}")
        
        return alerts
    
    def _create_alert_event(self, symbol: str, group_id: str, alert_data: Dict[str, Any]) -> AlertEvent:
        """Create an AlertEvent from alert data."""
        return AlertEvent(
            symbol=symbol,
            group_id=group_id,
            condition=alert_data['condition'],
            message=alert_data['message'],
            timestamp=datetime.now().isoformat(),
            severity=alert_data['severity'],
            indicator_values=alert_data['indicator_values']
        )
    
    def _trigger_alert(self, alert: AlertEvent) -> None:
        """Trigger an alert notification."""
        self.alert_history.append(alert)
        
        # Log the alert
        log_message = f"ALERT [{alert.severity.upper()}] {alert.symbol}: {alert.message}"
        if alert.severity == 'critical':
            self.logger.critical(log_message)
        elif alert.severity == 'warning':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Call notification callback if provided
        if self.notification_callback:
            try:
                self.notification_callback(alert)
            except Exception as e:
                self.logger.error(f"Error in notification callback: {str(e)}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[AlertEvent]:
        """Get alerts from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert.timestamp) > cutoff_time
        ]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get a summary of alert activity."""
        recent_alerts = self.get_recent_alerts(24)
        
        symbol_counts = {}
        condition_counts = {}
        severity_counts = {}
        
        for alert in recent_alerts:
            symbol_counts[alert.symbol] = symbol_counts.get(alert.symbol, 0) + 1
            condition_counts[alert.condition] = condition_counts.get(alert.condition, 0) + 1
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        
        return {
            'total_alerts_24h': len(recent_alerts),
            'total_alerts_all_time': len(self.alert_history),
            'alerts_by_symbol': symbol_counts,
            'alerts_by_condition': condition_counts,
            'alerts_by_severity': severity_counts,
            'monitoring_status': 'running' if self.is_running else 'stopped',
            'active_threads': len([t for t in self.alert_threads.values() if t.is_alive()])
        }
    
    def save_alert_history(self, filename: str = None) -> str:
        """Save alert history to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alert_history_{timestamp}.json"
        
        alert_data = [alert.to_dict() for alert in self.alert_history]
        
        with open(filename, 'w') as f:
            json.dump({
                'alerts': alert_data,
                'generated_at': datetime.now().isoformat(),
                'total_alerts': len(alert_data)
            }, f, indent=2)
        
        return filename

# Example notification callback function
def desktop_notification_callback(alert: AlertEvent) -> None:
    """Example callback for desktop notifications."""
    try:
        import plyer
        plyer.notification.notify(
            title=f"TradeMaster Alert - {alert.symbol}",
            message=alert.message,
            timeout=10
        )
    except ImportError:
        # Fallback to console notification if plyer is not available
        print(f"🔔 DESKTOP NOTIFICATION: {alert.symbol} - {alert.message}")
    except Exception as e:
        print(f"🔔 NOTIFICATION ERROR: {alert.symbol} - {alert.message} (Error: {e})")

# Example usage
if __name__ == "__main__":
    # Initialize the system
    groups_manager = SymbolGroupManager()
    alerts_engine = PeriodicAlertsEngine(groups_manager, desktop_notification_callback)
    
    # Start monitoring
    print("Starting periodic alerts monitoring...")
    alerts_engine.start_monitoring()
    
    try:
        # Keep running
        while True:
            time.sleep(60)
            summary = alerts_engine.get_alert_summary()
            print(f"Alert summary: {summary['total_alerts_24h']} alerts in last 24h")
    except KeyboardInterrupt:
        print("\nStopping alerts monitoring...")
        alerts_engine.stop_monitoring()
