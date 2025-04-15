"""
Configuration settings for the stock market analyzer application.
"""
import warnings
import os
import pandas as pd
from datetime import datetime, timedelta

# Suppress FutureWarnings to keep logs clean
warnings.simplefilter(action='ignore', category=FutureWarning)

# File paths
TEMPLATE_DIR = "."
TEMPLATE_FILE = "email_template.html"
STOCKS_UNIVERSE_FILE = "stocks_universe.csv"
LOG_DIR = "logs"

# Chart style settings
DARK_BG_COLOR = '#1b1b1b'
GRID_COLOR = '#444444'
UP_COLOR = '#4dfd5d'
DOWN_COLOR = '#fd4d4d'
LINE_COLOR = '#66ccff'

# Technical analysis settings
EWO_FAST_PERIOD = 5
EWO_SLOW_PERIOD = 35
REVERSAL_SENSITIVITY = 1.5
REVERSAL_LOOKBACK = 5

# Time periods
DEFAULT_LOOKBACK_PERIOD = '1y'
MACRO_LOOKBACK_DAYS = 180  # 6 months
FORECAST_STEPS = 60  # ~3 months trading days

# Data defaults
DEFAULT_UNIVERSE = pd.DataFrame({
    'symbol': ['^GSPC', 'SPY'],
    'sector': ['Index', 'ETF'],
})

# Create required directories
def ensure_directories_exist():
    """Create necessary directories if they don't exist."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)