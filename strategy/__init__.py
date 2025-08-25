"""
Strategy Package

This package contains all trading strategy implementations for the Finance Trade Assistant.
Strategies are registered here for easy access throughout the application.
"""

from .default_strategy import DefaultSingleTimeframeStrategy, create_default_strategy
from .dual_supertrend_check_single_timeframe import DualSupertrendSingleTimeframeStrategy, create_dual_supertrend_strategy

# Centralized strategy registry
STRATEGY_REGISTRY = {
    # Default strategy
    "default-check-single-timeframe": create_default_strategy,
    "single-check": create_default_strategy,  # Legacy name support
    
    # Dual Supertrend strategy
    "dual-supertrend-check-single-timeframe": create_dual_supertrend_strategy,
    "dual-supertrend": create_dual_supertrend_strategy,  # Short name
}

def get_strategy(strategy_name: str, custom_parameters=None):
    """
    Get a strategy instance by name.
    
    Args:
        strategy_name: Name of the strategy to create
        custom_parameters: Optional dictionary with custom parameter values
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If strategy name is not found
    """
    if strategy_name in STRATEGY_REGISTRY:
        return STRATEGY_REGISTRY[strategy_name](custom_parameters)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(STRATEGY_REGISTRY.keys())}")

def get_strategy_parameters_template(strategy_name: str):
    """
    Get the parameters template for a specific strategy.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Dictionary with parameter definitions
    """
    if strategy_name in STRATEGY_REGISTRY:
        strategy = STRATEGY_REGISTRY[strategy_name]()
        return strategy.get_parameters_template()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

def has_configurable_parameters(strategy_name: str) -> bool:
    """
    Check if a strategy has configurable parameters.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        True if strategy has configurable parameters
    """
    try:
        template = get_strategy_parameters_template(strategy_name)
        # Check if there are any real parameters (not just info messages)
        configurable_params = [p for p in template.values() if p.get("type") != "info"]
        return len(configurable_params) > 0
    except:
        return False

def list_available_strategies():
    """
    Get list of all available strategies.
    
    Returns:
        List of strategy names
    """
    return list(STRATEGY_REGISTRY.keys())

def get_strategy_info(strategy_name: str):
    """
    Get information about a specific strategy.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Dictionary with strategy information
    """
    if strategy_name in STRATEGY_REGISTRY:
        strategy = STRATEGY_REGISTRY[strategy_name]()
        return strategy.get_strategy_info()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

__all__ = [
    'DefaultSingleTimeframeStrategy',
    'DualSupertrendSingleTimeframeStrategy', 
    'get_strategy',
    'list_available_strategies',
    'get_strategy_info',
    'get_strategy_parameters_template',
    'has_configurable_parameters',
    'STRATEGY_REGISTRY'
]
