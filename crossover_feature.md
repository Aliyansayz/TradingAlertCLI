# Crossover Detection System with Volatility Filter

This document outlines the functionality of the advanced Crossover Detection System integrated into the trading indicators. This system is designed to identify high-probability trading signals by detecting crossovers and filtering them based on market volatility.

## 1. Core Features

### Crossover Detection
The system identifies bullish and bearish crossovers for the following indicators:

-   **Stochastic Oscillator**:
    -   **Bullish Crossover**: The `%K` line crosses above the `%D` line.
    -   **Bearish Crossover**: The `%K` line crosses below the `%D` line.

-   **Directional Movement Index (DMI)**:
    -   **Bullish Crossover**: The `+DI` line crosses above the `-DI` line.
    -   **Bearish Crossover**: The `-DI` line crosses above the `+DI` line.

-   **Supertrend**:
    -   **Bullish Crossover**: The trend flips from bearish (downtrend) to bullish (uptrend).
    -   **Bearish Crossover**: The trend flips from bullish (uptrend) to bearish (downtrend).

### Volatility Filter (ADX-Based)
To avoid false signals in low-volatility markets, a volatility filter using the **Average Directional Index (ADX)** is included.

-   **How it Works**: A crossover signal is only considered valid if the ADX value at the time of the crossover is **above** a specified threshold.
-   **Default Threshold**: `18` (This value is configurable).
-   **Activation**: This feature is enabled by default but can be toggled on or off. A higher ADX value indicates a stronger trend, making the crossover signal more reliable.

### Lookback Period for Recent Crossovers
The system can be configured to check for crossovers only within a recent window of data.

-   **Functionality**: You can specify the number of recent data points (e.g., the last 5 periods) to scan for crossovers.
-   **Example**: If you are using a 30-minute timeframe and set the lookback period to `5`, the system will check for any crossovers that occurred within the last **2.5 hours** (5 * 30 minutes).

## 2. How to Use

The crossover detection logic is encapsulated within a `CrossoverDetector` class, which is now integrated into the `Stochastic_Oscillator`, `SupertrendIndicator`, and `ADX` indicator classes.

### Configuration
You can configure the crossover settings when initializing an indicator:

```python
from backend.indicators import Stochastic_Oscillator, ADX

# --- Configuration ---
crossover_settings = {
    "crossover_enabled": True,
    "volatility_filter_enabled": True,
    "adx_threshold": 20,  # Set a custom ADX threshold
    "lookback_period": 5    # Check for crossovers in the last 5 periods
}

# --- Initialization ---
# Initialize ADX first to pass it to other indicators
adx_indicator = ADX(adx_period=14)

# Initialize Stochastic with crossover settings and the ADX indicator
stoch_indicator = Stochastic_Oscillator(
    k_period=14,
    crossover_settings=crossover_settings,
    adx_indicator=adx_indicator  # Pass the ADX instance for volatility filtering
)
```

### Accessing Crossover Signals
After calculating the indicator values, you can access the crossover results directly from the indicator object.

```python
# Assume 'eurusd_data' is a pandas DataFrame with OHLC data

# 1. Calculate ADX first
adx_data = adx_indicator.calculate(eurusd_data)

# 2. Calculate Stochastic Oscillator
stoch_data = stoch_indicator.calculate(eurusd_data)

# 3. Get the latest crossover signal
latest_signal = stoch_indicator.get_latest_crossover()

if latest_signal:
    print(f"Crossover detected for Stochastic Oscillator!")
    print(f"  - Type: {latest_signal['type']}")
    print(f"  - Index: {latest_signal['index']}")
    print(f"  - Price at Crossover: {latest_signal['price']:.4f}")
    if latest_signal['adx_value']:
        print(f"  - ADX at Crossover: {latest_signal['adx_value']:.2f}")
```

### Interpreting the Signal
The `get_latest_crossover()` method returns a dictionary with the following information if a valid crossover is found within the lookback period:

-   `type`: `'BULLISH'` or `'BEARISH'`.
-   `index`: The timestamp or index where the crossover occurred.
-   `price`: The closing price at the time of the crossover.
-   `adx_value`: The ADX value at the time of the crossover (if the volatility filter is enabled).

If no valid crossover is found, the method returns `None`.

## 3. Example Implementation

Here is a complete example of how to use the system to find DMI and Stochastic crossovers for EUR/USD data.

```python
import pandas as pd
from backend.indicators import ADX, Stochastic_Oscillator

# --- 1. Load Your Data ---
# eurusd_data = load_your_ohlc_data()

# --- 2. Configure and Initialize Indicators ---
crossover_config = {
    "lookback_period": 10,
    "adx_threshold": 20
}

adx_indicator = ADX(adx_period=14, crossover_settings=crossover_config)
stoch_indicator = Stochastic_Oscillator(
    k_period=14,
    crossover_settings=crossover_config,
    adx_indicator=adx_indicator
)

# --- 3. Calculate Indicators ---
# It's crucial to calculate ADX first
adx_results = adx_indicator.calculate(eurusd_data)
stoch_results = stoch_indicator.calculate(eurusd_data)

# --- 4. Check for Crossovers ---
dmi_signal = adx_indicator.get_latest_crossover()
stoch_signal = stoch_indicator.get_latest_crossover()

if dmi_signal:
    print(f"DMI Crossover: {dmi_signal['type']} at {dmi_signal['price']:.5f} (ADX: {dmi_signal['adx_value']:.2f})")

if stoch_signal:
    print(f"Stochastic Crossover: {stoch_signal['type']} at {stoch_signal['price']:.5f} (ADX: {stoch_signal['adx_value']:.2f})")

```
This system provides a robust and flexible way to generate and validate trading signals, helping you focus on crossovers that occur in favorable market conditions.
