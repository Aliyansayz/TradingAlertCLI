"""
Strategy Definition Pipeline Module

This module handles the definition and execution of trading strategies.
It provides a framework for creating complex trading strategies using
multiple indicators and custom logic.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging

class SignalType(Enum):
    """Enumeration for signal types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class ConditionOperator(Enum):
    """Enumeration for condition operators."""
    AND = "and"
    OR = "or"
    NOT = "not"

@dataclass
class TradingSignal:
    """Data class for trading signals."""
    timestamp: pd.Timestamp
    signal_type: SignalType
    strength: float  # Signal strength from 0.0 to 1.0
    indicators_used: List[str]
    metadata: Dict[str, Any] = None

@dataclass
class StrategyCondition:
    """Data class for strategy conditions."""
    name: str
    column1: str
    operator: str  # '>', '<', '>=', '<=', '==', '!=', 'cross_above', 'cross_below'
    column2: Optional[str] = None
    value: Optional[float] = None
    lookback: int = 1  # Number of periods to look back for cross conditions

class StrategyBuilder:
    """
    Builder class for creating trading strategies with multiple conditions.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.buy_conditions = []
        self.sell_conditions = []
        self.buy_operator = ConditionOperator.AND
        self.sell_operator = ConditionOperator.AND
        self.logger = logging.getLogger(__name__)
        
    def add_buy_condition(self, condition: StrategyCondition) -> 'StrategyBuilder':
        """Add a buy condition to the strategy."""
        self.buy_conditions.append(condition)
        return self
        
    def add_sell_condition(self, condition: StrategyCondition) -> 'StrategyBuilder':
        """Add a sell condition to the strategy."""
        self.sell_conditions.append(condition)
        return self
        
    def set_buy_operator(self, operator: ConditionOperator) -> 'StrategyBuilder':
        """Set the logical operator for combining buy conditions."""
        self.buy_operator = operator
        return self
        
    def set_sell_operator(self, operator: ConditionOperator) -> 'StrategyBuilder':
        """Set the logical operator for combining sell conditions."""
        self.sell_operator = operator
        return self
        
    def build(self) -> 'TradingStrategy':
        """Build and return the trading strategy."""
        return TradingStrategy(
            name=self.name,
            buy_conditions=self.buy_conditions,
            sell_conditions=self.sell_conditions,
            buy_operator=self.buy_operator,
            sell_operator=self.sell_operator
        )

class TradingStrategy:
    """
    Trading strategy class that evaluates conditions and generates signals.
    """
    
    def __init__(self, 
                 name: str,
                 buy_conditions: List[StrategyCondition],
                 sell_conditions: List[StrategyCondition],
                 buy_operator: ConditionOperator = ConditionOperator.AND,
                 sell_operator: ConditionOperator = ConditionOperator.AND):
        self.name = name
        self.buy_conditions = buy_conditions
        self.sell_conditions = sell_conditions
        self.buy_operator = buy_operator
        self.sell_operator = sell_operator
        self.logger = logging.getLogger(__name__)
        
    def evaluate_condition(self, df: pd.DataFrame, condition: StrategyCondition) -> pd.Series:
        """
        Evaluate a single condition on the dataframe.
        
        Args:
            df: DataFrame with indicator data
            condition: The condition to evaluate
            
        Returns:
            Boolean series indicating where condition is met
        """
        try:
            if condition.column1 not in df.columns:
                self.logger.warning(f"Column {condition.column1} not found in dataframe")
                return pd.Series([False] * len(df), index=df.index)
            
            col1 = df[condition.column1]
            
            if condition.operator in ['cross_above', 'cross_below']:
                # Handle cross conditions
                if condition.column2 and condition.column2 in df.columns:
                    col2 = df[condition.column2]
                    if condition.operator == 'cross_above':
                        return (col1.shift(condition.lookback) <= col2.shift(condition.lookback)) & (col1 > col2)
                    else:  # cross_below
                        return (col1.shift(condition.lookback) >= col2.shift(condition.lookback)) & (col1 < col2)
                elif condition.value is not None:
                    if condition.operator == 'cross_above':
                        return (col1.shift(condition.lookback) <= condition.value) & (col1 > condition.value)
                    else:  # cross_below
                        return (col1.shift(condition.lookback) >= condition.value) & (col1 < condition.value)
                        
            else:
                # Handle standard comparison conditions
                if condition.column2 and condition.column2 in df.columns:
                    col2 = df[condition.column2]
                    comparison_target = col2
                elif condition.value is not None:
                    comparison_target = condition.value
                else:
                    self.logger.warning(f"No comparison target for condition {condition.name}")
                    return pd.Series([False] * len(df), index=df.index)
                
                if condition.operator == '>':
                    return col1 > comparison_target
                elif condition.operator == '<':
                    return col1 < comparison_target
                elif condition.operator == '>=':
                    return col1 >= comparison_target
                elif condition.operator == '<=':
                    return col1 <= comparison_target
                elif condition.operator == '==':
                    return col1 == comparison_target
                elif condition.operator == '!=':
                    return col1 != comparison_target
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition {condition.name}: {str(e)}")
            
        return pd.Series([False] * len(df), index=df.index)
    
    def combine_conditions(self, conditions_results: List[pd.Series], operator: ConditionOperator) -> pd.Series:
        """
        Combine multiple condition results using the specified operator.
        
        Args:
            conditions_results: List of boolean series from condition evaluations
            operator: The logical operator to use
            
        Returns:
            Combined boolean series
        """
        if not conditions_results:
            return pd.Series([False] * len(conditions_results[0]) if conditions_results else [])
        
        if len(conditions_results) == 1:
            return conditions_results[0]
        
        result = conditions_results[0]
        for condition_result in conditions_results[1:]:
            if operator == ConditionOperator.AND:
                result = result & condition_result
            elif operator == ConditionOperator.OR:
                result = result | condition_result
                
        return result
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on the strategy conditions.
        
        Args:
            df: DataFrame with indicator data
            
        Returns:
            DataFrame with signal columns added
        """
        result_df = df.copy()
        
        # Evaluate buy conditions
        buy_results = []
        for condition in self.buy_conditions:
            buy_result = self.evaluate_condition(df, condition)
            buy_results.append(buy_result)
            
        # Evaluate sell conditions  
        sell_results = []
        for condition in self.sell_conditions:
            sell_result = self.evaluate_condition(df, condition)
            sell_results.append(sell_result)
        
        # Combine conditions
        if buy_results:
            result_df[f'{self.name}_buy'] = self.combine_conditions(buy_results, self.buy_operator)
        else:
            result_df[f'{self.name}_buy'] = False
            
        if sell_results:
            result_df[f'{self.name}_sell'] = self.combine_conditions(sell_results, self.sell_operator)
        else:
            result_df[f'{self.name}_sell'] = False
        
        # Generate signal strength (simple implementation)
        buy_strength = result_df[f'{self.name}_buy'].astype(float)
        sell_strength = result_df[f'{self.name}_sell'].astype(float)
        
        result_df[f'{self.name}_signal_strength'] = buy_strength - sell_strength
        
        return result_df
    
    def backtest(self, df: pd.DataFrame, initial_balance: float = 10000) -> Dict[str, Any]:
        """
        Simple backtesting of the strategy.
        
        Args:
            df: DataFrame with OHLC and indicator data
            initial_balance: Starting balance for backtest
            
        Returns:
            Dictionary with backtest results
        """
        signals_df = self.generate_signals(df)
        
        balance = initial_balance
        position = 0
        trades = []
        
        for i, row in signals_df.iterrows():
            if row[f'{self.name}_buy'] and position <= 0:
                # Buy signal
                if position < 0:
                    # Close short position
                    balance += position * row['close']
                    trades.append({'type': 'close_short', 'price': row['close'], 'timestamp': i})
                
                # Open long position
                position = balance / row['close']
                balance = 0
                trades.append({'type': 'buy', 'price': row['close'], 'timestamp': i})
                
            elif row[f'{self.name}_sell'] and position >= 0:
                # Sell signal
                if position > 0:
                    # Close long position
                    balance += position * row['close']
                    trades.append({'type': 'sell', 'price': row['close'], 'timestamp': i})
                    position = 0
        
        # Close any remaining position
        if position != 0:
            final_row = signals_df.iloc[-1]
            if position > 0:
                balance += position * final_row['close']
            else:
                balance += position * final_row['close']
            position = 0
        
        total_return = (balance - initial_balance) / initial_balance * 100
        
        return {
            'initial_balance': initial_balance,
            'final_balance': balance,
            'total_return_pct': total_return,
            'total_trades': len(trades),
            'trades': trades
        }

