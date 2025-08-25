# TradeMaster Pro - Advanced Trading Analysis Engine

**TradeMaster Pro** is a comprehensive financial market analysis engine that provides sophisticated trading tools, technical indicators, and automated analysis capabilities for traders and analysts. This backend system powers a complete trading infrastructure with CLI interface, symbol group management, and advanced indicator analysis.

## 🚀 Overview

TradeMaster Pro is designed to handle multiple asset classes (Forex, Stocks, Cryptocurrencies, and Indices) with configurable timeframes, automated analysis pipelines, and real-time monitoring capabilities. The system provides both programmatic API access and an interactive CLI interface for comprehensive market analysis.

## 🎯 Key Features

### 📊 Multi-Asset Support
- **Forex Pairs**: 50+ major, minor, and exotic currency pairs
- **Stocks**: 130+ popular stocks across different sectors
- **Cryptocurrencies**: 88+ digital currencies with market categorization
- **Indices**: Major global indices (S&P 500, NASDAQ, DAX, etc.)

### 🔧 Technical Analysis
- **20+ Technical Indicators**: RSI, MACD, Stochastic, ADX, Bollinger Bands, etc.
- **Oscillators**: Advanced oscillator analysis with status tracking
- **Crossover Detection**: Automated signal detection with volatility filtering
- **Custom Strategies**: Flexible strategy creation and backtesting framework

### 🎛️ Symbol Group Management
- **CRUD Operations**: Create, read, update, and delete symbol groups
- **Flexible Configuration**: Different timeframes and periods per symbol
- **Batch Processing**: Analyze multiple symbols simultaneously
- **Real-time Monitoring**: Periodic sentiment updates and alerts

### 🖥️ Interactive CLI Interface
- **Enhanced Navigation**: Arrow key support and intuitive menu system
- **Case-insensitive Commands**: Flexible command input with auto-detection
- **Real-time Analysis**: Live market data and indicator updates
- **Group Management**: Interactive symbol group configuration

## 📁 System Architecture

```
backend/
├── Core Pipeline System
│   ├── pipeline_main.py           # Main orchestrator
│   ├── pipeline_fetching_data.py  # Data fetching engine
│   ├── pipeline_applying_indicator.py # Technical indicators
│   └── pipeline_defining_strategy.py  # Strategy framework
│
├── Symbol Management
│   ├── symbol_groups_manager.py   # CRUD operations for groups
│   ├── crypto_symbols.py          # 88+ cryptocurrency mappings
│   ├── stocks_symbols.py          # 130+ stock symbols by sector
│   ├── forex_symbols.py           # Major/minor/exotic forex pairs
│   └── indices_symbols.py         # Global market indices
│
├── Analysis Engines
│   ├── group_analysis_engine.py   # Batch symbol analysis
│   ├── enhanced_forex_indices_analysis.py # Advanced analysis
│   ├── indicators.py              # Core technical indicators
│   └── indicators_oscillators.py  # Oscillator implementations
│
├── CLI Interface
│   ├── trading_cli.py              # Interactive command-line interface
│   ├── demo_cli.py                 # CLI demonstration scripts
│   └── demo_enhanced_features.py   # Feature showcases
│
├── Data Management
│   ├── yfinance_data_loader.py     # Yahoo Finance integration
│   ├── symbol_groups/              # Group configurations
│   └── preset/                     # Analysis presets
│
└── Testing & Documentation
    ├── test_*.py                   # Comprehensive test suite
    ├── BUILD_SUMMARY.md            # System build documentation
    └── ENHANCED_CLI_SUMMARY.md     # CLI features documentation
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install pandas numpy yfinance schedule

# Clone or navigate to the backend directory
cd backend/
```

### Basic Usage

#### 1. Interactive CLI Interface
```bash
# Start the interactive trading CLI
python trading_cli.py
```

The CLI provides:
- **Arrow Key Navigation**: Use arrow keys to navigate menus
- **Symbol Group Management**: Create, edit, and manage symbol groups
- **Real-time Analysis**: Get live market analysis and indicators
- **Periodic Monitoring**: Set up automated analysis alerts

#### 2. Programmatic API Access

