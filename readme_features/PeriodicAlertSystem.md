# Periodic Alert System - TradeMaster Pro CLI

## 🚨 Overview
The Periodic Alert System is TradeMaster Pro's real-time monitoring engine that provides continuous surveillance of active trades and symbols. It delivers intelligent, timely notifications about sentiment changes, ATR band updates, trailing stop adjustments, and trade validity status to help traders make informed decisions.

## 🎯 Core Alert System Architecture

### 🔄 Real-Time Monitoring Engine
```python
# Implementation in: trading_cli.py, enhanced_forex_indices_analysis.py

class PeriodicAlertEngine:
    """
    Central engine for managing periodic alerts across all active symbols
    """
    
    def __init__(self):
        self.active_monitors = {}
        self.alert_scheduler = AlertScheduler()
        self.alert_generators = {
            'sentiment': SentimentAlertGenerator(),
            'atr_bands': ATRBandAlertGenerator(),
            'trade_validity': TradeValidityAlertGenerator(),
            'technical_signals': TechnicalSignalAlertGenerator()
        }
        self.alert_history = AlertHistory()
        
    def start_symbol_monitoring(self, symbol_key, group_id, alert_config):
        """Start comprehensive monitoring for a symbol"""
        
    def stop_symbol_monitoring(self, symbol_key):
        """Stop monitoring for a symbol"""
        
    def update_monitoring_interval(self, symbol_key, new_interval_minutes):
        """Update alert frequency for a symbol"""
        
    def get_monitoring_status(self):
        """Get current status of all active monitors"""
```

### ⏰ Alert Scheduling System
```python
class AlertScheduler:
    """
    Intelligent scheduling system for periodic alerts
    """
    
    def __init__(self):
        self.scheduled_jobs = {}
        self.interval_jobs = {}
        self.market_hours_jobs = {}
        
    def schedule_interval_alerts(self, symbol_key, interval_minutes, alert_function):
        """
        Schedule alerts at fixed intervals
        
        Supported Intervals:
        - Ultra-fast: 1-5 minutes (scalping)
        - Fast: 5-15 minutes (day trading)
        - Standard: 15-60 minutes (swing trading)
        - Slow: 1-4 hours (position trading)
        """
        
    def schedule_market_hours_alerts(self, symbol_key, market_config, alert_function):
        """
        Schedule alerts based on market trading hours
        
        Market Configurations:
        - Forex: 24/5 with session-based intervals
        - NYSE/NASDAQ: 9:30 AM - 4:00 PM EST
        - Crypto: 24/7 continuous monitoring
        - European: 8:00 AM - 4:30 PM GMT
        """
        
    def schedule_volatility_adaptive_alerts(self, symbol_key, base_interval, volatility_multiplier):
        """
        Schedule alerts that adapt to market volatility
        - High volatility: More frequent alerts
        - Low volatility: Less frequent alerts
        """
```

## 🎯 Alert Types & Functionality

### 📊 Sentiment Change Alerts
```python
class SentimentAlertGenerator:
    """
    Monitor and alert on sentiment changes for active symbols
    """
    
    def __init__(self):
        self.sentiment_history = {}
        self.confidence_thresholds = {
            'significant_change': 0.15,
            'minor_change': 0.05,
            'direction_change': True
        }
    
    def check_sentiment_changes(self, symbol_key, current_analysis, previous_analysis):
        """
        Detect and alert on sentiment changes
        
        Monitored Changes:
        - Overall sentiment direction (BULLISH ↔ BEARISH)
        - Confidence score changes
        - Signal strength variations
        - New technical signals emergence
        """
        
        changes_detected = {
            'sentiment_direction_change': self._check_direction_change(current_analysis, previous_analysis),
            'confidence_change': self._check_confidence_change(current_analysis, previous_analysis),
            'signal_strength_change': self._check_signal_strength_change(current_analysis, previous_analysis),
            'new_signals': self._check_new_signals(current_analysis, previous_analysis)
        }
        
        if any(changes_detected.values()):
            self.generate_sentiment_alert(symbol_key, current_analysis, previous_analysis, changes_detected)
    
    def generate_sentiment_alert(self, symbol_key, current_analysis, previous_analysis, changes):
        """
        Generate comprehensive sentiment change alert
        
        Alert Format:
        🚨 SENTIMENT ALERT - EURUSD (15m) - 14:30:15
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📈 SENTIMENT CHANGE DETECTED
        
        Previous Analysis (14:15):
        • Sentiment: BULLISH (Confidence: 72%)
        • Signals: 4 Bullish, 1 Bearish, 2 Neutral
        
        Current Analysis (14:30):
        • Sentiment: BEARISH (Confidence: 68%) ⚠️ CHANGED
        • Signals: 2 Bullish, 4 Bearish, 1 Neutral
        
        🔍 KEY INDICATOR CHANGES:
        • RSI: 65.2 → 38.5 (entered oversold territory)
        • MACD: 0.0008 → -0.0012 (bearish crossover detected)
        • ADX: 22.5 → 26.8 (trend strength increasing)
        • Stochastic: 78.2 → 24.1 (oversold signal)
        
        💡 TRADING IMPLICATIONS:
        • Previous bullish momentum has weakened
        • New bearish signals emerging
        • Consider position review or exit strategy
        
        📊 Current Price: 1.0845 (-12 pips from last alert)
        """
```

