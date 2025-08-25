#!/usr/bin/env python3
"""
Default Trading Strategy Implementation

This module contains the default "single-timeframe-check" strategy implementation
that performs technical analysis on a single timeframe to determine trading signals.

Strategy: default-check-single-timeframe
- Analyzes technical indicators on a single timeframe
- Calculates oscillator signals
- Determines overall sentiment based on indicator consensus
- Provides comprehensive technical analysis results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime

from utility.indicators_oscillators import Oscillator, Oscillator_Status


class DefaultSingleTimeframeStrategy:
    """
    Default strategy for single timeframe technical analysis.
    
    This strategy implements the core analysis logic that was previously
    embedded in the SymbolAnalyzer class. It performs comprehensive
    technical analysis using multiple oscillators and indicators.
    """
    
    # Strategy parameter template - for default strategy, parameters come from indicator settings
    STRATEGY_PARAMETERS_TEMPLATE = {
        "note": {
            "name": "Default Strategy Note",
            "description": "This strategy uses global indicator settings. No custom parameters available.",
            "type": "info",
            "default": "Uses indicator settings from main configuration",
            "category": "Information"
        }
    }
    
    def __init__(self, custom_parameters=None):
        self.strategy_name = "default-check-single-timeframe"
        self.strategy_description = "Single timeframe technical analysis with multiple oscillators"
        
        # Default strategy doesn't use custom parameters - uses indicator settings instead
        self.parameters = {"note": "Uses global indicator settings"}
    
    def get_parameters_template(self) -> Dict[str, Dict[str, Any]]:
        """Get the strategy parameters template - empty for default strategy."""
        return self.STRATEGY_PARAMETERS_TEMPLATE.copy()
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current parameter values - empty for default strategy."""
        return self.parameters.copy()
    
    def update_parameters(self, new_parameters: Dict[str, Any]) -> bool:
        """Update strategy parameters - no-op for default strategy."""
        return True  # Always return success since no parameters to update
    
    def reset_parameters_to_default(self):
        """Reset parameters - no-op for default strategy."""
        pass
        
    def analyze_symbol_data(self, data: pd.DataFrame, symbol_key: str, config) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis on symbol data.
        
        Args:
            data: OHLCV price data
            symbol_key: Unique identifier for the symbol
            config: Symbol configuration containing timeframe, period etc.
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Basic price analysis
            latest_price = data['close'].iloc[-1]
            price_change = data['close'].iloc[-1] - data['close'].iloc[0]
            price_change_pct = (price_change / data['close'].iloc[0]) * 100
            
            # Get last 7 prices for trend analysis
            last_7_prices = data['close'].tail(7).tolist()
            
            # Calculate ATR-based risk management levels
            atr_bands = self._calculate_atr_bands(data, latest_price, symbol_key)
            
            # Apply technical indicators and oscillators
            indicators, oscillator_status = self._calculate_technical_indicators(data, symbol_key)
            
            # Calculate trading signals summary
            signals_summary = self._calculate_signals_summary(oscillator_status)
            
            # Determine overall market sentiment
            overall_sentiment = self._determine_overall_sentiment(signals_summary)
            
            return {
                'success': True,
                'latest_price': latest_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'last_7_prices': last_7_prices,
                'indicators': indicators,
                'oscillator_status': oscillator_status,
                'signals_summary': signals_summary,
                'overall_sentiment': overall_sentiment,
                'atr_bands': atr_bands,
                'strategy_used': self.strategy_name,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': f"Strategy analysis failed: {str(e)}",
                'strategy_used': self.strategy_name
            }
    
    def _calculate_atr_bands(self, data: pd.DataFrame, latest_price: float, symbol_key: str) -> Dict[str, float]:
        """
        Calculate ATR-based stop loss and take profit levels.
        
        Args:
            data: OHLCV price data
            latest_price: Current price
            symbol_key: Symbol identifier for error logging
            
        Returns:
            Dictionary with ATR bands and risk management levels
        """
        try:
            # Calculate ATR (Average True Range)
            high_low = data['high'] - data['low']
            high_close_prev = abs(data['high'] - data['close'].shift(1))
            low_close_prev = abs(data['low'] - data['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            atr_14 = true_range.rolling(window=14).mean().iloc[-1]
            
            # ATR-based bands (using 1.5x and 2x multipliers)
            return {
                'atr_value': atr_14,
                'upper_band_1.5x': latest_price + (atr_14 * 1.5),
                'lower_band_1.5x': latest_price - (atr_14 * 1.5),
                'upper_band_2x': latest_price + (atr_14 * 2.0),
                'lower_band_2x': latest_price - (atr_14 * 2.0),
                'stop_loss_long': latest_price - (atr_14 * 1.5),  # For long positions
                'take_profit_long': latest_price + (atr_14 * 2.0),  # For long positions
                'stop_loss_short': latest_price + (atr_14 * 1.5),  # For short positions
                'take_profit_short': latest_price - (atr_14 * 2.0)  # For short positions
            }
        except Exception as e:
            print(f"Error calculating ATR bands for {symbol_key}: {str(e)}")
            return {}
    
    def _calculate_technical_indicators(self, data: pd.DataFrame, symbol_key: str) -> Tuple[Dict[str, float], Dict[str, Dict[str, Any]]]:
        """
        Calculate technical indicators and oscillator signals.
        
        Args:
            data: OHLCV price data
            symbol_key: Symbol identifier for error logging
            
        Returns:
            Tuple of (indicators_dict, oscillator_status_dict)
        """
        oscillator = Oscillator(data)
        indicators = {}
        oscillator_status = {}
        
        try:
            # RSI (Relative Strength Index)
            rsi = oscillator.rsi_14()
            indicators['RSI_14'] = rsi.iloc[-1]
            oscillator_status['RSI_14'] = {
                'value': rsi.iloc[-1],
                'status': Oscillator_Status.get_status(rsi.iloc[-1], 'RSI_14'),
                'previous_value': rsi.iloc[-2] if len(rsi) > 1 else None
            }
            
            # Stochastic Oscillator
            stoch_data = oscillator.stochastic_k_14_3_3()
            indicators['Stoch_K'] = stoch_data['%K'].iloc[-1]
            indicators['Stoch_D'] = stoch_data['%D'].iloc[-1]
            oscillator_status['Stochastic_K'] = {
                'value': stoch_data['%K'].iloc[-1],
                'status': Oscillator_Status.get_status(stoch_data['%K'].iloc[-1], '%K'),
                'previous_value': stoch_data['%K'].iloc[-2] if len(stoch_data) > 1 else None
            }
            
            # CCI (Commodity Channel Index)
            cci = oscillator.cci_20()
            indicators['CCI_20'] = cci.iloc[-1]
            oscillator_status['CCI_20'] = {
                'value': cci.iloc[-1],
                'status': Oscillator_Status.get_status(cci.iloc[-1], 'CCI_20'),
                'previous_value': cci.iloc[-2] if len(cci) > 1 else None
            }
            
            # MACD (Moving Average Convergence Divergence)
            macd_data = oscillator.macd_12_26()
            indicators['MACD'] = macd_data['MACD'].iloc[-1]
            indicators['MACD_Signal'] = macd_data['Signal_Line'].iloc[-1]
            oscillator_status['MACD'] = {
                'value': macd_data['MACD'].iloc[-1],
                'status': Oscillator_Status.get_status(macd_data['MACD'].iloc[-1], 'MACD'),
                'previous_value': macd_data['MACD'].iloc[-2] if len(macd_data) > 1 else None
            }
            
            # Williams %R
            williams_r = oscillator.williams_percent_r()
            indicators['Williams_R'] = williams_r.iloc[-1]
            oscillator_status['Williams_R'] = {
                'value': williams_r.iloc[-1],
                'status': Oscillator_Status.get_status(williams_r.iloc[-1], '%R'),
                'previous_value': williams_r.iloc[-2] if len(williams_r) > 1 else None
            }
            
            # Bull/Bear Power
            bull_bear = oscillator.bull_bear_power()
            indicators['Bull_Power'] = bull_bear['Bull_Power'].iloc[-1]
            indicators['Bear_Power'] = bull_bear['Bear_Power'].iloc[-1]
            oscillator_status['Bull_Power'] = {
                'value': bull_bear['Bull_Power'].iloc[-1],
                'status': Oscillator_Status.get_status(bull_bear['Bull_Power'].iloc[-1], 'Bull_Power'),
                'previous_value': bull_bear['Bull_Power'].iloc[-2] if len(bull_bear) > 1 else None
            }
            oscillator_status['Bear_Power'] = {
                'value': bull_bear['Bear_Power'].iloc[-1],
                'status': Oscillator_Status.get_status(bull_bear['Bear_Power'].iloc[-1], 'Bear_Power'),
                'previous_value': bull_bear['Bear_Power'].iloc[-2] if len(bull_bear) > 1 else None
            }
            
            # DMI (Directional Movement Index)
            dmi = oscillator.calculate_dmi()
            indicators['DMI'] = dmi.iloc[-1]
            if len(data) >= 2:
                dmi_data = pd.DataFrame({'DMI': dmi}).tail(2)
                dmi_status = Oscillator_Status.dmi_status(dmi_data)
                oscillator_status['DMI'] = {
                    'value': dmi.iloc[-1],
                    'status': dmi_status,
                    'previous_value': dmi.iloc[-2] if len(dmi) > 1 else None
                }
                
        except Exception as e:
            print(f"Error calculating technical indicators for {symbol_key}: {str(e)}")
        
        return indicators, oscillator_status
    
    def _calculate_signals_summary(self, oscillator_status: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate summary of buy/sell/neutral signals from oscillators.
        
        Args:
            oscillator_status: Dictionary of oscillator status data
            
        Returns:
            Dictionary with signal counts
        """
        signals_summary = {"Buy": 0, "Sell": 0, "Neutral": 0}
        
        for status_data in oscillator_status.values():
            status = status_data.get('status', 'Neutral')
            signals_summary[status] = signals_summary.get(status, 0) + 1
        
        return signals_summary
    
    def _determine_overall_sentiment(self, signals_summary: Dict[str, int]) -> str:
        """
        Determine overall market sentiment based on signal consensus.
        
        Args:
            signals_summary: Dictionary with buy/sell/neutral signal counts
            
        Returns:
            Overall sentiment string (BULLISH/BEARISH/NEUTRAL)
        """
        if signals_summary["Buy"] > signals_summary["Sell"]:
            return "BULLISH"
        elif signals_summary["Sell"] > signals_summary["Buy"]:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def get_strategy_info(self) -> Dict[str, str]:
        """
        Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            'name': self.strategy_name,
            'description': self.strategy_description,
            'type': 'single_timeframe',
            'indicators_used': [
                'RSI_14', 'Stochastic_K', 'Stochastic_D', 'CCI_20', 'MACD',
                'Williams_R', 'Bull_Power', 'Bear_Power', 'DMI'
            ],
            'risk_management': ['ATR_bands', 'stop_loss', 'take_profit'],
            'version': '1.0'
        }


# Factory function to create strategy instance
def create_default_strategy(custom_parameters=None) -> DefaultSingleTimeframeStrategy:
    """
    Factory function to create a default strategy instance.
    
    Args:
        custom_parameters: Optional dictionary (ignored for default strategy)
    
    Returns:
        DefaultSingleTimeframeStrategy instance
    """
    return DefaultSingleTimeframeStrategy(custom_parameters)


# For backward compatibility - now points to centralized registry
def get_strategy(strategy_name: str) -> DefaultSingleTimeframeStrategy:
    """
    Get a strategy instance by name.
    NOTE: This function is deprecated. Use strategy.get_strategy() instead.
    
    Args:
        strategy_name: Name of the strategy to create
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If strategy name is not found
    """
    # Import here to avoid circular imports
    from . import get_strategy as centralized_get_strategy
    return centralized_get_strategy(strategy_name)


if __name__ == "__main__":
    # Example usage and testing
    strategy = create_default_strategy()
    info = strategy.get_strategy_info()
    
    print(f"Strategy: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"Type: {info['type']}")
    print(f"Indicators: {', '.join(info['indicators_used'])}")
    print(f"Risk Management: {', '.join(info['risk_management'])}")
