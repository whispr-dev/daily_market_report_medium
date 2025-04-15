import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pandas_datareader import data as pdr
import matplotlib.gridspec as gridspec

import base64
import io
import os
import warnings
import traceback
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from sendemail import send_email

# Suppress FutureWarnings to keep logs clean
warnings.simplefilter(action='ignore', category=FutureWarning)

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

def generate_candlestick_chart():
    """Download 6mo of ^GSPC, produce a candlestick chart, return base64."""
    try:
        df = yf.download("^GSPC", period="6mo", interval="1d", progress=False)
        if df.empty:
            print("Warning: ^GSPC candlestick data is empty.")
            return None

        # Handle multi-index columns in yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df.columns]

        # We only need these columns for mplfinance
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for c in required_cols:
            if c not in df.columns:
                print(f"Warning: {c} column missing in ^GSPC for candlestick chart.")
                return None

        # Coerce to numeric and handle missing values
        df = df[required_cols].apply(pd.to_numeric, errors='coerce')
        if df.isna().any().any():  # Check for any NaN values
            print("Warning: NaN values found in ^GSPC data. Filling forward.")
            df = df.ffill().bfill()  # Fill forward, then backward for any remaining NaNs
            
        if len(df) < 2:  # Ensure we have enough data points
            print("Warning: Not enough data points for ^GSPC candlestick chart.")
            return None

        df.index.name = 'Date'
        # Use a style that works well with dark background
        mpf_style = mpf.make_mpf_style(
            base_mpf_style='charles', 
            marketcolors=mpf.make_marketcolors(
                up='#4dfd5d', down='#fd4d4d',
                edge='inherit',
                wick='inherit',
                volume='in'
            ),
            figcolor='#1b1b1b',
            facecolor='#1b1b1b',
            edgecolor='#444444',
            gridcolor='#444444',
            gridstyle=':',
            gridaxis='both',
            y_on_right=True,
        )
        
        fig, axlist = mpf.plot(
            df, 
            type='candle', 
            style=mpf_style, 
            volume=True, 
            title="S&P 500 - 6 Month Candlestick Chart",
            returnfig=True, 
            figsize=(10, 6),
            tight_layout=True
        )
        
        # Adjust title color for dark background
        axlist[0].set_title("S&P 500 - 6 Month Candlestick Chart", color='white')
        
        # Adjust label colors
        for ax in axlist:
            ax.tick_params(colors='white')
            ax.set_ylabel(ax.get_ylabel(), color='white')
            
        return img_to_base64(fig)
    except Exception as e:
        print("Candlestick plot error:", e)
        traceback.print_exc()
        return None

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
        traceback.print_exc()
        return None