### 📈 ATR Band Update Alerts
```python
class ATRBandAlertGenerator:
    """
    Monitor ATR bands for trailing stop loss management
    """
    
    def __init__(self):
        self.atr_history = {}
        self.band_sensitivity = 0.5  # Minimum change to trigger alert
        
    def check_atr_band_updates(self, symbol_key, current_atr_data, previous_atr_data):
        """
        Monitor ATR band changes for active positions
        
        Monitored Metrics:
        - ATR value changes
        - Upper/Lower band shifts
        - Price position within bands
        - Volatility regime changes
        """
        
        band_changes = {
            'atr_value_change': self._calculate_atr_change(current_atr_data, previous_atr_data),
            'upper_band_shift': self._calculate_band_shift(current_atr_data['upper'], previous_atr_data['upper']),
            'lower_band_shift': self._calculate_band_shift(current_atr_data['lower'], previous_atr_data['lower']),
            'volatility_regime_change': self._check_volatility_regime(current_atr_data, previous_atr_data)
        }
        
        if self._significant_band_change(band_changes):
            self.generate_atr_band_alert(symbol_key, current_atr_data, previous_atr_data, band_changes)
    
    def generate_atr_band_alert(self, symbol_key, current_atr, previous_atr, changes):
        """
        Generate ATR band update alert for trailing stops
        
        Alert Format:
        📊 ATR BANDS UPDATE - GBPUSD (1h) - 15:45:30
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📈 VOLATILITY & TRAILING STOP UPDATE
        
        Current Market Data:
        • Price: 1.2634
        • ATR (14): 0.0089 (+0.0012 from previous)
        • Volatility: INCREASING ⬆️
        
        📊 ATR BAND LEVELS:
        Previous (15:30):
        • Upper Band: 1.2698 
        • Lower Band: 1.2532
        
        Current (15:45):
        • Upper Band: 1.2723 (+25 pips) ⬆️
        • Lower Band: 1.2545 (+13 pips) ⬆️
        
        🎯 TRAILING STOP RECOMMENDATIONS:
        
        For LONG Positions:
        • Conservative Stop: 1.2556 (78 pips below current)
        • Aggressive Stop: 1.2595 (39 pips below current)
        • Previous Stop: 1.2543 → New Stop: 1.2556 (+13 pips)
        
        For SHORT Positions:
        • Conservative Stop: 1.2712 (78 pips above current)
        • Aggressive Stop: 1.2673 (39 pips above current)
        • Previous Stop: 1.2687 → New Stop: 1.2712 (+25 pips)
        
        📍 PRICE POSITION:
        • Band Position: Lower Third (Bullish bias)
        • Distance to Upper: +89 pips (3.5% profit potential)
        • Distance to Lower: -89 pips (3.5% risk)
        
        ⚠️ RISK MANAGEMENT NOTE:
        Increased volatility detected - consider tighter position sizing
        """
```