class StrategyLibrary:
    """
    Library of predefined trading strategies.
    """
    
    @staticmethod
    def create_legacy_di_stoch_strategy() -> TradingStrategy:
        """
        Create the legacy DI + Stochastic strategy from the original strategy.py.
        This replicates the original logic:
        - Buy: +DI crosses above -DI AND %K crosses above %D
        - Sell: +DI crosses below -DI AND %K crosses below %D
        """
        builder = StrategyBuilder("Legacy_DI_Stoch")
        
        # Buy conditions (original: di_buy AND stoc_buy)
        builder.add_buy_condition(StrategyCondition(
            name="di_cross_up",
            column1="+DI",
            operator="cross_above", 
            column2="-DI",
            lookback=1
        ))
        
        builder.add_buy_condition(StrategyCondition(
            name="stoch_cross_up",
            column1="%K",
            operator="cross_above",
            column2="%D", 
            lookback=1
        ))
        
        # Sell conditions (original: di_sell AND stoc_sell)
        builder.add_sell_condition(StrategyCondition(
            name="di_cross_down",
            column1="+DI",
            operator="cross_below",
            column2="-DI",
            lookback=1
        ))
        
        builder.add_sell_condition(StrategyCondition(
            name="stoch_cross_down", 
            column1="%K",
            operator="cross_below",
            column2="%D",
            lookback=1
        ))
        
        return builder.build()
    
    @staticmethod
    def create_rsi_oversold_strategy() -> TradingStrategy:
        """Create a simple RSI oversold/overbought strategy."""
        builder = StrategyBuilder("RSI_Oversold")
        
        # Buy when RSI crosses above 30 (oversold)
        builder.add_buy_condition(StrategyCondition(
            name="rsi_oversold_exit",
            column1="rsi_default_rsi",  # Assuming default RSI indicator name
            operator="cross_above",
            value=30
        ))
        
        # Sell when RSI crosses below 70 (overbought)
        builder.add_sell_condition(StrategyCondition(
            name="rsi_overbought_exit",
            column1="rsi_default_rsi",
            operator="cross_below", 
            value=70
        ))
        
        return builder.build()
    
    @staticmethod
    def create_supertrend_strategy() -> TradingStrategy:
        """Create a Supertrend-based strategy."""
        builder = StrategyBuilder("Supertrend")
        
        # Buy when direction becomes True (bullish)
        builder.add_buy_condition(StrategyCondition(
            name="supertrend_bullish",
            column1="supertrend_direction",
            operator="==",
            value=1  # True = bullish
        ))
        
        # Sell when direction becomes False (bearish)
        builder.add_sell_condition(StrategyCondition(
            name="supertrend_bearish",
            column1="supertrend_direction",
            operator="==",
            value=0  # False = bearish
        ))
        
        return builder.build()