def generate_sector_heatmap(df_universe):
    """Generate a sector heatmap showing daily percentage changes."""
    try:
        # Check if we have the necessary columns
        if 'symbol' not in df_universe.columns:
            print("Warning: Missing 'symbol' column for heatmap.")
            return None
            
        # Check if we have a sector column
        if 'sector' not in df_universe.columns:
            print("Warning: Missing 'sector' column for heatmap. Using default.")
            df_universe['sector'] = 'Unknown'
            
        # Ensure we have pct_change and that it's numeric
        if 'pct_change' not in df_universe.columns:
            print("Warning: Missing pct_change column for heatmap.")
            return None
            
        # Make a copy to avoid modifying the original
        df = df_universe.copy()
        
        # Force numeric and drop NaNs
        df['pct_change'] = pd.to_numeric(df['pct_change'], errors='coerce')
        df.dropna(subset=['pct_change', 'sector'], inplace=True)
        
        # Filter out rows with empty sectors
        df = df[df['sector'].str.strip() != ""]
        
        if len(df) < 3:  # Arbitrary threshold - need enough data to make a meaningful heatmap
            print("Warning: Not enough valid data for sector heatmap.")
            return None

        # Group by sector to calculate average percent change per sector
        sector_data = df.groupby('sector')['pct_change'].agg(['mean', 'count']).reset_index()
        sector_data.columns = ['Sector', 'Avg Change %', 'Count']
        sector_data = sector_data.sort_values('Avg Change %', ascending=False)
        
        if len(sector_data) < 2:
            print("Warning: Not enough sectors for heatmap.")
            return None
            
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(10, max(6, len(sector_data) * 0.4)))
        
        # Set colors based on values (green for positive, red for negative)
        colors = ['#4dfd5d' if x >= 0 else '#fd4d4d' for x in sector_data['Avg Change %']]
        
        # Create horizontal bar chart
        bars = ax.barh(sector_data['Sector'], sector_data['Avg Change %'], color=colors)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width >= 0 else width - 0.2
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                    f'{width:.2f}%', va='center', ha='left' if width >= 0 else 'right',
                    color='black' if width >= 0 else 'white')
        
        # Style the chart
        ax.set_facecolor('#1b1b1b')
        fig.set_facecolor('#1b1b1b')
        ax.tick_params(colors='white')
        ax.set_xlabel('Percentage Change', color='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.grid(axis='x', linestyle=':', color='#444')
        
        ax.set_title('Sector Performance - Daily % Change', color='white')
        plt.tight_layout()
        
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error generating sector heatmap: {e}")
        traceback.print_exc()
        return None

def generate_macro_chart():
    """
    Download 6 months of data for S&P (Close or Adj Close),
    BTC-USD, and US M2 from FRED. Then produce a single line chart
    comparing them all. Also does a simple 6-month forecast for the S&P.
    """
    try:
        end = datetime.today()
        start = end - timedelta(days=180)
        
        # Get S&P 500 data
        try:
            df_spx = yf.download("^GSPC", start=start, progress=False)
            # Handle multi-index columns
            if isinstance(df_spx.columns, pd.MultiIndex):
                df_spx.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df_spx.columns]
            # Pick Close or Adj Close if available
            spx_col = "Adj Close" if "Adj Close" in df_spx.columns else "Close"
            if df_spx.empty or spx_col not in df_spx.columns:
                print("Warning: ^GSPC macro chart missing data.")
                return None
        except Exception as e:
            print(f"Error downloading S&P 500 data: {e}")
            return None
        
        # Get Bitcoin data
        try:
            df_btc = yf.download("BTC-USD", start=start, progress=False)
            # Handle multi-index columns
            if isinstance(df_btc.columns, pd.MultiIndex):
                df_btc.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df_btc.columns]
            # Pick Close or Adj Close if available
            btc_col = "Adj Close" if "Adj Close" in df_btc.columns else "Close"
            if df_btc.empty or btc_col not in df_btc.columns:
                print("Warning: BTC macro chart missing data.")
                return None
        except Exception as e:
            print(f"Error downloading Bitcoin data: {e}")
            return None
        
        # Get M2 data
        try:
            # Try to get M2 data from FRED
            df_m2 = pdr.DataReader("M2SL", "fred", start)
            if df_m2.empty or 'M2SL' not in df_m2.columns:
                print("Warning: M2 data is empty. Using placeholder values.")
                # Create empty DataFrame with same index as S&P
                df_m2 = pd.DataFrame(index=df_spx.index)
                df_m2['M2SL'] = np.nan
        except Exception as e:
            print(f"Warning: M2SL DataReader error: {e}")
            # Create empty DataFrame with same index as S&P
            df_m2 = pd.DataFrame(index=df_spx.index)
            df_m2['M2SL'] = np.nan
        
        # Combine into a single DataFrame
        df = pd.DataFrame({
            "S&P 500": df_spx[spx_col],
            "BTC": df_btc[btc_col],
            "M2": df_m2["M2SL"]
        })
        
        # Forward fill missing values and drop any completely empty rows
        df = df.ffill().dropna(how='all')
        if len(df) < 2:
            print("Warning: Not enough macro data to plot.")
            return None
            
        # Normalize to percentage change from start
        df_normalized = df.copy()
        for col in df.columns:
            if not df[col].isna().all():  # Skip columns that are all NaN
                first_valid = df[col].first_valid_index()
                if first_valid is not None:
                    base_value = df[col].loc[first_valid]
                    df_normalized[col] = df[col] / base_value * 100 - 100  # Show as % change from start
        
        # Only keep the columns that have data
        df_normalized = df_normalized.dropna(axis=1, how='all')
        
        # Optional short forecast for S&P
        forecast = None
        try:
            if "S&P 500" in df_normalized.columns and len(df_normalized["S&P 500"].dropna()) > 10:
                model = ExponentialSmoothing(
                    df_normalized["S&P 500"].dropna(), 
                    trend='add', 
                    seasonal=None,
                    initialization_method="estimated"
                )
                fit = model.fit()
                forecast_steps = 60  # ~3 months
                forecast = fit.forecast(steps=forecast_steps)
        except Exception as e:
            print(f"Forecast error: {e}")
            forecast = None
        
        # Create the plot with dark theme
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.set_facecolor('#1b1b1b')
        ax.set_facecolor('#1b1b1b')
        
        # Set the color cycle to match theme
        colors = ['#66ccff', '#4dfd5d', '#fd4d4d']
        
        # Plot the data
        for i, col in enumerate(df_normalized.columns):
            df_normalized[col].dropna().plot(
                ax=ax, 
                linewidth=2, 
                label=col,
                color=colors[i % len(colors)]
            )
        
        # Add forecast if available
        if forecast is not None and not forecast.empty:
            last_date = df_normalized.index[-1]
            forecast_index = pd.date_range(
                last_date + pd.Timedelta(days=1), 
                periods=len(forecast), 
                freq='B'
            )
            forecast = pd.Series(forecast.values, index=forecast_index)
            forecast.plot(
                ax=ax, 
                style="--", 
                color="#66ccff", 
                label="S&P 500 Forecast",
                linewidth=1.5
            )
        
        # Style the chart
        ax.set_title("Macro Trends: S&P 500 vs BTC vs M2 (6mo + forecast)", color='white')
        ax.set_ylabel("% Change from Start", color='white')
        ax.grid(True, linestyle=':', color='#444')
        ax.tick_params(colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        
        # Set legend with white text
        legend = ax.legend(facecolor='#1b1b1b')
        for text in legend.get_texts():
            text.set_color('white')
        
        plt.tight_layout()
        
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error creating macro chart: {e}")
        traceback.print_exc()
        return None

def analyze_technicals(symbol, period='1y'):
    """
    Enhanced technical analysis for a single symbol.
    Checks for:
    1. 52-week high
    2. 200-day MA crossover
    3. EWO status (bullish/bearish)
    4. Reversal signals
    
    Parameters:
    symbol : str, ticker symbol
    period : str, lookback period (default: '1y')
    
    Returns:
    dict with technical findings
    """
    try:
        df_data = yf.download(symbol, period=period, progress=False)
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

        # Handle multi-index columns
        if isinstance(df_data.columns, pd.MultiIndex):
            df_data.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df_data.columns]

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

