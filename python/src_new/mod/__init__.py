from mod.utils.image_utils import fig_to_png_bytes
"""
Stock Market Analyzer package.
"""
# Import main modules to make imports cleaner
from .analysis import analyze_technicals, calculate_ewo, detect_reversal_signals
from .analysis import find_trading_opportunities, get_market_summary
from .analysis import prepare_macro_data, generate_forecast
from .analysis import analyze_dividend_history
