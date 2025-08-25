# Dual Supertrend Check Single Timeframe Strategy

## Overview

The **dual-supertrend-check-single-timeframe** strategy is an advanced trading strategy that uses two Supertrend indicators with different parameters to generate buy and sell signals when both indicators align in the same direction. This strategy combines the trend-following capabilities of Supertrend with additional confirmation from baseline indicators like RSI, MACD, and ATR bands for risk management.

## Strategy Details

### Primary Indicators

1. **Supertrend A (Long-term)**
   - Period: 15
   - Multiplier: 3.142
   - Used for longer-term trend identification

2. **Supertrend B (Short-term)**
   - Period: 6
   - Multiplier: 0.66
   - Used for shorter-term trend confirmation

### Confirmation Indicators

- **RSI (14)**: Relative Strength Index for momentum confirmation
- **MACD (12, 26, 9)**: Moving Average Convergence Divergence for trend confirmation
- **ADX (14)**: Average Directional Index for trend strength measurement
- **Stochastic (14, 3, 3)**: Stochastic oscillator for momentum analysis

### Risk Management

- **ATR Bands**: Average True Range based stop-loss and take-profit levels
- **Dynamic Stop Loss**: 2x ATR for tighter risk control
- **Dynamic Take Profit**: 3x ATR for better risk-reward ratio

## Signal Generation Logic

### Buy Signals

Buy signals are generated when:
1. **Both Supertrends turn bullish** (direction_a == 1 AND direction_b == 1)
2. **RSI confirmation**: RSI < 70 (not overbought)
3. **MACD confirmation**: MACD > 0 (bullish momentum)
4. **Trend strength**: ADX > 25 (strong trend)

**Signal Strength Levels:**
- **STRONG_BUY**: 4+ confirmations
- **BUY**: 2-3 confirmations

### Sell Signals

Sell signals are generated when:
1. **Either Supertrend turns bearish** (direction_a == -1 OR direction_b == -1)
2. **RSI confirmation**: RSI > 30 (not oversold)
3. **MACD confirmation**: MACD < 0 (bearish momentum)
4. **Trend strength**: ADX > 25 (strong trend)

**Signal Strength Levels:**
- **STRONG_SELL**: 4+ confirmations
- **SELL**: 2+ confirmations

## Entry and Exit Rules

### Entry Rules

- **Long Entry**: When both Supertrends are bullish with sufficient confirmations
- **Entry Recommended**: When buy_confirmations >= 3

### Exit Rules

- **Exit Signal**: When either Supertrend turns bearish
- **Exit Recommended**: When sell_confirmations >= 2

### Risk Management Levels

- **Stop Loss (Long)**: Current Price - (2 × ATR_14)
- **Take Profit (Long)**: Current Price + (3 × ATR_21)
- **Stop Loss (Short)**: Current Price + (2 × ATR_14)
- **Take Profit (Short)**: Current Price - (3 × ATR_21)

## Supertrend Calculation

The Supertrend indicator is calculated using the following method:

```python
def supertrend_pandas(high, low, close, period, multiplier):
    # Calculate True Range components
    hl = high - low
    hc = (high - close.shift()).abs()
    lc = (low - close.shift()).abs()

    # True Range
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

    # Average True Range (ATR)
    atr = tr.rolling(window=period, min_periods=1).mean()

    # Middle price
    hl2 = (high + low) / 2

    # Upper and Lower Bands
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    # Calculate direction and supertrend values
    # (Stateful logic for direction changes)
```

## Symbol Group Integration

This strategy fully supports all Symbol Group features:

### Configuration Support

- **Timeframe Strategy Setting**: Can be set as "dual-supertrend-check-single-timeframe"
- **Per-Symbol Configuration**: Each symbol in a group can use different strategy parameters
- **Indicator Settings**: Supports custom RSI, MACD, and ATR parameters

### Group Analysis Features

- **Bulk Analysis**: Analyze entire symbol groups with this strategy
- **Comparative Results**: Compare results across symbols in a group
- **Scheduled Analysis**: Works with periodic alerts and scheduled analysis
- **Export Support**: Results can be exported with group analysis

### Periodic Alerts Integration

- **Alert Conditions**: Can trigger alerts based on:
  - Strong buy/sell signals
  - Supertrend direction changes
  - Risk management level breaches
- **Custom Thresholds**: Alert sensitivity can be customized per group