# Legacy compatibility - preserve original strategy.py functionality
def apply_legacy_strategy_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the original strategy signals as defined in strategy.py.
    This preserves the exact original logic.
    """
    result_df = df.copy()
    
    # Original signal generation logic (preserved as comments):
    """
    Original strategy.py signal logic:
    
    eurusd_data['di_buy']  = (eurusd_data['+DI'].shift(1) < eurusd_data['-DI'].shift(1)) & (eurusd_data['+DI'] > eurusd_data['-DI'])
    eurusd_data['di_sell'] = (eurusd_data['+DI'].shift(1) > eurusd_data['-DI'].shift(1)) & (eurusd_data['+DI'] < eurusd_data['-DI'])
    
    eurusd_data['stoc_buy'] = (eurusd_data['%K'].shift(1) < eurusd_data['%D'].shift(1)) & (eurusd_data['%K'] > eurusd_data['%D'])
    eurusd_data['stoc_sell'] = (eurusd_data['%K'].shift(1) > eurusd_data['%D'].shift(1)) & (eurusd_data['%K'] < eurusd_data['%D'])
    """
    
    # Apply the original logic
    if all(col in result_df.columns for col in ['+DI', '-DI', '%K', '%D']):
        result_df['di_buy'] = (result_df['+DI'].shift(1) < result_df['-DI'].shift(1)) & (result_df['+DI'] > result_df['-DI'])
        result_df['di_sell'] = (result_df['+DI'].shift(1) > result_df['-DI'].shift(1)) & (result_df['+DI'] < result_df['-DI'])
        
        result_df['stoc_buy'] = (result_df['%K'].shift(1) < result_df['%D'].shift(1)) & (result_df['%K'] > result_df['%D'])
        result_df['stoc_sell'] = (result_df['%K'].shift(1) > result_df['%D'].shift(1)) & (result_df['%K'] < result_df['%D'])
        
        # Combined signals
        result_df['combined_buy'] = result_df['di_buy'] & result_df['stoc_buy']
        result_df['combined_sell'] = result_df['di_sell'] & result_df['stoc_sell']
    
    return result_df

# Example usage
if __name__ == "__main__":
    # Create legacy strategy
    legacy_strategy = StrategyLibrary.create_legacy_di_stoch_strategy()
    print(f"Created strategy: {legacy_strategy.name}")
    print(f"Buy conditions: {len(legacy_strategy.buy_conditions)}")
    print(f"Sell conditions: {len(legacy_strategy.sell_conditions)}")