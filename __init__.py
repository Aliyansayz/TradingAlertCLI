"""
Backend Package for Finance Trade Assistant

This package provides a comprehensive trading pipeline system that includes:
- Data fetching from multiple sources (yfinance)
- Technical indicator calculation and application
- Trading strategy definition and execution
- Complete pipeline orchestration

The package maintains backward compatibility with all existing code while
providing a modern, modular architecture for extensibility.
"""

# Core imports for GUI functionality - no automatic execution
from .utility.symbol_groups_manager import SymbolGroupManager, SymbolGroup, SymbolConfig
from .workflow.group_analysis_engine import GroupAnalysisEngine, GroupAnalysisReporter, SymbolAnalyzer
from .trading_cli import IndicatorSettings, PeriodicUnitTester, SchedulerSettings

# Import symbol mappings
from .utility.forex_symbols import get_forex_symbols
from .utility.indices_symbols import get_indices_symbols
from .utility.crypto_symbols import get_crypto_symbols, get_crypto_categories
from .utility.stocks_symbols import (
    get_popular_stocks, 
    get_sector_stocks,
    get_market_cap_categories,
    search_stock
)

# Import indicator classes (preserved for backward compatibility)
from .utility.indicators import ADX, Stochastic_Oscillator, ATRBands, SupertrendIndicator, RSI
from .utility.indicators_oscillators import Oscillator

# Package metadata
__version__ = "1.0.0"
__author__ = "Finance Trade Assistant"
__description__ = "Comprehensive trading pipeline system"

# Define what gets imported with "from backend import *"
__all__ = [
    # Core components for GUI
    "SymbolGroupManager",
    "SymbolGroup", 
    "SymbolConfig",
    "GroupAnalysisEngine",
    "GroupAnalysisReporter",
    "SymbolAnalyzer",
    "IndicatorSettings",
    "PeriodicUnitTester",
    "SchedulerSettings",
    
    # Symbol mappings
    "get_forex_symbols",
    "get_indices_symbols", 
    "get_crypto_symbols",
    "get_crypto_categories",
    "get_popular_stocks",
    "get_sector_stocks",
    "get_market_cap_categories",
    "search_stock",
    
    # Indicators
    "ADX",
    "Stochastic_Oscillator",
    "ATRBands", 
    "SupertrendIndicator",
    "RSI",
    "Oscillator",
]

def get_available_symbols():
    """Get all available symbols organized by asset type."""
    return {
        'forex': get_forex_symbols(),
        'crypto': get_crypto_symbols(),
        'indices': get_indices_symbols(),
        'stocks': get_popular_stocks()
    }

def print_usage_examples():
    """Print usage examples for the backend package."""
    print("""
Finance Trade Assistant Backend Usage:

1. Create a symbol group manager:
   >>> from backend import SymbolGroupManager
   >>> manager = SymbolGroupManager()

2. Create and analyze groups:
   >>> from backend import GroupAnalysisEngine
   >>> engine = GroupAnalysisEngine()
   >>> results = engine.analyze_group(group)

3. Get available symbols:
   >>> from backend import get_available_symbols
   >>> symbols = get_available_symbols()
   
4. Configure indicators:
   >>> from backend import IndicatorSettings
   >>> settings = IndicatorSettings()
""")

# Initialization message
def _init_message():
    """Print initialization message."""
    print(f"Finance Trade Assistant Backend v{__version__} loaded successfully!")
    print("Use help(backend) for documentation or backend.print_usage_examples() for examples.")

# Auto-run initialization message when package is imported
if __name__ != "__main__":
    try:
        _init_message()
    except:
        pass  # Silently fail if printing is not available