## Usage Examples

### CLI Usage

```bash
# Set strategy in CLI indicator settings
1. Access CLI → Indicator Settings → Timeframe Strategy
2. Select "dual-supertrend-check-single-timeframe"
3. Configure additional parameters as needed
```

### Symbol Group Configuration

```python
from backend.utility.symbol_groups_manager import SymbolGroupManager, SymbolConfig

# Create symbol configuration with dual supertrend strategy
config = SymbolConfig(
    symbol="AAPL",
    timeframe="1d",
    period="3mo",
    strategy="dual-supertrend-check-single-timeframe"
)

# Add to symbol group
group_manager = SymbolGroupManager()
group = group_manager.create_group("Tech Stocks", "Technology stocks analysis")
group_manager.add_symbol_to_group(group.group_id, config)
```

### Programmatic Usage

```python
from backend.strategy import get_strategy

# Get the strategy instance
strategy = get_strategy("dual-supertrend-check-single-timeframe")

# Analyze symbol data
result = strategy.analyze_symbol_data(ohlcv_data, "SYMBOL", config)

# Check results
if result['success']:
    print(f"Signal Strength: {result['trading_signals']['signal_strength']}")
    print(f"Entry Recommended: {result['trading_signals']['entry_recommended']}")
    print(f"Overall Sentiment: {result['overall_sentiment']}")
```

## Output Structure

The strategy returns a comprehensive analysis result containing:

```python
{
    'success': True,
    'latest_price': float,
    'price_change': float,
    'price_change_pct': float,
    'supertrend_signals': {
        'latest_supertrend_a': float,
        'latest_direction_a': int,  # 1 for bullish, -1 for bearish
        'latest_supertrend_b': float,
        'latest_direction_b': int,
        'current_entry_signal': bool,
        'current_exit_signal': bool,
        'current_buy_signal': bool,
        'current_sell_signal': bool
    },
    'trading_signals': {
        'signal_strength': str,  # STRONG_BUY, BUY, SELL, STRONG_SELL, NEUTRAL
        'buy_confirmations': int,
        'sell_confirmations': int,
        'entry_recommended': bool,
        'exit_recommended': bool
    },
    'indicators': {
        'RSI_14': float,
        'MACD': float,
        'ADX_14': float,
        'Stoch_K': float
    },
    'atr_bands': {
        'atr_14': float,
        'stop_loss_long': float,
        'take_profit_long': float,
        'stop_loss_short': float,
        'take_profit_short': float
    },
    'overall_sentiment': str,  # BULLISH, BEARISH, NEUTRAL
    'strategy_used': str
}
```

## Performance Characteristics

### Strengths

- **Trend Following**: Excellent at capturing strong trends
- **Dual Confirmation**: Reduces false signals with two Supertrend parameters
- **Risk Management**: Built-in ATR-based stop losses and take profits
- **Multi-Timeframe Suitable**: Works well on various timeframes
- **Low Lag**: Supertrend indicators respond quickly to price changes

### Considerations

- **Ranging Markets**: May generate false signals in sideways markets
- **Whipsaws**: Can be affected by volatile market conditions
- **Parameter Sensitivity**: Performance depends on chosen periods and multipliers

### Best Suited For

- **Trending Markets**: Works best in strong trending conditions
- **Medium to Long-term Trading**: Designed for swing trading and position trading
- **Risk-Conscious Traders**: Built-in risk management features
- **Multi-Symbol Analysis**: Excellent for portfolio-wide analysis

## Testing and Validation

The strategy includes comprehensive testing capabilities:

- **Backtesting**: Historical performance analysis
- **Signal Validation**: Verification of entry/exit logic
- **Risk Management Testing**: Stop loss and take profit effectiveness
- **Comparison Analysis**: Performance vs. other strategies

Use the included test script to validate the strategy:

```bash
python test_dual_supertrend_strategy.py
```

## Version History

- **v1.0**: Initial implementation with dual Supertrend logic, baseline indicators, and symbol group integration

## Future Enhancements

- **Adaptive Parameters**: Dynamic adjustment of Supertrend parameters based on market volatility
- **Multi-Timeframe Analysis**: Integration of multiple timeframes for signal confirmation
- **Machine Learning Integration**: AI-based parameter optimization
- **Advanced Risk Management**: Position sizing based on volatility and correlation analysis