```python
# Import the main pipeline
from pipeline_main import TradingPipeline

# Initialize the pipeline
pipeline = TradingPipeline()

# Analyze a single symbol
result = pipeline.analyze_symbol('EURUSD', 'forex', period='7d', interval='1h')
print(f"Latest Price: {result['latest_price']}")
print(f"Sentiment: {result['overall_sentiment']}")

# Analyze multiple symbols
symbols = ['AAPL', 'GOOGL', 'MSFT']
results = pipeline.analyze_batch(symbols, 'stocks')
```

#### 3. Symbol Group Management

```python
from symbol_groups_manager import SymbolGroupManager, SymbolConfig

# Initialize manager
manager = SymbolGroupManager()

# Create a new symbol group
symbols = {
    'eurusd_1h': SymbolConfig('EURUSD', 'forex', '1h', '7d'),
    'gbpusd_1h': SymbolConfig('GBPUSD', 'forex', '1h', '7d')
}

group_id = manager.create_group(
    name="Major Forex Pairs",
    description="High-volume forex pairs for day trading",
    symbols=symbols
)

# Analyze the group
from group_analysis_engine import GroupAnalysisEngine
engine = GroupAnalysisEngine()
results = engine.analyze_group(group_id)
```

## 📊 Data Fetching Capabilities

### Supported Data Sources
- **Yahoo Finance**: Primary data source with broad market coverage
- **Real-time Data**: Live market data for active trading
- **Historical Data**: Comprehensive historical analysis

### Timeframe Options
- **Minute**: 1m, 5m, 15m, 30m
- **Hourly**: 1h, 2h, 4h
- **Daily**: 1d
- **Weekly/Monthly**: 1wk, 1mo

### Period Options
- **Short-term**: 1d, 5d, 1wk
- **Medium-term**: 1mo, 3mo, 6mo
- **Long-term**: 1y, 2y, 5y, max

## 🔧 Technical Indicators

### Trend Indicators
- **ADX (Average Directional Index)**: Trend strength measurement
- **MACD**: Moving Average Convergence Divergence
- **Moving Averages**: SMA, EMA with customizable periods
- **Bollinger Bands**: Volatility and mean reversion analysis

### Momentum Oscillators
- **RSI (Relative Strength Index)**: Overbought/oversold conditions
- **Stochastic Oscillator**: Price momentum analysis
- **Williams %R**: Price reversal signals
- **CCI (Commodity Channel Index)**: Cyclical trends

### Volatility Indicators
- **ATR (Average True Range)**: Volatility measurement
- **Bollinger Band Width**: Volatility expansion/contraction
- **Standard Deviation**: Price dispersion analysis

### Volume Analysis
- **Volume Moving Averages**: Volume trend analysis
- **On-Balance Volume (OBV)**: Volume-price relationship
- **Volume Rate of Change**: Volume momentum

## 🎛️ Symbol Groups Configuration

### Group Structure
```json
{
  "group_id": "major_forex",
  "name": "Major Forex Pairs",
  "description": "High-volume currency pairs",
  "symbols": {
    "eurusd_1h": {
      "symbol": "EURUSD",
      "asset_type": "forex",
      "timeframe": "1h",
      "period": "7d",
      "data_source": "yfinance",
      "enabled": true
    }
  },
  "enabled": true,
  "tags": ["forex", "major"],
  "metadata": {}
}
```

### Supported Asset Types
- **forex**: Currency pairs (e.g., EURUSD, GBPUSD)
- **stocks**: Equity securities (e.g., AAPL, GOOGL)
- **crypto**: Cryptocurrencies (e.g., BTC, ETH)
- **indices**: Market indices (e.g., SPY, QQQ)

## 🚀 CLI Interface Features

### Enhanced Navigation
- **Arrow Keys**: Navigate menus with arrow keys
- **Case-insensitive Commands**: `ext`, `EXT`, `clr`, `CLR` all exit
- **Special Characters**: `+`/`-` for enable/disable operations
- **Smart Input**: Automatic command detection and processing

### Menu System
```
🎯 TRADING ANALYSIS CLI
========================
1. 👥 Manage Symbol Groups
2. 📊 Run Group Analysis
3. 🔍 Analyze Individual Symbol
4. ⚙️  Configure Indicators
5. 📈 Real-time Monitoring
6. 🎯 Strategy Backtesting
7. 📋 View Analysis History
8. ⚡ Quick Analysis Presets
```

### Real-time Features
- **Live Price Updates**: Real-time price monitoring
- **Sentiment Alerts**: Automated sentiment change notifications
- **Periodic Analysis**: Scheduled analysis runs
- **Performance Monitoring**: Track analysis success rates

