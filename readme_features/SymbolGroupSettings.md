# Symbol Group Settings - TradeMaster Pro CLI

## 🎯 Overview
Symbol Group Settings provide comprehensive configuration management for both individual symbols within groups and group-wide settings. This system allows fine-tuned control over analysis parameters, indicator configurations, scheduling settings, and alert preferences at multiple levels.

## 🎛️ Multi-Level Settings Architecture

### 📊 Settings Hierarchy
```python
# Settings inheritance: Symbol-level → Group-level → Global defaults

SETTINGS_HIERARCHY = {
    'global_defaults': {
        'priority': 1,
        'description': 'System-wide default settings'
    },
    'group_level': {
        'priority': 2, 
        'description': 'Settings applied to entire group'
    },
    'symbol_level': {
        'priority': 3,
        'description': 'Individual symbol overrides (highest priority)'
    }
}
```

### 🏗️ Settings Manager Class
```python
class SymbolGroupSettingsManager:
    """
    Comprehensive settings management for symbol groups and individual symbols
    """
    
    def __init__(self, storage_path="symbol_groups/settings.json"):
        self.storage_path = storage_path
        self.group_settings = {}
        self.symbol_settings = {}
        self.global_defaults = self.load_global_defaults()
        
    def get_effective_settings(self, group_id, symbol_key=None):
        """
        Get effective settings with proper inheritance hierarchy
        Priority: Symbol > Group > Global
        """
        
    def update_group_settings(self, group_id, settings_update):
        """Update settings for entire group"""
        
    def update_symbol_settings(self, group_id, symbol_key, settings_update):
        """Update settings for individual symbol"""
        
    def reset_to_defaults(self, group_id, symbol_key=None):
        """Reset settings to defaults (group or symbol level)"""
```

## ⚙️ Group-Level Settings

### 📊 Group Analysis Configuration
```python
class GroupAnalysisSettings:
    """
    Analysis configuration applied to the entire group
    """
    
    def __init__(self, group_id):
        self.group_id = group_id
        self.settings = {
            'analysis_frequency': {
                'enabled': True,
                'interval_minutes': 15,
                'auto_start': True,
                'trading_hours_only': False
            },
            'correlation_analysis': {
                'enabled': True,
                'correlation_threshold': 0.8,
                'alert_on_high_correlation': True,
                'lookback_period_days': 30
            },
            'group_sentiment': {
                'aggregation_method': 'weighted_average',
                'minimum_symbols_required': 3,
                'confidence_threshold': 0.6
            },
            'risk_management': {
                'max_group_risk': 0.05,
                'diversification_threshold': 0.7,
                'position_sizing_method': 'equal_weight'
            }
        }
    
    def update_analysis_frequency(self, interval_minutes):
        """Update how frequently group analysis runs"""
        
    def configure_correlation_monitoring(self, threshold, alert_enabled):
        """Configure correlation monitoring settings"""
        
    def set_risk_parameters(self, max_risk, diversification_threshold):
        """Set group-level risk management parameters"""
```

### 🎯 Group Indicator Configuration
```python
class GroupIndicatorSettings:
    """
    Indicator settings applied across all symbols in the group
    """
    
    def __init__(self, group_id):
        self.group_id = group_id
        self.indicator_config = {
            'trend_indicators': {
                'ADX': {
                    'enabled': True,
                    'period': 14,
                    'threshold': 18,
                    'di_threshold': 25
                },
                'MACD': {
                    'enabled': True,
                    'fast_period': 12,
                    'slow_period': 26,
                    'signal_period': 9
                },
                'Moving_Averages': {
                    'enabled': True,
                    'periods': [10, 20, 50, 200],
                    'types': ['SMA', 'EMA']
                }
            },
            'momentum_oscillators': {
                'RSI': {
                    'enabled': True,
                    'period': 14,
                    'overbought': 70,
                    'oversold': 30
                },
                'Stochastic': {
                    'enabled': True,
                    'k_period': 14,
                    'd_period': 3,
                    'overbought': 80,
                    'oversold': 20
                }
            },
            'volatility_indicators': {
                'Bollinger_Bands': {
                    'enabled': True,
                    'period': 20,
                    'std_dev': 2.0
                },
                'ATR': {
                    'enabled': True,
                    'period': 14,
                    'multiplier': 2.0
                }
            }
        }
    
    def apply_asset_optimized_settings(self, asset_type):
        """Apply optimized settings based on primary asset type of group"""
        
    def enable_all_indicators(self):
        """Enable all available indicators for the group"""
        
    def create_minimal_indicator_set(self):
        """Configure minimal set for fast analysis"""
```

