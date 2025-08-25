"""
Strategy Module for Finance Trade Assistant

This module contains trading strategy implementations and calculations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utility.indicators_oscillators import Oscillator
import pandas as pd

def calculate_strategy_signals(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate trading strategy signals for given data."""
    strategy_data = data.copy()
    
    # Initialize oscillator
    oscillator = Oscillator(strategy_data)
    
    # Calculate stochastic values
    stoch_data = oscillator.stochastic_k_14_3_3()
    strategy_data['%K'] = stoch_data['%K']
    strategy_data['%D'] = stoch_data['%D']
    
    # Calculate DMI and ADX values
    dmi_values = oscillator.calculate_dmi()
    strategy_data['DMI'] = dmi_values
    adx_values = oscillator.adx_14()
    strategy_data['ADX'] = adx_values
    
    # For now, create placeholder DI values (these would need proper implementation)
    # Using DMI as a proxy since the original +DI/-DI methods don't exist
    strategy_data['+DI'] = strategy_data['DMI'].where(strategy_data['DMI'] > 0, 0)
    strategy_data['-DI'] = abs(strategy_data['DMI'].where(strategy_data['DMI'] < 0, 0))
    
    # Calculate DI crossover signals
    strategy_data['di_buy'] = (strategy_data['+DI'].shift(1) < strategy_data['-DI'].shift(1)) & (strategy_data['+DI'] > strategy_data['-DI'])
    strategy_data['di_sell'] = (strategy_data['+DI'].shift(1) > strategy_data['-DI'].shift(1)) & (strategy_data['+DI'] < strategy_data['-DI'])
    
    # Calculate stochastic crossover signals
    strategy_data['stoc_buy'] = (strategy_data['%K'].shift(1) < strategy_data['%D'].shift(1)) & (strategy_data['%K'] > strategy_data['%D'])
    strategy_data['stoc_sell'] = (strategy_data['%K'].shift(1) > strategy_data['%D'].shift(1)) & (strategy_data['%K'] < strategy_data['%D'])
    
    return strategy_data

# Example usage - commented out to prevent execution on import
# if __name__ == "__main__":
#     # This would be used when running strategy.py directly
#     pass
