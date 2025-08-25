"""
Indicator Application Pipeline Module

This module handles the application of technical indicators to financial data.
It provides a unified interface for applying multiple indicators and manages
their calculation lifecycle.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging

# Import all indicator classes from the existing indicators module
from utility.indicators import ADX, Stochastic_Oscillator, ATRBands, SupertrendIndicator, RSI
from utility.indicators_oscillators import Oscillator

class IndicatorPipeline:
    """
    Pipeline for applying technical indicators to OHLC data.
    Manages indicator instances and their calculations.
    """
    
    def __init__(self):
        self.indicators = {}
        self.applied_indicators = {}
        self.logger = logging.getLogger(__name__)
        
    def add_indicator(self, name: str, indicator_class: str, **kwargs) -> bool:
        """
        Add an indicator to the pipeline.
        
        Args:
            name: Unique name for this indicator instance
            indicator_class: The class name of the indicator
            **kwargs: Parameters for the indicator constructor
            
        Returns:
            Boolean indicating success
        """
        try:
            if indicator_class == "ADX":
                self.indicators[name] = ADX(**kwargs)
            elif indicator_class == "Stochastic_Oscillator":
                self.indicators[name] = Stochastic_Oscillator(**kwargs)
            elif indicator_class == "ATRBands":
                self.indicators[name] = ATRBands(**kwargs)
            elif indicator_class == "SupertrendIndicator":
                self.indicators[name] = SupertrendIndicator(**kwargs)
            elif indicator_class == "RSI":
                self.indicators[name] = RSI(**kwargs)
            elif indicator_class == "Oscillator":
                # Note: Oscillator class requires dataframe in constructor
                # Will be handled differently in apply_indicators method
                self.indicators[name] = {"class": "Oscillator", "params": kwargs}
            else:
                self.logger.error(f"Unknown indicator class: {indicator_class}")
                return False
                
            self.logger.info(f"Added indicator {name} ({indicator_class}) to pipeline")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding indicator {name}: {str(e)}")
            return False
    
    def remove_indicator(self, name: str) -> bool:
        """
        Remove an indicator from the pipeline.
        
        Args:
            name: Name of the indicator to remove
            
        Returns:
            Boolean indicating success
        """
        if name in self.indicators:
            del self.indicators[name]
            if name in self.applied_indicators:
                del self.applied_indicators[name]
            self.logger.info(f"Removed indicator {name} from pipeline")
            return True
        return False
    
    def apply_indicators(self, df: pd.DataFrame, indicator_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Apply specified indicators to the dataframe.
        
        Args:
            df: OHLC dataframe
            indicator_names: List of indicator names to apply. If None, applies all.
            
        Returns:
            DataFrame with indicator columns added
        """
        if df.empty:
            self.logger.warning("Empty dataframe provided to apply_indicators")
            return df
            
        # Make a copy to avoid modifying the original
        result_df = df.copy()
        
        # Determine which indicators to apply
        if indicator_names is None:
            indicator_names = list(self.indicators.keys())
        
        for name in indicator_names:
            if name not in self.indicators:
                self.logger.warning(f"Indicator {name} not found in pipeline")
                continue
                
            try:
                indicator = self.indicators[name]
                
                # Handle different indicator types
                if isinstance(indicator, dict) and indicator.get("class") == "Oscillator":
                    # Special handling for Oscillator class
                    result_df = self._apply_oscillator(result_df, name, indicator["params"])
                elif hasattr(indicator, 'calculate'):
                    # Standard indicator with calculate method
                    result_df = self._apply_standard_indicator(result_df, name, indicator)
                else:
                    self.logger.warning(f"Unknown indicator type for {name}")
                    
            except Exception as e:
                self.logger.error(f"Error applying indicator {name}: {str(e)}")
                continue
        
        return result_df
    
    def _apply_standard_indicator(self, df: pd.DataFrame, name: str, indicator) -> pd.DataFrame:
        """Apply a standard indicator with calculate method."""
        try:
            if isinstance(indicator, ADX):
                plus_di, minus_di, adx = indicator.calculate(df)
                df[f'{name}_plus_di'] = plus_di
                df[f'{name}_minus_di'] = minus_di  
                df[f'{name}_adx'] = adx
                
            elif isinstance(indicator, Stochastic_Oscillator):
                k, d = indicator.calculate(df)
                df[f'{name}_k'] = k
                df[f'{name}_d'] = d
                
            elif isinstance(indicator, ATRBands):
                atr, upper, lower = indicator.calculate(df)
                df[f'{name}_atr'] = atr
                df[f'{name}_upper'] = upper
                df[f'{name}_lower'] = lower
                
            elif isinstance(indicator, SupertrendIndicator):
                supertrend, direction = indicator.calculate(df)
                df[f'{name}_supertrend'] = supertrend
                df[f'{name}_direction'] = direction
                
            elif isinstance(indicator, RSI):
                rsi = indicator.calculate(df)
                df[f'{name}_rsi'] = rsi
                
            self.applied_indicators[name] = True
            
        except Exception as e:
            self.logger.error(f"Error in _apply_standard_indicator for {name}: {str(e)}")
            
        return df
    
    def _apply_oscillator(self, df: pd.DataFrame, name: str, params: Dict) -> pd.DataFrame:
        """Apply oscillator indicators."""
        try:
            oscillator = Oscillator(df)
            
            # Apply all oscillator methods based on params
            if params.get('rsi_14', False):
                df[f'{name}_rsi_14'] = oscillator.rsi_14()
                
            if params.get('stochastic', False):
                stoch_data = oscillator.stochastic_k_14_3_3()
                df[f'{name}_stoch_k'] = stoch_data['%K']
                df[f'{name}_stoch_d'] = stoch_data['%D']
                
            if params.get('cci_20', False):
                df[f'{name}_cci_20'] = oscillator.cci_20()
                
            if params.get('adx_14', False):
                df[f'{name}_adx_14'] = oscillator.adx_14()
                
            if params.get('dmi', False):
                df[f'{name}_dmi'] = oscillator.calculate_dmi()
                
            if params.get('awesome_oscillator', False):
                df[f'{name}_ao'] = oscillator.awesome_oscillator()
                
            if params.get('momentum_10', False):
                df[f'{name}_momentum'] = oscillator.momentum_10()
                
            if params.get('macd', False):
                df[f'{name}_macd'] = oscillator.macd_12_26()
                
            self.applied_indicators[name] = True
            
        except Exception as e:
            self.logger.error(f"Error in _apply_oscillator for {name}: {str(e)}")
            
        return df
    
    def get_indicator_list(self) -> List[str]:
        """Get list of available indicators in the pipeline."""
        return list(self.indicators.keys())
    
    def get_applied_indicators(self) -> List[str]:
        """Get list of successfully applied indicators."""
        return [name for name, applied in self.applied_indicators.items() if applied]
    
    def reset_indicators(self):
        """Reset all indicators to initial state."""
        for indicator in self.indicators.values():
            if hasattr(indicator, 'initial_run'):
                indicator.initial_run = True
                indicator.need_recalc = False
        
        self.applied_indicators = {}
        self.logger.info("Reset all indicators to initial state")

