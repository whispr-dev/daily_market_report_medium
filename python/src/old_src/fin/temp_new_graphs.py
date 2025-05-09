import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import io
import base64
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec

def img_to_base64(fig):
    """Utility to convert a Matplotlib figure to base64-encoded PNG."""
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)  # Close figure to free memory
        return img_data
    except Exception as e:
        print(f"Error in img_to_base64: {e}")
        plt.close(fig)  # Ensure figure is closed even on error
        return None

def calculate_ewo(df, fast_period=5, slow_period=35):
    """
    Calculate Elliott Wave Oscillator (EWO)
    EWO = Fast MA - Slow MA of the close prices
    """
    # Ensure we have the necessary columns
    if 'Close' not in df.columns:
        print("Warning: Close column missing for EWO calculation.")
        return None
    
    # Calculate the two moving averages
    df['fast_ma'] = df['Close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['Close'].rolling(window=slow_period).mean()
    
    # Calculate the EWO
    df['ewo'] = df['fast_ma'] - df['slow_ma']
    
    return df

def detect_reversal_signals(df, sensitivity=1.5, lookback=5):
    """
    Detect potential reversal signals based on price action.
    This is a simplified approach to mimic K's Reversal Indicator.
    
    Parameters:
    df : DataFrame with OHLC data
    sensitivity : float, controls how sensitive the detection is
    lookback : int, number of periods to look back for pattern detection
    
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

def generate_enhanced_candlestick_chart():
    """
    Download 6mo of ^GSPC, add technical indicators, produce a candlestick chart with EWO.
    """
    try:
        # Download the data
        df = yf.download("^GSPC", period="6mo", interval="1d", progress=False)
        if df.empty:
            print("Warning: ^GSPC candlestick data is empty.")
            return None

        # Handle multi-index columns in yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df.columns]

        # We need these columns for mplfinance
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for c in required_cols:
            if c not in df.columns:
                print(f"Warning: {c} column missing in ^GSPC for candlestick chart.")
                return None

        # Coerce to numeric and handle missing values
        df = df[required_cols].apply(pd.to_numeric, errors='coerce')
        if df.isna().any().any():
            print("Warning: NaN values found in ^GSPC data. Filling forward.")
            df = df.ffill().bfill()
            
        if len(df) < 2:
            print("Warning: Not enough data points for ^GSPC candlestick chart.")
            return None

        # Calculate the Elliott Wave Oscillator
        df = calculate_ewo(df)
        
        # Add reversal signal detection
        df = detect_reversal_signals(df)
        
        # Create figure with two subplots (candlestick above, EWO below)
        fig = plt.figure(figsize=(12, 8), facecolor='#1b1b1b')
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        
        # Main chart (candlestick)
        ax1 = fig.add_subplot(gs[0])
        
        # Plot candlesticks
        mpf.plot(
            df, 
            type='candle', 
            style='charles', 
            ax=ax1,
            volume=False,  # We'll handle volume separately
            ylabel='Price ($)',
            datetime_format='%Y-%m-%d',
            xrotation=45,
            colorup='#4dfd5d', 
            colordown='#fd4d4d',
            edgecolor='#1b1b1b'
        )
        
        # Add the "blue line" (20-day moving average)
        ax1.plot(df.index, df['blue_line'], color='#66ccff', linewidth=1.5, label='20-Day MA')
        
        # Add reversal markers
        for idx, row in df.iterrows():
            if row['bull_reversal']:
                ax1.scatter(idx, row['Low'] * 0.995, marker='^', color='#4dfd5d', s=100, zorder=5)
            elif row['bear_reversal']:
                ax1.scatter(idx, row['High'] * 1.005, marker='v', color='#fd4d4d', s=100, zorder=5)
        
        # Style the main chart
        ax1.set_facecolor('#1b1b1b')
        ax1.set_title("S&P 500 with Reversal Signals", color='white', fontsize=16)
        ax1.tick_params(colors='white')
        ax1.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax1.legend(facecolor='#333333', edgecolor='#444444', labelcolor='white')
        
        # EWO chart
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        # Plot EWO as a histogram
        ewo_colors = ['#fd4d4d' if x < 0 else '#4dfd5d' for x in df['ewo']]
        ax2.bar(df.index, df['ewo'], color=ewo_colors, alpha=0.7)
        
        # Add a zero line
        ax2.axhline(y=0, color='#aaaaaa', linestyle='-', linewidth=0.5)
        
        # Style the EWO chart
        ax2.set_facecolor('#1b1b1b')
        ax2.set_title("Elliott Wave Oscillator (5-35)", color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax2.set_ylabel('EWO Value', color='white')
        
        # Adjust layout and style the figure
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)
        
        return img_to_base64(fig)
        
    except Exception as e:
        print("Enhanced candlestick plot error:", e)
        import traceback
        traceback.print_exc()
        return None