### 📅 Group Scheduling Settings
```python
class GroupSchedulingSettings:
    """
    Scheduling configuration for automated group operations
    """
    
    def __init__(self, group_id):
        self.group_id = group_id
        self.schedule_config = {
            'automated_analysis': {
                'enabled': True,
                'schedule_type': 'interval',  # 'interval', 'cron', 'market_hours'
                'interval_minutes': 15,
                'start_time': '09:00',
                'end_time': '17:00',
                'timezone': 'UTC',
                'weekdays_only': True
            },
            'data_refresh': {
                'enabled': True,
                'interval_minutes': 5,
                'force_refresh_hours': [9, 12, 15, 18]
            },
            'report_generation': {
                'enabled': True,
                'daily_summary_time': '18:00',
                'weekly_report_day': 'friday',
                'monthly_report_day': 1
            },
            'alert_checking': {
                'enabled': True,
                'check_interval_seconds': 60,
                'max_alerts_per_hour': 10
            }
        }
    
    def set_market_hours_schedule(self, market='forex'):
        """Configure schedule based on market trading hours"""
        
    def set_custom_interval(self, interval_minutes, start_time=None, end_time=None):
        """Set custom analysis interval"""
        
    def configure_business_hours_only(self, enabled=True):
        """Enable/disable analysis during business hours only"""
```

## 🎯 Symbol-Level Settings

### 📊 Individual Symbol Configuration
```python
class SymbolSettings:
    """
    Settings for individual symbols within a group
    """
    
    def __init__(self, group_id, symbol_key):
        self.group_id = group_id
        self.symbol_key = symbol_key
        self.symbol_config = {
            'data_settings': {
                'timeframe': '1h',
                'period': '7d',
                'data_source': 'yfinance',
                'data_quality_threshold': 0.95
            },
            'analysis_settings': {
                'enabled': True,
                'priority': 'normal',  # 'high', 'normal', 'low'
                'include_in_group_analysis': True,
                'weight_in_group': 1.0
            },
            'alert_settings': {
                'sentiment_alerts': True,
                'price_alerts': True,
                'technical_alerts': True,
                'risk_alerts': True
            },
            'performance_tracking': {
                'track_signals': True,
                'track_accuracy': True,
                'benchmark_comparison': True
            }
        }
    
    def update_timeframe(self, new_timeframe):
        """Update analysis timeframe for this symbol"""
        
    def set_symbol_priority(self, priority_level):
        """Set analysis priority for this symbol"""
        
    def configure_symbol_alerts(self, alert_types):
        """Configure which alerts are enabled for this symbol"""
```

### 🎛️ Symbol-Specific Indicator Overrides
```python
class SymbolIndicatorOverrides:
    """
    Symbol-specific indicator configuration overrides
    """
    
    def __init__(self, group_id, symbol_key):
        self.group_id = group_id
        self.symbol_key = symbol_key
        self.overrides = {}
    
    def override_rsi_settings(self, period=None, overbought=None, oversold=None):
        """Override RSI settings for this specific symbol"""
        if any([period, overbought, oversold]):
            self.overrides['RSI'] = {
                'period': period or 14,
                'overbought': overbought or 70,
                'oversold': oversold or 30,
                'custom_override': True
            }
    
    def override_macd_settings(self, fast=None, slow=None, signal=None):
        """Override MACD settings for this specific symbol"""
        
    def apply_volatility_adjusted_settings(self, volatility_level):
        """
        Apply volatility-adjusted settings
        - High volatility: Longer periods, wider bands
        - Low volatility: Shorter periods, tighter bands
        """
        
    def apply_asset_specific_optimization(self):
        """Apply optimizations based on specific asset characteristics"""
        asset_type = self.get_symbol_asset_type()
        symbol = self.get_symbol_name()
        
        # Apply symbol-specific optimizations
        if symbol == 'EURUSD':
            self.apply_eurusd_optimizations()
        elif symbol == 'BTCUSD':
            self.apply_bitcoin_optimizations()
        elif symbol in ['AAPL', 'GOOGL', 'MSFT']:
            self.apply_tech_stock_optimizations()
```

## 📅 Scheduler Settings