### ⚖️ Trade Validity Status Alerts
```python
class TradeValidityAlertGenerator:
    """
    Monitor the validity of original trade decisions
    """
    
    def __init__(self):
        self.original_analyses = {}
        self.validity_thresholds = {
            'confidence_drop': 0.20,
            'sentiment_reversal': True,
            'signal_deterioration': 0.30
        }
    
    def store_original_trade_analysis(self, symbol_key, trade_entry_data, analysis_data):
        """Store original analysis when trade is entered"""
        self.original_analyses[symbol_key] = {
            'entry_time': trade_entry_data['timestamp'],
            'entry_price': trade_entry_data['price'],
            'trade_direction': trade_entry_data['direction'],
            'original_sentiment': analysis_data['overall_sentiment'],
            'original_confidence': analysis_data['confidence_score'],
            'original_signals': analysis_data['signals_summary'],
            'key_indicators': analysis_data['indicators']
        }
    
    def check_trade_validity(self, symbol_key, current_analysis):
        """
        Check if original trade reasoning is still valid
        
        Validity Factors:
        - Sentiment alignment with original trade
        - Confidence level maintenance
        - Signal deterioration assessment
        - Risk/reward ratio changes
        """
        
        if symbol_key not in self.original_analyses:
            return None
            
        original = self.original_analyses[symbol_key]
        
        validity_assessment = {
            'sentiment_valid': self._check_sentiment_validity(original, current_analysis),
            'confidence_valid': self._check_confidence_validity(original, current_analysis),
            'signals_valid': self._check_signals_validity(original, current_analysis),
            'overall_validity': None
        }
        
        validity_assessment['overall_validity'] = self._calculate_overall_validity(validity_assessment)
        
        self.generate_trade_validity_alert(symbol_key, original, current_analysis, validity_assessment)
    
    def generate_trade_validity_alert(self, symbol_key, original, current, validity):
        """
        Generate comprehensive trade validity alert
        
        Alert Format:
        ⚖️ TRADE VALIDITY CHECK - AAPL (30m) - 16:20:45
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📊 TRADE PERFORMANCE & VALIDITY ASSESSMENT
        
        🎯 ORIGINAL TRADE (14:15):
        • Direction: LONG @ $145.50
        • Sentiment: BULLISH (75% confidence)
        • Key Signals: RSI oversold bounce, MACD bullish cross
        • Trade Age: 2h 5m
        
        📈 CURRENT STATUS (16:20):
        • Current Price: $147.20 (+$1.70, +1.17%)
        • Current Sentiment: BULLISH (71% confidence)
        • Unrealized P&L: +$170.00 (100 shares)
        
        ✅ VALIDITY ASSESSMENT:
        
        ✅ Sentiment Alignment: VALID
        • Original: BULLISH → Current: BULLISH ✓
        • Confidence: 75% → 71% (minor decline)
        
        ✅ Signal Integrity: VALID  
        • RSI: Still in healthy bullish range (58.2)
        • MACD: Maintaining bullish momentum
        • New confirmations: Bollinger Band breakout
        
        ✅ Risk Management: OPTIMAL
        • Stop Loss: $143.20 (-$2.30, -1.58%) ✓
        • Take Profit: $149.80 (+$2.60, +1.79%) ✓
        • Risk/Reward: 1:1.13 → Improved to 1:1.53
        
        🎯 RECOMMENDATION: HOLD POSITION
        • Trade thesis remains intact
        • Risk/reward has improved
        • Consider partial profit taking at $148.50
        
        📊 PERFORMANCE METRICS:
        • Win Rate: 85% (last 20 trades)
        • Average Hold Time: 3h 15m
        • Best Exit: +2.1% (take profit trigger)
        """
```