## 🧪 Testing and Validation

### Test Suite
```bash
# Run all tests
python -m pytest test_*.py -v

# Run specific test modules
python test_pipeline.py          # Pipeline functionality
python test_cli_functionality.py # CLI interface tests
python test_enhanced_cli.py      # Enhanced CLI features
python test_simple_groups.py     # Symbol group operations
```

### Validation Features
- **Data Integrity**: Automatic data validation and cleaning
- **Symbol Verification**: Real-time symbol availability checking
- **Performance Metrics**: Analysis speed and accuracy tracking
- **Error Handling**: Comprehensive error detection and recovery

## 📈 Advanced Features

### Strategy Framework
```python
from pipeline_defining_strategy import StrategyLibrary, TradingStrategy

# Create custom strategy
strategy = TradingStrategy(
    name="RSI Crossover",
    conditions={
        'buy': 'RSI < 30 and price > SMA_20',
        'sell': 'RSI > 70 and price < SMA_20'
    }
)

# Backtest strategy
results = strategy.backtest(data, start_date='2024-01-01')
```

### Batch Analysis
```python
from group_analysis_engine import GroupAnalysisEngine

engine = GroupAnalysisEngine()

# Analyze all groups
all_results = engine.analyze_all_groups()

# Generate comprehensive report
report = engine.generate_group_report(group_id, include_charts=True)
```

### Real-time Monitoring
```python
from trading_cli import TradingCLI

cli = TradingCLI()

# Start periodic monitoring
cli.start_periodic_monitoring(
    interval_minutes=15,
    symbols=['EURUSD', 'GBPUSD', 'USDJPY']
)
```

## 🔧 Configuration Options

### Pipeline Configuration
```python
config = {
    'data': {
        'default_period': '7d',
        'default_interval': '1h',
        'cache_enabled': True
    },
    'indicators': {
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'adx_threshold': 18
    },
    'analysis': {
        'volatility_filter': True,
        'min_data_points': 50,
        'confidence_threshold': 0.7
    }
}

pipeline = TradingPipeline(config)
```

### Indicator Settings
```python
from trading_cli import IndicatorSettings

settings = IndicatorSettings()
settings.update_setting('crossover_indicators', 'macd', True)
settings.update_setting('adx_threshold', 25)
settings.save_settings()
```

## 📊 Output and Reporting

### Analysis Results Format
```python
{
    'symbol': 'EURUSD',
    'asset_type': 'forex',
    'latest_price': 1.0845,
    'price_change': 0.0012,
    'price_change_pct': 0.11,
    'overall_sentiment': 'BULLISH',
    'indicators': {
        'RSI': 45.2,
        'MACD': 0.0008,
        'ADX': 22.5
    },
    'signals_summary': {
        'bullish': 3,
        'bearish': 1,
        'neutral': 2
    },
    'analysis_timestamp': '2024-12-28 10:30:00'
}
```

### Export Options
- **JSON**: Machine-readable analysis results
- **CSV**: Spreadsheet-compatible data export
- **Reports**: Human-readable analysis summaries
- **Charts**: Visual analysis outputs (planned feature)

## 🛠️ Extending the System

### Adding New Indicators
```python
class CustomIndicator:
    def __init__(self, period=14):
        self.period = period
    
    def calculate(self, data):
        # Custom indicator logic
        return result

# Register with indicator manager
indicator_manager.register_indicator('custom', CustomIndicator)
```

### Creating Custom Strategies
```python
def custom_strategy(data, indicators):
    signals = []
    # Strategy logic
    return signals

# Register strategy
strategy_library.register_strategy('custom_strat', custom_strategy)
```

## 📚 Documentation and Support

### Additional Resources
- **BUILD_SUMMARY.md**: Detailed system build documentation
- **ENHANCED_CLI_SUMMARY.md**: CLI feature specifications
- **crossover_feature.md**: Crossover detection documentation
- **instructions.py**: Comprehensive API documentation

### Support
- All core functionality is thoroughly tested
- Comprehensive error handling and logging
- Backward compatibility with existing code
- Modular architecture for easy maintenance

---

**TradeMaster Pro** provides a complete trading analysis infrastructure that scales from individual symbol analysis to comprehensive market monitoring. Whether you're a day trader needing real-time analysis or a quantitative analyst building sophisticated strategies, TradeMaster Pro delivers the tools and reliability you need for professional financial market analysis.