def find_trading_opportunities(df_universe):
    """
    Find potential trading opportunities based on the trading rules in fin.txt.
    
    Buy signals:
    - Magic Reversal Indicator bullish signal
    - Elliott Wave Oscillator green and rising
    - Confirmation candle
    
    Sell signals:
    - Magic Reversal Indicator bearish signal
    - Elliott Wave Oscillator red and falling
    - Confirmation candle
    
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

def main():
    """Main function to generate and send the daily stock market report."""
    print("Starting Daily Stonk Market Report generation...")
    
    try:
        # Create a logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        # 1) Read CSV, ensure 'symbol' column
        try:
            df_universe = pd.read_csv("stocks_universe.csv")
            df_universe.columns = df_universe.columns.str.strip().str.lower()
            
            if 'symbol' not in df_universe.columns:
                raise KeyError("The 'symbol' column is missing from stocks_universe.csv")
                
            # Add sector column if missing (needed for heatmap)
            if 'sector' not in df_universe.columns and 'sectordisp' in df_universe.columns:
                df_universe['sector'] = df_universe['sectordisp']
            elif 'sector' not in df_universe.columns:
                print("Warning: 'sector' column missing. Adding default sector for heatmap.")
                df_universe['sector'] = "Unknown"
                
        except Exception as e:
            print(f"Error reading stock universe: {e}")
            print("Using default S&P 500 symbols...")
            # Fallback to basic S&P 500 index only if universe file fails
            df_universe = pd.DataFrame({
                'symbol': ['^GSPC', 'SPY'],
                'sector': ['Index', 'ETF'],
            })

        # 2) Build daily % change for each symbol
        print(f"Downloading data for {len(df_universe)} symbols...")
        changes = []
        for i, sym in enumerate(df_universe['symbol']):
            try:
                # Show progress periodically
                if i % 25 == 0:
                    print(f"Processing symbol {i+1}/{len(df_universe)}")
                
                data = yf.download(sym, period='2d', progress=False)
                if data.empty:
                    changes.append(np.nan)
                    continue
                    
                # Handle multi-index columns
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in data.columns]
                
                # prefer 'Adj Close' if available
                col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
                
                # need at least 2 rows
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

        df_universe['pct_change'] = changes

        # 3) Determine 52-week highs and 200d cross
        print("Finding 52-week highs and 200-day MA crossovers...")
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

        # 4) Find trading opportunities based on EWO and reversal signals
        print("Finding trading opportunities...")
        trading_signals = find_trading_opportunities(df_universe)
        buy_signals = trading_signals['buy_signals']
        sell_signals = trading_signals['sell_signals']
        fails.extend(trading_signals['errors'])

        # 5) Gather S&P 500 stats for the email
        print("Getting S&P 500 data...")
        try:
            spx = yf.download("^GSPC", period='2d', progress=False)
            sp500_value = 0
            sp500_pct_change = 0
            sp500_date = ""
            
            if not spx.empty:
                # Handle multi-index columns
                if isinstance(spx.columns, pd.MultiIndex):
                    spx.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in spx.columns]
                
                if 'Close' in spx.columns:
                    sp500_value = spx['Close'].iloc[-1]
                    sp500_date = str(spx.index[-1].date())
                    if len(spx) > 1:
                        sp500_pct_change = (spx['Close'].iloc[-1] - spx['Close'].iloc[-2]) / spx['Close'].iloc[-2] * 100.0
        except Exception as e:
            print(f"Error getting S&P 500 data: {e}")
            sp500_value = "N/A"
            sp500_pct_change = 0
            sp500_date = datetime.today().strftime("%Y-%m-%d")

        # 6) Generate charts
        print("Generating standard candlestick chart...")
        candle_b64 = generate_candlestick_chart()
        
        print("Generating enhanced chart with reversal indicators...")
        enhanced_b64 = generate_enhanced_candlestick_chart()
        
        print("Generating sector heatmap...")
        heatmap_b64 = generate_sector_heatmap(df_universe)
        
        print("Generating macro chart...")
        macro_b64 = generate_macro_chart()

        # 7) Render template
        print("Rendering HTML template...")
        env = Environment(loader=FileSystemLoader("."))
        try:
            template = env.get_template("email_template.html")
            
            html_output = template.render(
                sp500_value=f"{sp500_value:.2f}" if isinstance(sp500_value, float) else sp500_value,
                sp500_date=sp500_date,
                sp500_pct_change=f"{sp500_pct_change:.2f}" if isinstance(sp500_pct_change, float) else sp500_pct_change,
                candle_chart=candle_b64,
                enhanced_chart=enhanced_b64,
                heatmap=heatmap_b64,
                macro_chart=macro_b64,
                fifty_two_week_high=fifty_two_week_high,
                crossover_200d=crossover_200d,
                buy_signals=buy_signals,
                sell_signals=sell_signals,
                failed_stocks=fails
            )
            
            # Save a local copy of the report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"report_{timestamp}.html"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(html_output)
            print(f"HTML report saved as {report_filename}")
            
            # 8) Send email
            print("Sending email...")
            try:
                send_email("Daily Stonk Market Report", html_output)
                print("Email sent successfully!")
            except Exception as e:
                print(f"Error sending email: {e}")
                print("Email could not be sent, but HTML report was saved locally.")
                
        except Exception as e:
            print(f"Error rendering template: {e}")
            
    except Exception as e:
        print(f"Unexpected error in main function: {e}")
        traceback.print_exc()
    
    print("Daily Stonk Market Report generation completed.")

if __name__ == "__main__":
    main()