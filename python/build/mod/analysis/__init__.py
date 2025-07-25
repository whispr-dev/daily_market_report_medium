from mod.utils.image_utils import fig_to_png_bytes
"""
Analysis package for stock market technical and fundamental analysis.

This package contains modules for various types of financial analysis:
- Technical indicators
- Market patterns
- Macroeconomic analysis
- Dividend analysis
"""

# You can optionally expose specific functions directly from the package level
# This allows users to import them like: from analysis import analyze_technicals
from .technical import analyze_technicals, calculate_ewo, detect_reversal_signals
from .market import find_trading_opportunities, get_market_summary
from .macro import prepare_macro_data, generate_forecast
from .dividend import analyze_dividend_history, get_current_bid_ask_spreads
# mod/analysis/__init__.py
from .market import find_trading_opportunities, get_market_summary

# You can define a __all__ list to control what's imported with "from analysis import *"
__all__ = [
    'analyze_technicals',
    'calculate_ewo',
    'detect_reversal_signals',
    'find_trading_opportunities',
    'get_market_summary',
    'prepare_macro_data',
    'generate_forecast',
    'analyze_dividend_history',
    'get_current_bid_ask_spreads'
]

# You could also add package-level variables or constants
PACKAGE_VERSION = '0.1.0'