### 🔔 Technical Signal Alerts
```python
class TechnicalSignalAlertGenerator:
    """
    Alert on new technical signals and crossovers
    """
    
    def __init__(self):
        self.signal_history = {}
        self.crossover_detector = EnhancedCrossoverDetector()
        
    def check_new_technical_signals(self, symbol_key, current_analysis, previous_analysis):
        """
        Monitor for new technical signals and crossovers
        
        Signal Types:
        - Indicator crossovers (MACD, Stochastic, etc.)
        - Support/resistance breaks
        - Trend line breaks
        - Volume confirmations
        """
        
        new_signals = {
            'crossovers': self._detect_new_crossovers(current_analysis, previous_analysis),
            'breakouts': self._detect_breakouts(current_analysis, previous_analysis),
            'confirmations': self._detect_confirmations(current_analysis, previous_analysis),
            'divergences': self._detect_divergences(current_analysis, previous_analysis)
        }
        
        if any(new_signals.values()):
            self.generate_technical_signal_alert(symbol_key, current_analysis, new_signals)
    
    def generate_technical_signal_alert(self, symbol_key, analysis, signals):
        """
        Generate technical signal alert
        
        Alert Format:
        🔔 NEW TECHNICAL SIGNALS - USDJPY (1h) - 17:00:00
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ⚡ FRESH TECHNICAL SIGNALS DETECTED
        
        📊 Current Price: 149.82 JPY
        
        🎯 NEW SIGNALS DETECTED:
        
        1. 📈 MACD BULLISH CROSSOVER
        • MACD Line: -0.12 → +0.08 (crossed signal line)
        • Signal Strength: STRONG
        • Last Crossover: 3 days ago (successful)
        
        2. 🎯 RSI OVERSOLD BOUNCE
        • RSI: 28.5 → 35.2 (bouncing from oversold)
        • Bounce Strength: MODERATE
        • Historical Success Rate: 73%
        
        3. 📊 STOCHASTIC BULLISH DIVERGENCE
        • Price: Lower low at 149.25
        • Stochastic: Higher low (bullish divergence)
        • Divergence Strength: STRONG
        
        4. 🔄 VOLUME CONFIRMATION
        • Volume: +45% above average
        • Price/Volume Alignment: BULLISH
        • Institutional Activity: DETECTED
        
        💡 SIGNAL CONFLUENCE:
        • Total Bullish Signals: 7 (+3 new)
        • Total Bearish Signals: 2 (-1)
        • Net Signal Strength: +5 BULLISH
        
        🎯 TRADING IMPLICATIONS:
        • Strong bullish momentum building
        • Multiple timeframe alignment
        • Entry opportunity: 149.80-150.00
        • Target: 151.50 (+170 pips)
        • Stop: 149.20 (-60 pips)
        • Risk/Reward: 1:2.8
        """
```

## ⚙️ Alert Configuration System

### 🎛️ Symbol-Specific Alert Settings
```python
class SymbolAlertConfiguration:
    """
    Configure alerts for individual symbols with active trades
    """
    
    def __init__(self, symbol_key, group_id):
        self.symbol_key = symbol_key
        self.group_id = group_id
        self.alert_config = {
            'monitoring_enabled': True,
            'alert_interval_minutes': 15,
            'active_trade_info': None,
            'alert_types': {
                'sentiment_changes': {
                    'enabled': True,
                    'sensitivity': 'medium',  # low, medium, high
                    'minimum_confidence_change': 0.10
                },
                'atr_band_updates': {
                    'enabled': True,
                    'update_threshold_pips': 5,
                    'trailing_stop_alerts': True
                },
                'trade_validity_checks': {
                    'enabled': True,
                    'check_interval_minutes': 30,
                    'validity_threshold': 0.60
                },
                'technical_signals': {
                    'enabled': True,
                    'signal_types': ['crossovers', 'breakouts', 'divergences'],
                    'minimum_signal_strength': 'medium'
                }
            },
            'notification_methods': ['console', 'log_file'],
            'quiet_hours': {
                'enabled': False,
                'start_time': '22:00',
                'end_time': '06:00'
            }
        }
    
    def activate_for_trade(self, trade_entry_info):
        """Activate alerts when entering a trade"""
        self.alert_config['active_trade_info'] = {
            'entry_time': trade_entry_info['timestamp'],
            'entry_price': trade_entry_info['price'],
            'direction': trade_entry_info['direction'],
            'position_size': trade_entry_info['size'],
            'stop_loss': trade_entry_info['stop_loss'],
            'take_profit': trade_entry_info['take_profit']
        }
        self.alert_config['monitoring_enabled'] = True
        
    def deactivate_alerts(self):
        """Deactivate alerts when closing trade"""
        self.alert_config['monitoring_enabled'] = False
        self.alert_config['active_trade_info'] = None
        
    def update_alert_frequency(self, new_interval_minutes):
        """Update alert frequency based on market conditions"""
        self.alert_config['alert_interval_minutes'] = new_interval_minutes
```