### ⏰ Comprehensive Scheduling System
```python
class AdvancedScheduler:
    """
    Advanced scheduling system for symbol groups and individual symbols
    """
    
    def __init__(self):
        self.active_schedules = {}
        self.schedule_history = {}
        
    def create_symbol_schedule(self, group_id, symbol_key, schedule_config):
        """
        Create custom schedule for individual symbol
        
        Schedule Types:
        - Fixed interval (every X minutes)
        - Market hours based
        - Event-driven (on price change, volume spike)
        - Cron-style scheduling
        """
        
    def create_group_schedule(self, group_id, schedule_config):
        """Create schedule for entire group analysis"""
        
    def setup_market_hours_schedule(self, group_id, market_config):
        """
        Setup schedule based on market trading hours
        
        Supported Markets:
        - Forex: 24/5 with session-based analysis
        - NYSE: 9:30 AM - 4:00 PM EST
        - NASDAQ: 9:30 AM - 4:00 PM EST  
        - Crypto: 24/7 continuous
        - LSE: 8:00 AM - 4:30 PM GMT
        """
        
    def setup_volatility_based_schedule(self, group_id, volatility_thresholds):
        """Adjust analysis frequency based on market volatility"""
```

### 🎯 Periodic Alert Configuration
```python
class PeriodicAlertSettings:
    """
    Configuration for periodic alerts on symbols in groups
    """
    
    def __init__(self, group_id):
        self.group_id = group_id
        self.alert_config = {
            'sentiment_change_alerts': {
                'enabled': True,
                'check_interval_minutes': 15,
                'minimum_change_threshold': 0.1,
                'alert_methods': ['console', 'log_file']
            },
            'atr_band_alerts': {
                'enabled': True,
                'check_interval_minutes': 15,
                'upper_band_breach': True,
                'lower_band_breach': True,
                'trailing_stop_alerts': True
            },
            'trade_validity_alerts': {
                'enabled': True,
                'check_interval_minutes': 30,
                'alert_on_invalidation': True,
                'confidence_threshold': 0.6
            },
            'performance_alerts': {
                'enabled': True,
                'daily_summary': True,
                'weekly_summary': True,
                'significant_moves_threshold': 0.02
            }
        }
    
    def enable_sentiment_alerts(self, symbols, interval_minutes=15):
        """Enable periodic sentiment change alerts for specific symbols"""
        
    def enable_atr_trailing_alerts(self, symbols, interval_minutes=15):
        """Enable ATR-based trailing stop alerts"""
        
    def configure_trade_validation_alerts(self, symbols, validation_rules):
        """Configure alerts for trade validity checking"""
```

## 🚨 First-Time Setup: Periodic Alert Selection

