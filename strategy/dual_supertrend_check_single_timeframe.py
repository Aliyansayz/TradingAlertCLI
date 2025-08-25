#!/usr/bin/env python3
"""
Dual Supertrend Strategy Implementation

This module contains the "dual-supertrend-check-single-timeframe" strategy implementation
that uses two different Supertrend indicators with different parameters to generate
buy/sell signals when both align in the same direction.

Strategy: dual-supertrend-check-single-timeframe
- Uses two Supertrend indicators with different periods and multipliers
- Generates buy signals when both Supertrends turn bullish
- Generates sell signals when both Supertrends turn bearish
- Includes RSI, ATR bands for additional confirmation and risk management
- Provides comprehensive technical analysis results with symbol group support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime

from utility.indicators_oscillators import Oscillator, Oscillator_Status


class DualSupertrendSingleTimeframeStrategy:
    """
    Dual Supertrend strategy for single timeframe technical analysis.
    
    This strategy uses two Supertrend indicators with different parameters:
    - Supertrend A: Period=15, Multiplier=3.142 (longer-term trend)
    - Supertrend B: Period=6, Multiplier=0.66 (shorter-term trend)
    
    Buy signals are generated when both Supertrends turn bullish (direction = 1)
    Sell signals are generated when both Supertrends turn bearish (direction = -1)
    """
    
    # Strategy parameter template - configurable settings
    STRATEGY_PARAMETERS_TEMPLATE = {
        "supertrend_a_period": {
            "name": "Supertrend A Period",
            "description": "Period for longer-term Supertrend indicator",
            "type": "int",
            "default": 15,
            "min": 5,
            "max": 50,
            "category": "Supertrend A"
        },
        "supertrend_a_multiplier": {
            "name": "Supertrend A Multiplier",
            "description": "ATR multiplier for longer-term Supertrend",
            "type": "float",
            "default": 3.142,
            "min": 0.5,
            "max": 10.0,
            "step": 0.1,
            "category": "Supertrend A"
        },
        "supertrend_b_period": {
            "name": "Supertrend B Period", 
            "description": "Period for shorter-term Supertrend indicator",
            "type": "int",
            "default": 6,
            "min": 3,
            "max": 30,
            "category": "Supertrend B"
        },
        "supertrend_b_multiplier": {
            "name": "Supertrend B Multiplier",
            "description": "ATR multiplier for shorter-term Supertrend",
            "type": "float",
            "default": 0.66,
            "min": 0.1,
            "max": 5.0,
            "step": 0.01,
            "category": "Supertrend B"
        },
        "confirmation_threshold": {
            "name": "Buy Confirmation Threshold",
            "description": "Minimum confirmations needed for buy signal",
            "type": "int",
            "default": 3,
            "min": 1,
            "max": 5,
            "category": "Signal Generation"
        },
        "exit_threshold": {
            "name": "Exit Confirmation Threshold",
            "description": "Minimum confirmations needed for exit signal",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 4,
            "category": "Signal Generation"
        },
        "atr_stop_multiplier": {
            "name": "ATR Stop Loss Multiplier",
            "description": "ATR multiplier for stop loss calculation",
            "type": "float",
            "default": 2.0,
            "min": 0.5,
            "max": 5.0,
            "step": 0.1,
            "category": "Risk Management"
        },
        "atr_target_multiplier": {
            "name": "ATR Take Profit Multiplier",
            "description": "ATR multiplier for take profit calculation",
            "type": "float",
            "default": 3.0,
            "min": 1.0,
            "max": 10.0,
            "step": 0.1,
            "category": "Risk Management"
        },
        "rsi_overbought": {
            "name": "RSI Overbought Level",
            "description": "RSI level considered overbought",
            "type": "float",
            "default": 70.0,
            "min": 60.0,
            "max": 90.0,
            "step": 1.0,
            "category": "Confirmation Indicators"
        },
        "rsi_oversold": {
            "name": "RSI Oversold Level",
            "description": "RSI level considered oversold",
            "type": "float",
            "default": 30.0,
            "min": 10.0,
            "max": 40.0,
            "step": 1.0,
            "category": "Confirmation Indicators"
        },
        "trend_strength_threshold": {
            "name": "Trend Strength Threshold (ADX)",
            "description": "ADX level considered strong trend",
            "type": "float",
            "default": 25.0,
            "min": 15.0,
            "max": 40.0,
            "step": 1.0,
            "category": "Confirmation Indicators"
        }
    }
    
    def __init__(self, custom_parameters=None):
        self.strategy_name = "dual-supertrend-check-single-timeframe"
        self.strategy_description = "Dual Supertrend crossover strategy with RSI and ATR bands"
        
        # Load default parameters
        self.parameters = {}
        for param_key, param_config in self.STRATEGY_PARAMETERS_TEMPLATE.items():
            self.parameters[param_key] = param_config["default"]
        
        # Override with custom parameters if provided
        if custom_parameters:
            for param_key, param_value in custom_parameters.items():
                if param_key in self.parameters:
                    self.parameters[param_key] = param_value
        
        # Set individual parameter variables for easy access
        self.supertrend_a_period = self.parameters["supertrend_a_period"]
        self.supertrend_a_multiplier = self.parameters["supertrend_a_multiplier"]
        self.supertrend_b_period = self.parameters["supertrend_b_period"]
        self.supertrend_b_multiplier = self.parameters["supertrend_b_multiplier"]
        self.confirmation_threshold = self.parameters["confirmation_threshold"]
        self.exit_threshold = self.parameters["exit_threshold"]
        self.atr_stop_multiplier = self.parameters["atr_stop_multiplier"]
        self.atr_target_multiplier = self.parameters["atr_target_multiplier"]
        self.rsi_overbought = self.parameters["rsi_overbought"]
        self.rsi_oversold = self.parameters["rsi_oversold"]
        self.trend_strength_threshold = self.parameters["trend_strength_threshold"]
        
    def analyze_symbol_data(self, data: pd.DataFrame, symbol_key: str, config) -> Dict[str, Any]:
        """
        Perform dual supertrend analysis on symbol data.
        
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
            
            # Calculate Supertrend indicators
            supertrend_signals = self._calculate_supertrend_signals(data, symbol_key)
            
            # Calculate ATR-based risk management levels
            atr_bands = self._calculate_atr_bands(data, latest_price, symbol_key)
            
            # Apply baseline technical indicators (RSI, etc.)
            indicators, oscillator_status = self._calculate_baseline_indicators(data, symbol_key)
            
            # Generate trading signals
            trading_signals = self._generate_trading_signals(supertrend_signals, indicators, symbol_key)
            
            # Calculate signals summary including supertrend signals
            signals_summary = self._calculate_signals_summary(oscillator_status, trading_signals)
            
            # Determine overall market sentiment
            overall_sentiment = self._determine_overall_sentiment(signals_summary, trading_signals)
            
            return {
                'success': True,
                'latest_price': latest_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'last_7_prices': last_7_prices,
                'supertrend_signals': supertrend_signals,
                'trading_signals': trading_signals,
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
                'error_message': f"Dual Supertrend strategy analysis failed: {str(e)}",
                'strategy_used': self.strategy_name
            }
    
    def _calculate_supertrend_signals(self, data: pd.DataFrame, symbol_key: str) -> Dict[str, Any]:
        """
        Calculate Supertrend indicators and signals.
        
        Args:
            data: OHLCV price data
            symbol_key: Symbol identifier for error logging
            
        Returns:
            Dictionary with Supertrend signals and values
        """
        try:
            # Calculate Supertrend A (longer-term)
            supertrend_a, direction_a = self._supertrend_pandas(
                data['high'], data['low'], data['close'],
                self.supertrend_a_period, self.supertrend_a_multiplier
            )
            
            # Calculate Supertrend B (shorter-term)
            supertrend_b, direction_b = self._supertrend_pandas(
                data['high'], data['low'], data['close'],
                self.supertrend_b_period, self.supertrend_b_multiplier
            )
            
            # Generate entry and exit signals
            entries = (direction_a == 1) & (direction_b == 1)
            exits = (direction_a == -1) | (direction_b == -1)
            
            # Detect crossovers for signal generation
            direction_a_prev = direction_a.shift(1)
            direction_b_prev = direction_b.shift(1)
            
            # Buy signal: both turn bullish
            buy_signals = ((direction_a == 1) & (direction_a_prev != 1)) | \
                         ((direction_b == 1) & (direction_b_prev != 1)) & \
                         (direction_a == 1) & (direction_b == 1)
            
            # Sell signal: either turns bearish
            sell_signals = ((direction_a == -1) & (direction_a_prev != -1)) | \
                          ((direction_b == -1) & (direction_b_prev != -1))
            
            return {
                'supertrend_a': supertrend_a,
                'direction_a': direction_a,
                'supertrend_b': supertrend_b,
                'direction_b': direction_b,
                'entries': entries,
                'exits': exits,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'latest_supertrend_a': supertrend_a.iloc[-1],
                'latest_direction_a': direction_a.iloc[-1],
                'latest_supertrend_b': supertrend_b.iloc[-1],
                'latest_direction_b': direction_b.iloc[-1],
                'current_entry_signal': entries.iloc[-1],
                'current_exit_signal': exits.iloc[-1],
                'current_buy_signal': buy_signals.iloc[-1],
                'current_sell_signal': sell_signals.iloc[-1]
            }
            
        except Exception as e:
            print(f"Error calculating Supertrend signals for {symbol_key}: {str(e)}")
            return {}
    
    def _supertrend_pandas(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                          period: int, multiplier: float) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Supertrend indicator using pandas.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
            multiplier: Multiplier for ATR
            
        Returns:
            Tuple of (supertrend, direction) series
        """
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
            atr_21 = true_range.rolling(window=21).mean().iloc[-1]
            
            # ATR-based bands (using configurable multipliers)
            return {
                'atr_14': atr_14,
                'atr_21': atr_21,
                'upper_band_1.5x': latest_price + (atr_14 * 1.5),
                'lower_band_1.5x': latest_price - (atr_14 * 1.5),
                'upper_band_2x': latest_price + (atr_14 * 2.0),
                'lower_band_2x': latest_price - (atr_14 * 2.0),
                'upper_band_3x': latest_price + (atr_21 * 3.0),
                'lower_band_3x': latest_price - (atr_21 * 3.0),
                'stop_loss_long': latest_price - (atr_14 * self.atr_stop_multiplier),
                'take_profit_long': latest_price + (atr_21 * self.atr_target_multiplier),
                'stop_loss_short': latest_price + (atr_14 * self.atr_stop_multiplier),
                'take_profit_short': latest_price - (atr_21 * self.atr_target_multiplier)
            }
        except Exception as e:
            print(f"Error calculating ATR bands for {symbol_key}: {str(e)}")
            return {}
    
    def _calculate_baseline_indicators(self, data: pd.DataFrame, symbol_key: str) -> Tuple[Dict[str, float], Dict[str, Dict[str, Any]]]:
        """
        Calculate baseline technical indicators (RSI, etc.) for confirmation.
        
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
            # RSI (Relative Strength Index) - primary confirmation indicator
            rsi = oscillator.rsi_14()
            indicators['RSI_14'] = rsi.iloc[-1]
            oscillator_status['RSI_14'] = {
                'value': rsi.iloc[-1],
                'status': Oscillator_Status.get_status(rsi.iloc[-1], 'RSI_14'),
                'previous_value': rsi.iloc[-2] if len(rsi) > 1 else None
            }
            
            # MACD for trend confirmation
            macd_data = oscillator.macd_12_26()
            indicators['MACD'] = macd_data['MACD'].iloc[-1]
            indicators['MACD_Signal'] = macd_data['Signal_Line'].iloc[-1]
            oscillator_status['MACD'] = {
                'value': macd_data['MACD'].iloc[-1],
                'status': Oscillator_Status.get_status(macd_data['MACD'].iloc[-1], 'MACD'),
                'previous_value': macd_data['MACD'].iloc[-2] if len(macd_data) > 1 else None
            }
            
            # ADX for trend strength
            adx = oscillator.adx_14()
            indicators['ADX_14'] = adx.iloc[-1]
            oscillator_status['ADX_14'] = {
                'value': adx.iloc[-1],
                'status': 'Strong Trend' if adx.iloc[-1] > 25 else 'Weak Trend',
                'previous_value': adx.iloc[-2] if len(adx) > 1 else None
            }
            
            # Stochastic for momentum
            stoch_data = oscillator.stochastic_k_14_3_3()
            indicators['Stoch_K'] = stoch_data['%K'].iloc[-1]
            indicators['Stoch_D'] = stoch_data['%D'].iloc[-1]
            oscillator_status['Stochastic_K'] = {
                'value': stoch_data['%K'].iloc[-1],
                'status': Oscillator_Status.get_status(stoch_data['%K'].iloc[-1], '%K'),
                'previous_value': stoch_data['%K'].iloc[-2] if len(stoch_data) > 1 else None
            }
            
        except Exception as e:
            print(f"Error calculating baseline indicators for {symbol_key}: {str(e)}")
        
        return indicators, oscillator_status
    
    def _generate_trading_signals(self, supertrend_signals: Dict[str, Any], 
                                indicators: Dict[str, float], symbol_key: str) -> Dict[str, Any]:
        """
        Generate final trading signals combining Supertrend and baseline indicators.
        
        Args:
            supertrend_signals: Supertrend calculation results
            indicators: Baseline indicator values
            symbol_key: Symbol identifier for error logging
            
        Returns:
            Dictionary with trading signals and recommendations
        """
        try:
            # Current Supertrend directions
            direction_a = supertrend_signals.get('latest_direction_a', 0)
            direction_b = supertrend_signals.get('latest_direction_b', 0)
            
            # RSI confirmation
            rsi = indicators.get('RSI_14', 50)
            macd = indicators.get('MACD', 0)
            adx = indicators.get('ADX_14', 0)
            
            # Main Supertrend signals
            both_bullish = (direction_a == 1) and (direction_b == 1)
            either_bearish = (direction_a == -1) or (direction_b == -1)
            
            # Signal strength based on confirmations
            buy_confirmations = 0
            sell_confirmations = 0
            
            if both_bullish:
                buy_confirmations += 2  # Strong signal from both Supertrends
                if rsi < self.rsi_overbought:  # Not overbought (configurable)
                    buy_confirmations += 1
                if macd > 0:  # MACD bullish
                    buy_confirmations += 1
                if adx > self.trend_strength_threshold:  # Strong trend (configurable)
                    buy_confirmations += 1
            
            if either_bearish:
                sell_confirmations += 1 if direction_a == -1 else 0
                sell_confirmations += 1 if direction_b == -1 else 0
                if rsi > self.rsi_oversold:  # Not oversold (configurable)
                    sell_confirmations += 1
                if macd < 0:  # MACD bearish
                    sell_confirmations += 1
                if adx > self.trend_strength_threshold:  # Strong trend (configurable)
                    sell_confirmations += 1
            
            # Determine signal strength using configurable thresholds
            if buy_confirmations >= (self.confirmation_threshold + 1):
                signal_strength = "STRONG_BUY"
            elif buy_confirmations >= self.confirmation_threshold:
                signal_strength = "BUY"
            elif sell_confirmations >= (self.exit_threshold + 2):
                signal_strength = "STRONG_SELL"
            elif sell_confirmations >= self.exit_threshold:
                signal_strength = "SELL"
            else:
                signal_strength = "NEUTRAL"
            
            return {
                'signal_strength': signal_strength,
                'buy_confirmations': buy_confirmations,
                'sell_confirmations': sell_confirmations,
                'both_supertrends_bullish': both_bullish,
                'either_supertrend_bearish': either_bearish,
                'supertrend_a_bullish': direction_a == 1,
                'supertrend_b_bullish': direction_b == 1,
                'rsi_confirmation': rsi,
                'macd_confirmation': macd,
                'trend_strength': adx,
                'entry_recommended': buy_confirmations >= self.confirmation_threshold,
                'exit_recommended': sell_confirmations >= self.exit_threshold
            }
            
        except Exception as e:
            print(f"Error generating trading signals for {symbol_key}: {str(e)}")
            return {'signal_strength': 'NEUTRAL', 'error': str(e)}
    
    def _calculate_signals_summary(self, oscillator_status: Dict[str, Dict[str, Any]], 
                                 trading_signals: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate summary of buy/sell/neutral signals including Supertrend signals.
        
        Args:
            oscillator_status: Dictionary of oscillator status data
            trading_signals: Trading signals from Supertrend analysis
            
        Returns:
            Dictionary with signal counts
        """
        signals_summary = {"Buy": 0, "Sell": 0, "Neutral": 0}
        
        # Count oscillator signals
        for status_data in oscillator_status.values():
            status = status_data.get('status', 'Neutral')
            if 'Buy' in status or 'Bullish' in status:
                signals_summary["Buy"] += 1
            elif 'Sell' in status or 'Bearish' in status:
                signals_summary["Sell"] += 1
            else:
                signals_summary["Neutral"] += 1
        
        # Add Supertrend signal weight
        signal_strength = trading_signals.get('signal_strength', 'NEUTRAL')
        if 'BUY' in signal_strength:
            signals_summary["Buy"] += 2  # Supertrend gets double weight
        elif 'SELL' in signal_strength:
            signals_summary["Sell"] += 2  # Supertrend gets double weight
        else:
            signals_summary["Neutral"] += 1
        
        return signals_summary
    
    def _determine_overall_sentiment(self, signals_summary: Dict[str, int], 
                                   trading_signals: Dict[str, Any]) -> str:
        """
        Determine overall market sentiment with Supertrend priority.
        
        Args:
            signals_summary: Dictionary with buy/sell/neutral signal counts
            trading_signals: Trading signals from Supertrend analysis
            
        Returns:
            Overall sentiment string (BULLISH/BEARISH/NEUTRAL)
        """
        signal_strength = trading_signals.get('signal_strength', 'NEUTRAL')
        
        # Supertrend gets priority in sentiment determination
        if signal_strength in ['STRONG_BUY', 'BUY']:
            return "BULLISH"
        elif signal_strength in ['STRONG_SELL', 'SELL']:
            return "BEARISH"
        else:
            # Fall back to oscillator consensus
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
            'primary_indicators': [
                f'Supertrend_A(period={self.supertrend_a_period}, multiplier={self.supertrend_a_multiplier})',
                f'Supertrend_B(period={self.supertrend_b_period}, multiplier={self.supertrend_b_multiplier})'
            ],
            'confirmation_indicators': ['RSI_14', 'MACD', 'ADX_14', 'Stochastic_K'],
            'risk_management': ['ATR_bands', 'stop_loss', 'take_profit'],
            'signal_generation': 'Both Supertrends must align for entry signals',
            'configurable_parameters': len(self.STRATEGY_PARAMETERS_TEMPLATE),
            'version': '1.1'
        }
    
    def get_parameters_template(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the strategy parameters template for configuration UI.
        
        Returns:
            Dictionary with parameter definitions
        """
        return self.STRATEGY_PARAMETERS_TEMPLATE.copy()
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """
        Get current parameter values.
        
        Returns:
            Dictionary with current parameter values
        """
        return self.parameters.copy()
    
    def update_parameters(self, new_parameters: Dict[str, Any]) -> bool:
        """
        Update strategy parameters.
        
        Args:
            new_parameters: Dictionary with new parameter values
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Validate parameters against template
            for param_key, param_value in new_parameters.items():
                if param_key not in self.STRATEGY_PARAMETERS_TEMPLATE:
                    print(f"Warning: Unknown parameter '{param_key}' ignored")
                    continue
                
                template = self.STRATEGY_PARAMETERS_TEMPLATE[param_key]
                
                # Type validation
                if template["type"] == "int":
                    param_value = int(param_value)
                    if param_value < template.get("min", float('-inf')) or param_value > template.get("max", float('inf')):
                        print(f"Warning: Parameter '{param_key}' value {param_value} outside valid range")
                        continue
                elif template["type"] == "float":
                    param_value = float(param_value)
                    if param_value < template.get("min", float('-inf')) or param_value > template.get("max", float('inf')):
                        print(f"Warning: Parameter '{param_key}' value {param_value} outside valid range")
                        continue
                
                # Update parameter
                self.parameters[param_key] = param_value
            
            # Update individual parameter variables
            self.supertrend_a_period = self.parameters["supertrend_a_period"]
            self.supertrend_a_multiplier = self.parameters["supertrend_a_multiplier"]
            self.supertrend_b_period = self.parameters["supertrend_b_period"]
            self.supertrend_b_multiplier = self.parameters["supertrend_b_multiplier"]
            self.confirmation_threshold = self.parameters["confirmation_threshold"]
            self.exit_threshold = self.parameters["exit_threshold"]
            self.atr_stop_multiplier = self.parameters["atr_stop_multiplier"]
            self.atr_target_multiplier = self.parameters["atr_target_multiplier"]
            self.rsi_overbought = self.parameters["rsi_overbought"]
            self.rsi_oversold = self.parameters["rsi_oversold"]
            self.trend_strength_threshold = self.parameters["trend_strength_threshold"]
            
            return True
            
        except Exception as e:
            print(f"Error updating parameters: {str(e)}")
            return False
    
    def reset_parameters_to_default(self):
        """Reset all parameters to their default values."""
        for param_key, param_config in self.STRATEGY_PARAMETERS_TEMPLATE.items():
            self.parameters[param_key] = param_config["default"]
        
        # Update individual parameter variables
        self.supertrend_a_period = self.parameters["supertrend_a_period"]
        self.supertrend_a_multiplier = self.parameters["supertrend_a_multiplier"]
        self.supertrend_b_period = self.parameters["supertrend_b_period"]
        self.supertrend_b_multiplier = self.parameters["supertrend_b_multiplier"]
        self.confirmation_threshold = self.parameters["confirmation_threshold"]
        self.exit_threshold = self.parameters["exit_threshold"]
        self.atr_stop_multiplier = self.parameters["atr_stop_multiplier"]
        self.atr_target_multiplier = self.parameters["atr_target_multiplier"]
        self.rsi_overbought = self.parameters["rsi_overbought"]
        self.rsi_oversold = self.parameters["rsi_oversold"]
        self.trend_strength_threshold = self.parameters["trend_strength_threshold"]


# Factory function to create strategy instance
def create_dual_supertrend_strategy(custom_parameters=None) -> DualSupertrendSingleTimeframeStrategy:
    """
    Factory function to create a dual supertrend strategy instance.
    
    Args:
        custom_parameters: Optional dictionary with custom parameter values
    
    Returns:
        DualSupertrendSingleTimeframeStrategy instance
    """
    return DualSupertrendSingleTimeframeStrategy(custom_parameters)


if __name__ == "__main__":
    # Example usage and testing
    strategy = create_dual_supertrend_strategy()
    info = strategy.get_strategy_info()
    
    print(f"Strategy: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"Type: {info['type']}")
    print(f"Primary Indicators: {', '.join(info['primary_indicators'])}")
    print(f"Confirmation Indicators: {', '.join(info['confirmation_indicators'])}")
    print(f"Risk Management: {', '.join(info['risk_management'])}")
    print(f"Signal Generation: {info['signal_generation']}")