class IndicatorManager:
    """
    High-level manager for indicator operations.
    Provides convenience methods for common indicator setups.
    """
    
    def __init__(self):
        self.pipeline = IndicatorPipeline()
        
    def setup_default_indicators(self):
        """Setup a default set of commonly used indicators."""
        # Add ADX with default parameters
        self.pipeline.add_indicator("adx_default", "ADX", adx_period=14)
        
        # Add Stochastic Oscillator
        self.pipeline.add_indicator("stoch_default", "Stochastic_Oscillator", 
                                  k_period=7, k_smooth=3, d_period=3)
        
        # Add RSI
        self.pipeline.add_indicator("rsi_default", "RSI", rsi_period=14)
        
        # Add ATR Bands
        self.pipeline.add_indicator("atr_bands", "ATRBands", 
                                  atr_period=7, atr_multiplier=2.3)
        
        # Add Supertrend
        self.pipeline.add_indicator("supertrend", "SupertrendIndicator", 
                                  period=10, multiplier=3.0)
        
        # Add Oscillator bundle
        self.pipeline.add_indicator("oscillators", "Oscillator", 
                                  rsi_14=True, stochastic=True, cci_20=True)
        
    def setup_forex_indicators(self):
        """Setup indicators optimized for forex trading."""
        # ADX for trend strength
        self.pipeline.add_indicator("adx_forex", "ADX", adx_period=14)
        
        # Stochastic for momentum
        self.pipeline.add_indicator("stoch_forex", "Stochastic_Oscillator", 
                                  k_period=14, k_smooth=3, d_period=3)
        
        # RSI for overbought/oversold
        self.pipeline.add_indicator("rsi_forex", "RSI", rsi_period=14)
        
        # ATR for volatility
        self.pipeline.add_indicator("atr_forex", "ATRBands", 
                                  atr_period=14, atr_multiplier=2.0)
    
    def apply_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all configured indicators to the dataframe."""
        return self.pipeline.apply_indicators(df)

# Legacy compatibility function - preserves original strategy.py functionality
def apply_legacy_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply indicators using the original approach from strategy.py.
    This maintains compatibility with existing code.
    """
    # Preserve original strategy.py code as comments:
    """
    Original strategy.py code:
    
    stoc_indicator = Stochastic_Oscillator()
    adx_indicator = ADX()
    
    eurusd_data['+DI'], eurusd_data['-DI'], eurusd_data['ADX'] = adx_indicator.calculate(eurusd_data)
    
    eurusd_data['di_buy']  = (eurusd_data['+DI'].shift(1) < eurusd_data['-DI'].shift(1)) & (eurusd_data['+DI'] > eurusd_data['-DI'])
    eurusd_data['di_sell'] = (eurusd_data['+DI'].shift(1) > eurusd_data['-DI'].shift(1)) & (eurusd_data['+DI'] < eurusd_data['-DI'])
    
    eurusd_data['%K'], eurusd_data['%D'] = stoc_indicator.calculate(eurusd_data)
    
    eurusd_data['stoc_buy'] = (eurusd_data['%K'].shift(1) < eurusd_data['%D'].shift(1)) & (eurusd_data['%K'] > eurusd_data['%D'])
    eurusd_data['stoc_sell'] = (eurusd_data['%K'].shift(1) > eurusd_data['%D'].shift(1)) & (eurusd_data['%K'] < eurusd_data['%D'])
    """
    
    # Replicate the original logic using the new pipeline
    result_df = df.copy()
    
    # Initialize indicators with original parameters
    stoc_indicator = Stochastic_Oscillator()
    adx_indicator = ADX()
    
    # Apply ADX
    result_df['+DI'], result_df['-DI'], result_df['ADX'] = adx_indicator.calculate(result_df)
    
    # Apply Stochastic
    result_df['%K'], result_df['%D'] = stoc_indicator.calculate(result_df)
    
    # Generate buy/sell signals as in original
    result_df['di_buy'] = (result_df['+DI'].shift(1) < result_df['-DI'].shift(1)) & (result_df['+DI'] > result_df['-DI'])
    result_df['di_sell'] = (result_df['+DI'].shift(1) > result_df['-DI'].shift(1)) & (result_df['+DI'] < result_df['-DI'])
    
    result_df['stoc_buy'] = (result_df['%K'].shift(1) < result_df['%D'].shift(1)) & (result_df['%K'] > result_df['%D'])
    result_df['stoc_sell'] = (result_df['%K'].shift(1) > result_df['%D'].shift(1)) & (result_df['%K'] < result_df['%D'])
    
    return result_df

# Example usage
if __name__ == "__main__":
    # Test the indicator pipeline
    manager = IndicatorManager()
    manager.setup_default_indicators()
    
    print(f"Available indicators: {manager.pipeline.get_indicator_list()}")