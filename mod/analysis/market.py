"""
Market analysis functions focused on identifying trading opportunities.
"""
import numpy as np
import pandas as pd
import traceback
from .technical import analyze_technicals

def calculate_percent_changes(df_universe):
    """
    Calculate daily percentage changes for all symbols in the universe.
    
    Args:
        df_universe: DataFrame with 'symbol' column
        
    Returns:
        DataFrame with added 'pct_change' column
    """
    from ..data.fetcher import fetch_symbol_data
    
    df = df_universe.copy()
    changes = []
    
    for i, sym in enumerate(df['symbol']):
        try:
            # Show progress periodically
            if i % 25 == 0:
                print(f"Processing symbol {i+1}/{len(df)}")
            
            data = fetch_symbol_data(sym, period='2d')
            if data.empty:
                changes.append(np.nan)
                continue
                
            # Prefer 'Adj Close' if available
            col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
            
            # Need at least 2 rows
            if len(data) < 2:
                changes.append(np.nan)
                continue
                
            close_vals = data[col].dropna()
            if len(close_vals) < 2:
                changes.append(np.nan)
                continue
                
            pct = (close_vals.iloc[-1] - close_vals.iloc[-2]) / close_vals.iloc[-2] * 100.0
            changes.append(pct)
        except Exception as e:
            print(f"Error processing {sym}: {e}")
            changes.append(np.nan)

    df['pct_change'] = changes
    return df

def find_technical_patterns(df_universe):
    """
    Find 52-week highs and 200-day MA crossovers in stock universe.
    
    Args:
        df_universe: DataFrame with 'symbol' column
        
    Returns:
        tuple of (52-week high symbols, 200-day crossover symbols, errors)
    """
    fifty_two_week_high = []
    crossover_200d = []
    fails = []
    
    for i, sym in enumerate(df_universe['symbol']):
        try:
            # Show progress periodically
            if i % 25 == 0:
                print(f"Checking technicals for symbol {i+1}/{len(df_universe)}")
            
            tech_results = analyze_technicals(sym)
            
            if tech_results.get('error'):
                fails.append((sym, tech_results['error']))
                continue
            
            if tech_results['fifty_two_week_high']:
                fifty_two_week_high.append(sym)
                
            if tech_results['crossover_200d']:
                crossover_200d.append(sym)
                    
        except Exception as e:
            fails.append((sym, str(e)))
            
    return fifty_two_week_high, crossover_200d, fails

def find_trading_opportunities(df_universe):
    """
    Find potential trading opportunities based on the trading rules.
    
    Buy signals:
    - Magic Reversal Indicator bullish signal
    - Elliott Wave Oscillator green and rising
    - Confirmation candle
    
    Sell signals:
    - Magic Reversal Indicator bearish signal
    - Elliott Wave Oscillator red and falling
    - Confirmation candle
    
    Args:
        df_universe: DataFrame with 'symbol' column
        
    Returns:
        dict with buy and sell signals
    """
    buy_signals = []
    sell_signals = []
    errors = []
    
    for i, row in df_universe.iterrows():
        sym = row['symbol']
        try:
            # Analyze technicals for this symbol
            tech = analyze_technicals(sym)
            
            if tech.get('error'):
                errors.append((sym, tech['error']))
                continue
                
            # Check for buy signal
            if tech['recent_bull_reversal'] and tech['ewo_bullish']:
                buy_signals.append({
                    'symbol': sym,
                    'reason': "Bullish reversal with positive EWO momentum"
                })
                
            # Check for sell signal
            if tech['recent_bear_reversal'] and tech['ewo_bearish']:
                sell_signals.append({
                    'symbol': sym,
                    'reason': "Bearish reversal with negative EWO momentum"
                })
                
        except Exception as e:
            errors.append((sym, str(e)))
            
    return {
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'errors': errors
    }

def get_market_summary():
    """
    Get current S&P 500 market summary data.
    
    Returns:
        dict with S&P 500 data including value, date, and percent change
    """
    from ..data.fetcher import fetch_symbol_data
    
    try:
        spx = fetch_symbol_data("^GSPC", period='2d')
        sp500_value = 0
        sp500_pct_change = 0
        sp500_date = ""
        
        if not spx.empty:
            if 'Close' in spx.columns:
                sp500_value = spx['Close'].iloc[-1]
                sp500_date = str(spx.index[-1].date())
                if len(spx) > 1:
                    sp500_pct_change = (spx['Close'].iloc[-1] - spx['Close'].iloc[-2]) / spx['Close'].iloc[-2] * 100.0
    except Exception as e:
        print(f"Error getting S&P 500 data: {e}")
        from datetime import datetime
        sp500_value = "N/A"
        sp500_pct_change = 0
        sp500_date = datetime.today().strftime("%Y-%m-%d")
        
    return {
        'value': sp500_value,
        'date': sp500_date,
        'pct_change': sp500_pct_change
    }