### 🎯 Initial Symbol Alert Configuration
```python
class FirstTimeAlertSetup:
    """
    Interactive setup for selecting symbols for periodic alerts
    """
    
    def __init__(self, group_id):
        self.group_id = group_id
        self.selected_symbols = {}
        
    def run_first_time_setup(self):
        """
        Interactive wizard for first-time alert setup
        """
        print("🚨 PERIODIC ALERT SETUP WIZARD")
        print("=" * 50)
        print("Select symbols for periodic monitoring and alerts...")
        
        # Display all symbols in group
        group_symbols = self.get_group_symbols()
        
        # Allow user to select symbols for alerts
        selected = self.interactive_symbol_selection(group_symbols)
        
        # Configure alert intervals for each selected symbol
        for symbol_key in selected:
            self.configure_symbol_alerts(symbol_key)
        
        # Save configuration
        self.save_alert_configuration()
        
        print("✅ Alert setup completed!")
        
    def interactive_symbol_selection(self, symbols):
        """Interactive symbol selection with checkboxes"""
        print("\n📊 Available symbols in group:")
        print("-" * 30)
        
        selected_symbols = []
        for i, (symbol_key, config) in enumerate(symbols.items(), 1):
            symbol_name = config.symbol
            timeframe = config.timeframe
            asset_type = config.asset_type
            
            print(f"{i}. {symbol_name} ({asset_type}) - {timeframe}")
            
            # Get user selection
            choice = input(f"Enable alerts for {symbol_name}? (y/n): ").lower()
            if choice in ['y', 'yes']:
                selected_symbols.append(symbol_key)
                
        return selected_symbols
    
    def configure_symbol_alerts(self, symbol_key):
        """Configure specific alert settings for selected symbol"""
        symbol_config = self.get_symbol_config(symbol_key)
        
        print(f"\n⚙️ Configuring alerts for {symbol_config.symbol}")
        print("-" * 40)
        
        # Configure alert interval based on timeframe
        timeframe = symbol_config.timeframe
        suggested_interval = self.suggest_alert_interval(timeframe)
        
        print(f"Suggested alert interval: {suggested_interval} minutes")
        custom_interval = input(f"Use suggested interval? (y/n): ").lower()
        
        if custom_interval in ['n', 'no']:
            interval = int(input("Enter custom interval (minutes): "))
        else:
            interval = suggested_interval
            
        # Configure alert types
        alert_types = self.select_alert_types()
        
        # Save symbol alert configuration
        self.selected_symbols[symbol_key] = {
            'interval_minutes': interval,
            'alert_types': alert_types,
            'enabled': True
        }
    
    def suggest_alert_interval(self, timeframe):
        """Suggest appropriate alert interval based on symbol timeframe"""
        interval_mapping = {
            '1m': 5,     # Alert every 5 minutes for 1-min charts
            '5m': 15,    # Alert every 15 minutes for 5-min charts  
            '15m': 15,   # Alert every 15 minutes for 15-min charts
            '30m': 30,   # Alert every 30 minutes for 30-min charts
            '1h': 60,    # Alert every hour for 1-hour charts
            '4h': 240,   # Alert every 4 hours for 4-hour charts
            '1d': 1440   # Alert daily for daily charts
        }
        return interval_mapping.get(timeframe, 60)  # Default to 1 hour
    
    def select_alert_types(self):
        """Interactive selection of alert types"""
        available_alerts = {
            'sentiment_change': 'Sentiment change alerts',
            'atr_bands': 'ATR upper/lower band alerts',
            'trailing_stop': 'Trailing stop loss alerts',
            'trade_validity': 'Trade validity status alerts',
            'technical_signals': 'New technical signals',
            'price_targets': 'Price target alerts'
        }
        
        selected_alerts = []
        print("\n📢 Available alert types:")
        for key, description in available_alerts.items():
            choice = input(f"Enable {description}? (y/n): ").lower()
            if choice in ['y', 'yes']:
                selected_alerts.append(key)
                
        return selected_alerts
```

## ⏰ Periodic Alert System

### 🔄 Active Symbol Monitoring
```python
class ActiveSymbolMonitor:
    """
    Monitor symbols with active trades for periodic alerts
    """
    
    def __init__(self):
        self.active_symbols = {}
        self.alert_history = {}
        self.monitoring_threads = {}
        
    def activate_symbol_monitoring(self, group_id, symbol_key, trade_info):
        """
        Activate monitoring for symbol with active trade
        
        Args:
            trade_info: {
                'entry_price': float,
                'direction': 'long'/'short',
                'stop_loss': float,
                'take_profit': float,
                'entry_time': datetime,
                'position_size': float
            }
        """
        
    def start_periodic_alerts(self, symbol_key, alert_interval_minutes):
        """Start periodic alerting for specific symbol"""
        
    def check_sentiment_changes(self, symbol_key):
        """
        Check for sentiment changes and generate alerts
        
        Alerts when:
        - Overall sentiment changes (BULLISH → BEARISH)
        - Confidence score changes significantly
        - New trading signals appear
        """
        
    def check_atr_band_updates(self, symbol_key):
        """
        Check ATR band updates for trailing stop management
        
        Provides:
        - New ATR upper band value
        - New ATR lower band value
        - Recommended trailing stop adjustment
        - Current price relative to bands
        """
        
    def check_trade_validity(self, symbol_key, original_analysis):
        """
        Check if original trade sentiment is still valid
        
        Alerts when:
        - Original bullish sentiment becomes bearish
        - Confidence drops below threshold
        - Stop loss levels need adjustment
        """
```