### 📊 Adaptive Alert Intervals
```python
class AdaptiveAlertScheduler:
    """
    Dynamically adjust alert intervals based on market conditions
    """
    
    def __init__(self):
        self.base_intervals = {
            '1m': 5,     # 5-minute alerts for 1-min charts
            '5m': 15,    # 15-minute alerts for 5-min charts
            '15m': 15,   # 15-minute alerts for 15-min charts
            '30m': 30,   # 30-minute alerts for 30-min charts
            '1h': 60,    # 1-hour alerts for 1-hour charts
            '4h': 240,   # 4-hour alerts for 4-hour charts
            '1d': 1440   # Daily alerts for daily charts
        }
        
    def calculate_adaptive_interval(self, symbol_key, base_timeframe, current_volatility):
        """
        Calculate adaptive alert interval based on volatility
        
        Adaptation Rules:
        - High volatility: 50% more frequent alerts
        - Medium volatility: Standard frequency
        - Low volatility: 50% less frequent alerts
        """
        
        base_interval = self.base_intervals.get(base_timeframe, 60)
        
        if current_volatility > 0.02:  # High volatility
            adapted_interval = int(base_interval * 0.5)
        elif current_volatility < 0.005:  # Low volatility
            adapted_interval = int(base_interval * 1.5)
        else:  # Medium volatility
            adapted_interval = base_interval
            
        # Ensure minimum/maximum bounds
        adapted_interval = max(1, min(adapted_interval, 480))  # 1 min to 8 hours
        
        return adapted_interval
    
    def adjust_for_market_session(self, symbol_key, base_interval, current_session):
        """
        Adjust intervals based on market session activity
        
        Session Adjustments:
        - Asian session: +25% interval (slower)
        - London session: -25% interval (faster)
        - New York session: Standard interval
        - Overlap sessions: -50% interval (much faster)
        """
        
        session_multipliers = {
            'asian': 1.25,
            'london': 0.75,
            'new_york': 1.0,
            'london_ny_overlap': 0.5,
            'asian_london_overlap': 0.8
        }
        
        multiplier = session_multipliers.get(current_session, 1.0)
        return int(base_interval * multiplier)
```

## 🎯 CLI Alert Management Interface

### 💻 Interactive Alert Control
```bash
# Access periodic alerts through main CLI
python trading_cli.py

# Periodic Alert Management Menu:
# 📢 PERIODIC ALERT SYSTEM
# ├── 1. 🎯 Activate Symbol Alerts
# ├── 2. ⏰ Configure Alert Intervals  
# ├── 3. 🔔 Alert Type Selection
# ├── 4. 📊 View Active Monitors
# ├── 5. 📈 Alert Performance Stats
# ├── 6. ⚙️ Advanced Alert Settings
# ├── 7. 📁 Alert History & Logs
# ├── 8. 🚨 Test Alert System
# └── 9. 🔙 Back to Main Menu
```

### 🎛️ CLI Alert Operations
```python
class CLIAlertManager:
    """
    Command-line interface for alert management
    """
    
    def cli_activate_symbol_alerts(self):
        """Interactive symbol alert activation"""
        print("🎯 SYMBOL ALERT ACTIVATION")
        print("=" * 40)
        
        # List available symbols from groups
        available_symbols = self.get_available_symbols()
        
        # Interactive symbol selection
        selected_symbols = self.interactive_symbol_selection(available_symbols)
        
        # Configure alerts for each selected symbol
        for symbol_key in selected_symbols:
            self.configure_symbol_alerts_interactive(symbol_key)
        
        print("✅ Symbol alerts activated successfully!")
    
    def cli_configure_alert_intervals(self):
        """Interactive alert interval configuration"""
        
    def cli_view_active_monitors(self):
        """Display currently active alert monitors"""
        print("📊 ACTIVE ALERT MONITORS")
        print("=" * 50)
        
        active_monitors = self.alert_engine.get_active_monitors()
        
        if not active_monitors:
            print("❌ No active monitors")
            return
            
        for symbol_key, monitor_info in active_monitors.items():
            print(f"🎯 {monitor_info['symbol']} ({monitor_info['asset_type']})")
            print(f"   Interval: {monitor_info['interval_minutes']} minutes")
            print(f"   Status: {'🟢 Active' if monitor_info['enabled'] else '🔴 Paused'}")
            print(f"   Last Alert: {monitor_info['last_alert_time']}")
            print(f"   Alert Count: {monitor_info['alert_count']} today")
            print()
    
    def cli_alert_performance_stats(self):
        """Display alert system performance statistics"""
        
    def cli_test_alert_system(self):
        """Test alert system functionality"""
```

