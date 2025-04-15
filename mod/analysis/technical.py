"""
Technical analysis functions for stock data.
"""
import numpy as np
import pandas as pd
from ..config import EWO_FAST_PERIOD, EWO_SLOW_PERIOD, REVERSAL_SENSITIVITY, REVERSAL_LOOKBACK

def calculate_ewo(df, fast_period=EWO_FAST_PERIOD, slow_period=EWO_SLOW_PERIOD):
    """
    Calculate Elliott Wave Oscillator (EWO)
    EWO = Fast MA - Slow MA of the close prices
    
    Args:
        df: DataFrame with OHLC data
        fast_period: Period for fast moving average
        slow_period: Period for slow moving average
        
    Returns:
        DataFrame with added EWO columns
    """
    # Ensure we have the necessary columns
    if 'Close' not in df.columns:
        print("Warning: Close column missing for EWO calculation.")
        return df
    
    # Calculate the two moving averages
    df['fast_ma'] = df['Close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['Close'].rolling(window=slow_period).mean()
    
    # Calculate the EWO
    df['ewo'] = df['fast_ma'] - df['slow_ma']
    
    return df

def detect_reversal_signals(df, sensitivity=REVERSAL_SENSITIVITY, lookback=REVERSAL_LOOKBACK):
    """
    Detect potential reversal signals based on price action.
    This is a simplified approach to mimic K's Reversal Indicator.
    
    Args:
        df: DataFrame with OHLC data
        sensitivity: float, controls how sensitive the detection is
        lookback: int, number of periods to look back for pattern detection
        
    Returns:
        DataFrame with added columns for reversal signals
    """
    # Copy the dataframe to avoid modifying the original
    df = df.copy()
    
    # Calculate some basic indicators
    # 1. ATR (Average True Range) for volatility
    df['high_low'] = df['High'] - df['Low']
    df['high_close'] = np.abs(df['High'] - df['Close'].shift(1))
    df['low_close'] = np.abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = np.maximum(df['high_low'], np.maximum(df['high_close'], df['low_close']))
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # 2. Price momentum
    df['price_momentum'] = df['Close'].diff(lookback)
    
    # 3. Detect potential reversal points
    # Bullish reversal: price has been falling and momentum starts to turn positive
    df['bull_reversal'] = (df['price_momentum'].shift(1) < 0) & \
                          (df['price_momentum'] > 0) & \
                          (df['Low'] < df['Low'].rolling(window=lookback).min().shift(1)) & \
                          (df['Close'] > df['Open']) & \
                          (df['ATR'] > df['ATR'].rolling(window=lookback*2).mean() * sensitivity)
                           
    # Bearish reversal: price has been rising and momentum starts to turn negative
    df['bear_reversal'] = (df['price_momentum'].shift(1) > 0) & \
                          (df['price_momentum'] < 0) & \
                          (df['High'] > df['High'].rolling(window=lookback).max().shift(1)) & \
                          (df['Close'] < df['Open']) & \
                          (df['ATR'] > df['ATR'].rolling(window=lookback*2).mean() * sensitivity)
    
    # 4. Calculate a "blue line" reference (a simple moving average)
    df['blue_line'] = df['Close'].rolling(window=20).mean()
    
    # Clean up temporary columns
    df = df.drop(['high_low', 'high_close', 'low_close', 'TR'], axis=1)
    
    return df

def analyze_technicals(symbol, df_data=None, period='1y'):
    """
    Enhanced technical analysis for a single symbol.
    Checks for:
    1. 52-week high
    2. 200-day MA crossover
    3. EWO status (bullish/bearish)
    4. Reversal signals
    
    Args:
        symbol: str, ticker symbol
        df_data: DataFrame, optional pre-loaded data
        period: str, lookback period
        
    Returns:
        dict with technical findings
    """
    from ..data.fetcher import fetch_symbol_data
    
    try:
        if df_data is None:
            df_data = fetch_symbol_data(symbol, period=period)
            
        results = {
            'symbol': symbol,
            'fifty_two_week_high': False,
            'crossover_200d': False,
            'ewo_bullish': False,
            'ewo_bearish': False,
            'recent_bull_reversal': False,
            'recent_bear_reversal': False,
            'error': None
        }
        
        if df_data.empty: 
            results['error'] = "No data returned"
            return results

        # prefer Adj Close
        col = 'Adj Close' if 'Adj Close' in df_data.columns else 'Close'
        closes = df_data[col].dropna()

        if len(closes) < 5:  # Need at least 5 days for basic indicators
            results['error'] = "Not enough data"
            return results

        # Check for 52-week high
        current_price = closes.iloc[-1]
        max_52wk = closes.max()
        
        if np.isclose(current_price, max_52wk, atol=0.01) or current_price >= max_52wk * 0.99:
            results['fifty_two_week_high'] = True

        # Check for 200-day MA crossover
        if len(closes) >= 200:
            ma200 = closes.rolling(200).mean()
            # Check if price crossed above MA recently (within last 5 days)
            if (closes.iloc[-1] > ma200.iloc[-1]) and any(closes.iloc[-6:-1] <= ma200.iloc[-6:-1].values):
                results['crossover_200d'] = True
        
        # Calculate EWO if we have enough data
        if len(df_data) >= 35:  # Minimum required for slow EWO period
            # Add required columns if missing
            if 'Open' not in df_data.columns:
                df_data['Open'] = closes
            if 'High' not in df_data.columns:
                df_data['High'] = closes
            if 'Low' not in df_data.columns:
                df_data['Low'] = closes
                
            # Calculate EWO
            df_data = calculate_ewo(df_data)
            
            # Check recent EWO status (last 3 days)
            recent_ewo = df_data['ewo'].iloc[-3:].values
            
            # EWO is bullish if the latest value is positive and increasing
            if recent_ewo[-1] > 0 and recent_ewo[-1] > recent_ewo[-2]:
                results['ewo_bullish'] = True
            
            # EWO is bearish if the latest value is negative and decreasing
            if recent_ewo[-1] < 0 and recent_ewo[-1] < recent_ewo[-2]:
                results['ewo_bearish'] = True
                
            # Add reversal signal detection
            df_data = detect_reversal_signals(df_data)
            
            # Check for recent reversal signals (last 5 days)
            if df_data['bull_reversal'].iloc[-5:].any():
                results['recent_bull_reversal'] = True
                
            if df_data['bear_reversal'].iloc[-5:].any():
                results['recent_bear_reversal'] = True
                
        return results
        
    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}