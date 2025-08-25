
Add a new strategy in CLI App, "dual-supertrend-check-single-timeframe" and it uses baseline indicators rsi, atr bands(especially for stop loss take profits), alongside. Ensure it uses all Symbol Group Features too, 
create a new file inside #file:strategy "dual_supertrend_check_single_timeframe.md"


```

import pandas as pd

def supertrend_pandas(high: pd.Series, low: pd.Series, close: pd.Series, period: int, multiplier: float):
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

    # Initialize series
    direction = pd.Series(1, index=close.index)
    supertrend = pd.Series(0.0, index=close.index)

    # Iterative calculation (stateful logic)
    for i in range(1, len(close)):
        if close.iloc[i] > upperband.iloc[i - 1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lowerband.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        supertrend.iloc[i] = lowerband.iloc[i] if direction.iloc[i] == 1 else upperband.iloc[i]

    return supertrend, direction


# Example usage:
# Calculate two supertrends with different parameters
supertrend_A, direction_A = supertrend_pandas(data_high, data_low, data_close, 15, 3.142)
supertrend_B, direction_B = supertrend_pandas(data_high, data_low, data_close, 6, 0.66)

# Define entry and exit signals
entries = (direction_A == 1) & (direction_B == 1)
exits = (direction_A == -1) | (direction_B == -1)

# Put everything into a dictionary
signals = {
    "Supertrend_A": supertrend_A,
    "Direction_A": direction_A,
    "Supertrend_B": supertrend_B,
    "Direction_B": direction_B,
    "Entries": entries,
    "Exits": exits
}

# Optional: Convert to DataFrame for visualization
signals_df = pd.DataFrame(signals)


```