## 📊 Alert Analytics & Performance

### 📈 Alert Effectiveness Tracking
```python
class AlertPerformanceAnalyzer:
    """
    Analyze effectiveness and performance of alert system
    """
    
    def __init__(self):
        self.alert_outcomes = {}
        self.response_times = {}
        self.accuracy_metrics = {}
        
    def track_alert_outcome(self, alert_id, outcome_data):
        """
        Track the outcome of alerts for effectiveness analysis
        
        Outcome Types:
        - 'actionable': Alert led to trading action
        - 'informational': Alert provided useful information
        - 'noise': Alert was not useful
        - 'false_positive': Alert was incorrect
        """
        
    def calculate_alert_accuracy(self, time_period='7d'):
        """Calculate accuracy metrics for alert system"""
        
    def analyze_optimal_intervals(self, symbol_key):
        """Analyze optimal alert intervals for specific symbols"""
        
    def generate_performance_report(self):
        """
        Generate comprehensive alert performance report
        
        Report Contents:
        - Alert frequency statistics
        - Accuracy by alert type
        - Response time analysis  
        - Optimal interval recommendations
        - Cost/benefit analysis
        """
```

### 🎯 Alert Optimization Engine
```python
class AlertOptimizationEngine:
    """
    Continuously optimize alert parameters for better performance
    """
    
    def __init__(self):
        self.optimization_data = {}
        self.learning_algorithms = {}
        
    def optimize_alert_intervals(self, symbol_key, historical_performance):
        """Optimize alert intervals based on historical effectiveness"""
        
    def optimize_alert_thresholds(self, alert_type, performance_data):
        """Optimize sensitivity thresholds for different alert types"""
        
    def machine_learning_optimization(self, training_data):
        """Use ML algorithms to optimize alert parameters"""
        
    def a_b_test_alert_configurations(self, test_configs):
        """A/B test different alert configurations"""
```

## 🔧 Advanced Alert Features

### 🎯 Context-Aware Alerts
```python
class ContextAwareAlertSystem:
    """
    Generate alerts with market context and background information
    """
    
    def add_market_context(self, alert_data, symbol_key):
        """Add relevant market context to alerts"""
        
    def add_historical_context(self, alert_data, symbol_key):
        """Add historical performance context"""
        
    def add_correlation_context(self, alert_data, symbol_key):
        """Add information about correlated assets"""
        
    def add_news_sentiment_context(self, alert_data, symbol_key):
        """Add relevant news and sentiment context"""
```

### 🚨 Emergency Alert System
```python
class EmergencyAlertSystem:
    """
    High-priority alerts for critical market events
    """
    
    def setup_emergency_triggers(self, symbol_key, emergency_config):
        """
        Setup emergency alert triggers
        
        Emergency Conditions:
        - Rapid price movements (>5% in 5 minutes)
        - Volume spikes (>1000% of average)
        - Gap openings (>2% gap)
        - Stop loss breaches
        - Major news events
        """
        
    def trigger_emergency_alert(self, symbol_key, emergency_type, severity):
        """Trigger immediate emergency alert"""
        
    def emergency_notification_methods(self):
        """Multiple notification channels for emergencies"""
        return {
            'console_flash': 'Immediate console notification',
            'audio_alert': 'Sound notification',
            'desktop_notification': 'System tray notification',
            'email_alert': 'Emergency email notification',
            'sms_alert': 'SMS notification (if configured)'
        }
```

The Periodic Alert System transforms TradeMaster Pro into a proactive trading assistant, providing intelligent, timely, and contextual information to support informed trading decisions across all monitored symbols and timeframes.