### 📊 Alert Content Generation
```python
class PeriodicAlertGenerator:
    """
    Generate comprehensive periodic alerts for active symbols
    """
    
    def generate_sentiment_alert(self, symbol_key, current_analysis, previous_analysis):
        """
        Generate sentiment change alert
        
        Alert Format:
        🚨 SENTIMENT ALERT - EURUSD (15m)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Previous: BULLISH (Confidence: 72%)
        Current:  BEARISH (Confidence: 68%)
        Change:   BULLISH → BEARISH ⚠️
        
        Key Changes:
        • RSI: 45.2 → 38.5 (entered oversold)
        • MACD: 0.0008 → -0.0012 (bearish crossover)
        • ADX: 22.5 → 26.8 (trend strengthening)
        
        Recommendation: Consider position review
        """
        
    def generate_atr_bands_alert(self, symbol_key, atr_analysis):
        """
        Generate ATR bands update alert
        
        Alert Format:
        📊 ATR BANDS UPDATE - GBPUSD (1h)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Current Price: 1.2634
        ATR Value: 0.0089 (24-hour period)
        
        📈 Upper Band: 1.2723 (+0.89%)
        📉 Lower Band: 1.2545 (-0.89%)
        
        🎯 Trailing Stop Suggestions:
        Long Position: 1.2556 (78 pips below)
        Short Position: 1.2712 (78 pips above)
        
        Band Position: Middle range (neutral)
        """
        
    def generate_trade_validity_alert(self, symbol_key, trade_info, current_analysis):
        """
        Generate trade validity status alert
        
        Alert Format:
        ⚖️ TRADE VALIDITY CHECK - AAPL (30m)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Original Trade: LONG @ $145.50 (2h ago)
        Current Price: $147.20 (+1.17%)
        
        ✅ Trade Status: VALID
        Original Sentiment: BULLISH (75% confidence)
        Current Sentiment: BULLISH (71% confidence)
        
        Performance:
        • Unrealized P&L: +$1.70 per share
        • Stop Loss: $143.20 (-89 pips)
        • Take Profit: $149.80 (+275 pips)
        
        Recommendation: Hold position
        """
```

## 🎛️ CLI Settings Interface

### 💻 Interactive Settings Management
```bash
# Settings management through CLI
python trading_cli.py

# Settings Menu Structure:
# 📊 Symbol Group Settings
# ├── 1. 🏢 Group-Level Settings
# │   ├── Analysis Configuration
# │   ├── Indicator Settings  
# │   ├── Scheduling Settings
# │   └── Alert Configuration
# ├── 2. 🎯 Symbol-Level Settings
# │   ├── Individual Symbol Config
# │   ├── Indicator Overrides
# │   ├── Alert Preferences
# │   └── Performance Tracking
# ├── 3. ⏰ Periodic Alert Setup
# │   ├── First-Time Setup Wizard
# │   ├── Active Symbol Selection
# │   ├── Alert Interval Config
# │   └── Alert Type Selection
# └── 4. 📊 Settings Import/Export
```

### 🎯 CLI Settings Operations
```python
class CLISettingsManager:
    """
    Command-line interface for settings management
    """
    
    def cli_group_settings_menu(self, group_id):
        """Interactive group settings configuration"""
        
    def cli_symbol_settings_menu(self, group_id, symbol_key):
        """Interactive symbol settings configuration"""
        
    def cli_periodic_alert_wizard(self, group_id):
        """Wizard for setting up periodic alerts"""
        
    def cli_settings_import_export(self):
        """Import/export settings configurations"""
        
    def cli_settings_reset_wizard(self):
        """Interactive settings reset with confirmations"""
```

## 💾 Settings Storage & Management

### 🗄️ Settings Persistence
```python
class SettingsStorage:
    """
    Handle storage and retrieval of all settings
    """
    
    def __init__(self, storage_path="symbol_groups/"):
        self.group_settings_path = f"{storage_path}group_settings.json"
        self.symbol_settings_path = f"{storage_path}symbol_settings.json"
        self.alert_config_path = f"{storage_path}alert_configurations.json"
        
    def save_group_settings(self, group_id, settings):
        """Save group-level settings"""
        
    def save_symbol_settings(self, group_id, symbol_key, settings):
        """Save symbol-level settings"""
        
    def save_alert_configuration(self, group_id, alert_config):
        """Save periodic alert configuration"""
        
    def backup_all_settings(self, backup_path):
        """Create backup of all settings"""
        
    def restore_settings_from_backup(self, backup_path):
        """Restore settings from backup"""
```

### 🔄 Settings Validation
```python
class SettingsValidator:
    """
    Validate settings configurations
    """
    
    def validate_group_settings(self, settings):
        """Validate group-level settings"""
        
    def validate_symbol_settings(self, settings, symbol_config):
        """Validate symbol-level settings"""
        
    def validate_alert_configuration(self, alert_config):
        """Validate alert configuration"""
        
    def check_settings_conflicts(self, group_settings, symbol_settings):
        """Check for conflicts between group and symbol settings"""
```

Symbol Group Settings provide comprehensive control over every aspect of analysis and monitoring, enabling precise customization for different trading strategies and market conditions while maintaining the flexibility to adapt to changing requirements.
