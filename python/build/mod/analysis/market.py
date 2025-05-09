from mod.utils.image_utils import fig_to_png_bytes
"""
Module for market analysis functions.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os
import re

def calculate_percent_changes(symbols):
    """
    Calculate daily percent changes for the given symbols.
    
    Args:
        symbols (list): List of stock symbols or DataFrame with symbol column
        
    Returns:
        pd.DataFrame: DataFrame with symbols and their percent changes
    """
    from mod.data.fetcher import fetch_symbol_data
    
    results = []
    
    # Check if input is already a DataFrame
    if isinstance(symbols, pd.DataFrame):
        # Extract symbols from DataFrame
        if 'symbol' in symbols.columns:
            symbols = symbols['symbol'].tolist()
        else:
            # Assume the DataFrame index contains symbols
            symbols = symbols.index.tolist()
    
    # Process each symbol
    for symbol in symbols:
        try:
            # Fetch data for the symbol
            data = fetch_symbol_data(symbol, period="5d", interval="1d")
            
            if data is not None and not data.empty:
                # Calculate percent changes
                if len(data) >= 2:
                    last_close = data['Close'].iloc[-1]
                    prev_close = data['Close'].iloc[-2]
                    pct_change = ((last_close - prev_close) / prev_close) * 100
                    
                    # Get additional data
                    daily_high = data['High'].iloc[-1]
                    daily_low = data['Low'].iloc[-1]
                    volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
                    
                    results.append({
                        'symbol': symbol,
                        'last_price': last_close,
                        'previous_close': prev_close,
                        'daily_change': last_close - prev_close,
                        'percent_change': pct_change,
                        'daily_high': daily_high,
                        'daily_low': daily_low,
                        'volume': volume
                    })
                else:
                    print(f"Not enough data for {symbol}")
        except Exception as e:
            print(f"Error calculating percent change for {symbol}: {e}")
    
    # Create DataFrame from results
    df_results = pd.DataFrame(results)
    
    # Sort by percent change (descending)
    if not df_results.empty:
        df_results = df_results.sort_values('percent_change', ascending=False)
    
    return df_results

def find_technical_patterns(symbols, pattern_type='all'):
    """
    Find technical patterns in the given symbols.
    
    Args:
        symbols (list or pd.DataFrame): List of stock symbols or DataFrame with symbol column
        pattern_type (str): Type of patterns to find ('all', 'bullish', 'bearish')
        
    Returns:
        tuple: (fifty_two_week_high, crossover_200d, technical_errors)
            - fifty_two_week_high: DataFrame of stocks at 52-week highs
            - crossover_200d: DataFrame of stocks crossing 200-day MA
            - technical_errors: List of symbols with errors
    """
    from mod.data.fetcher import fetch_symbol_data
    import pandas as pd
    
    fifty_two_week_high = []
    crossover_200d = []
    technical_errors = []
    
    # Extract symbols if input is DataFrame
    if isinstance(symbols, pd.DataFrame):
        if 'symbol' in symbols.columns:
            symbol_list = symbols['symbol'].tolist()
        else:
            # Assume the DataFrame index contains symbols
            symbol_list = symbols.index.tolist()
    elif isinstance(symbols, list):
        symbol_list = symbols
    else:
        # Handle unexpected input type
        print(f"Warning: Unexpected type for symbols: {type(symbols)}")
        return [], [], ["Invalid input type"]
    
    for symbol in symbol_list:
        try:
            # Fetch 1-year data for calculating 52-week high
            data = fetch_symbol_data(symbol, period="1y", interval="1d")
            
            if data is not None and not data.empty:
                # Check for 52-week high
                current_price = data['Close'].iloc[-1]
                year_high = data['High'].max()
                
                # If price is within 2% of 52-week high
                if current_price >= year_high * 0.98:
                    fifty_two_week_high.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'year_high': year_high,
                        'pct_from_high': ((current_price - year_high) / year_high) * 100
                    })
                
                # Check for 200-day moving average crossover
                if len(data) >= 200:
                    # Calculate 200-day MA
                    data['MA200'] = data['Close'].rolling(window=200).mean()
                    
                    # Check if price crossed above MA200 recently (last 5 days)
                    if len(data) > 5:
                        recent_data = data.iloc[-5:]
                        prev_data = data.iloc[-10:-5]
                        
                        # Price was below MA200 before and is above now
                        prev_below = False
                        for _, row in prev_data.iterrows():
                            if row['Close'] < row['MA200']:
                                prev_below = True
                                break
                        
                        recent_above = True
                        for _, row in recent_data.iterrows():
                            if row['Close'] <= row['MA200']:  # Using <= instead of < for safety
                                recent_above = False
                                break
                        
                        if prev_below and recent_above:
                            crossover_200d.append({
                                'symbol': symbol,
                                'current_price': current_price,
                                'ma_200': data['MA200'].iloc[-1],
                                'days_above_ma': sum(1 for _, row in recent_data.iterrows() if row['Close'] > row['MA200'])
                            })
            else:
                technical_errors.append(f"{symbol}: No data")
        except Exception as e:
            print(f"Error analyzing technical patterns for {symbol}: {e}")
            technical_errors.append(f"{symbol}: {str(e)}")
    
    # Convert lists to DataFrames
    df_fifty_two_week_high = pd.DataFrame(fifty_two_week_high) if fifty_two_week_high else pd.DataFrame()
    df_crossover_200d = pd.DataFrame(crossover_200d) if crossover_200d else pd.DataFrame()
    
    return df_fifty_two_week_high, df_crossover_200d, technical_errors

def find_trading_opportunities(symbols, criteria='momentum'):
    """
    Find trading opportunities based on specified criteria.
    
    Args:
        symbols (list or pd.DataFrame): List of stock symbols or DataFrame with symbol column
        criteria (str): Criteria for finding opportunities ('momentum', 'value', 'trend')
        
    Returns:
        dict: Dictionary with buy and sell signals
    """
    from mod.data.fetcher import fetch_symbol_data
    import pandas as pd
    
    opportunities = []
    errors = []
    
    # Extract symbols if input is DataFrame
    if isinstance(symbols, pd.DataFrame):
        if 'symbol' in symbols.columns:
            symbol_list = symbols['symbol'].tolist()
        else:
            # Assume the DataFrame index contains symbols
            symbol_list = symbols.index.tolist()
    else:
        symbol_list = symbols
    
    for symbol in symbol_list:
        try:
            # Fetch data for analysis
            data = fetch_symbol_data(symbol, period="3mo", interval="1d")
            
            if data is not None and not data.empty and len(data) > 20:
                current_price = data['Close'].iloc[-1]
                
                # Calculate various indicators
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['MA50'] = data['Close'].rolling(window=50).mean()
                
                # Relative strength (ratio to index)
                sp500 = fetch_symbol_data('^GSPC', period="3mo", interval="1d")
                if sp500 is not None and not sp500.empty and len(sp500) > 20:
                    # Normalize both to 100 at the start
                    norm_stock = data['Close'] / data['Close'].iloc[0] * 100
                    norm_sp500 = sp500['Close'] / sp500['Close'].iloc[0] * 100
                    
                    # Calculate relative strength
                    rel_strength = norm_stock.iloc[-1] / norm_sp500.iloc[-1]
                else:
                    rel_strength = 1.0
                
                # Calculate volume trend
                avg_volume = data['Volume'].mean()
                recent_volume = data['Volume'].iloc[-5:].mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Calculate volatility (standard deviation of daily returns)
                data['Returns'] = data['Close'].pct_change()
                volatility = data['Returns'].std() * 100  # Convert to percentage
                
                # Check for criteria
                opportunity = False
                reason = ""
                signal_type = "neutral"
                
                if criteria == 'momentum':
                    # Momentum criteria: Price > MA20, MA20 > MA50, Good RS, Increasing volume
                    if (current_price > data['MA20'].iloc[-1] and 
                        data['MA20'].iloc[-1] > data['MA50'].iloc[-1] and 
                        rel_strength > 1.05 and 
                        volume_ratio > 1.2):
                        opportunity = True
                        reason = "Strong momentum with good relative strength and increasing volume"
                        signal_type = "buy"
                
                elif criteria == 'value':
                    # Simple value criteria: Price < MA50 but RS is good, low volatility
                    if (current_price < data['MA50'].iloc[-1] and 
                        rel_strength > 0.95 and 
                        volatility < 2.0):
                        opportunity = True
                        reason = "Potential value opportunity with stable price action"
                        signal_type = "sell"
                
                elif criteria == 'trend':
                    # Trend following: Price above both MAs, MAs in proper order, and RS > 1
                    if (current_price > data['MA20'].iloc[-1] > data['MA50'].iloc[-1] and 
                        rel_strength > 1.0):
                        opportunity = True
                        reason = "Strong uptrend with good market performance"
                        signal_type = "buy"
                
                # If opportunity found, add to results
                if opportunity:
                    opportunities.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'criteria': criteria,
                        'reason': reason,
                        'signal_type': signal_type,
                        'rel_strength': rel_strength,
                        'volume_ratio': volume_ratio,
                        'volatility': volatility
                    })
        
        except Exception as e:
            print(f"Error finding opportunities for {symbol}: {e}")
            errors.append(f"{symbol}: {str(e)}")
    
    # Create DataFrame from results
    df_opportunities = pd.DataFrame(opportunities)
    
    # Split into buy and sell signals
    buy_signals = []
    sell_signals = []
    
    if not df_opportunities.empty:
        # Sort by relative strength
        df_opportunities = df_opportunities.sort_values('rel_strength', ascending=False)
        
        # Extract buy and sell signals
        buy_df = df_opportunities[df_opportunities['signal_type'] == 'buy']
        sell_df = df_opportunities[df_opportunities['signal_type'] == 'sell']
        
        # Convert to records format
        buy_signals = buy_df.to_dict('records') if not buy_df.empty else []
        sell_signals = sell_df.to_dict('records') if not sell_df.empty else []
    
    # Return as dictionary
    return {
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'errors': errors
    }

def get_market_summary():
    """
    Fetches a brief summary for the S&P 500 as placeholder implementation.
    """
    import yfinance as yf
    from datetime import datetime

    ticker = yf.Ticker('^GSPC')
    hist = ticker.history(period='2d')
    if hist.empty or len(hist) < 2:
        return {
            'sp500_value': 'N/A',
            'sp500_date': datetime.now().strftime("%Y-%m-%d"),
            'sp500_pct_change': 'N/A'
        }
    latest = hist['Close'][-1]
    previous = hist['Close'][-2]
    pct_change = ((latest - previous) / previous) * 100

    return {
        'sp500_value': f"{latest:.2f}",
        'sp500_date': hist.index[-1].strftime("%Y-%m-%d"),
        'sp500_pct_change': f"{pct_change:.2f}"
    }

def analyze_sector_performance():
    """
    Analyze the performance of market sectors.
    
    Returns:
        pd.DataFrame: DataFrame with sector performance
    """
    # Sector ETFs
    sectors = {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLV': 'Healthcare',
        'XLC': 'Communication Services',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLI': 'Industrials',
        'XLB': 'Materials',
        'XLU': 'Utilities',
        'XLRE': 'Real Estate',
        'XLE': 'Energy'
    }
    
    results = []
    
    for symbol, sector in sectors.items():
        try:
            # Get data for 1 month and 3 months
            data = yf.download(symbol, period="3mo", interval="1d", progress=False)
            
            if not data.empty and len(data) > 20:
                current_price = data['Close'].iloc[-1]
                one_day_ago = data['Close'].iloc[-2]
                one_week_ago = data['Close'].iloc[-5] if len(data) >= 5 else data['Close'].iloc[0]
                one_month_ago = data['Close'].iloc[-20] if len(data) >= 20 else data['Close'].iloc[0]
                three_months_ago = data['Close'].iloc[0]
                
                # Calculate percent changes
                daily_change = ((current_price - one_day_ago) / one_day_ago) * 100
                weekly_change = ((current_price - one_week_ago) / one_week_ago) * 100
                monthly_change = ((current_price - one_month_ago) / one_month_ago) * 100
                three_month_change = ((current_price - three_months_ago) / three_months_ago) * 100
                
                # Calculate relative strength vs S&P 500
                sp500 = yf.download('^GSPC', period="3mo", interval="1d", progress=False)
                if not sp500.empty and len(sp500) > 20:
                    sp_current = sp500['Close'].iloc[-1]
                    sp_three_months_ago = sp500['Close'].iloc[0]
                    sp_change = ((sp_current - sp_three_months_ago) / sp_three_months_ago) * 100
                    
                    # Relative performance
                    rel_strength = three_month_change - sp_change
                else:
                    rel_strength = 0
                
                results.append({
                    'sector': sector,
                    'symbol': symbol,
                    'current_price': current_price,
                    'daily_change': daily_change,
                    'weekly_change': weekly_change,
                    'monthly_change': monthly_change,
                    'three_month_change': three_month_change,
                    'rel_strength': rel_strength
                })
        except Exception as e:
            print(f"Error analyzing sector {sector}: {e}")
    
    # Create DataFrame
    df_sectors = pd.DataFrame(results)
    
    # Sort by 3-month performance
    if not df_sectors.empty:
        df_sectors = df_sectors.sort_values('three_month_change', ascending=False)
    
    return df_sectors

def volume_analysis(symbols):
    """
    Analyze trading volume patterns.
    
    Args:
        symbols (list or pd.DataFrame): List of stock symbols or DataFrame with symbol column
        
    Returns:
        pd.DataFrame: DataFrame with volume analysis
    """
    from mod.data.fetcher import fetch_symbol_data
    
    results = []
    
    # Extract symbols if input is DataFrame
    if isinstance(symbols, pd.DataFrame):
        if 'symbol' in symbols.columns:
            symbol_list = symbols['symbol'].tolist()
        else:
            # Assume the DataFrame index contains symbols
            symbol_list = symbols.index.tolist()
    else:
        symbol_list = symbols
    
    for symbol in symbol_list:
        try:
            # Fetch data for the symbol
            data = fetch_symbol_data(symbol, period="1mo", interval="1d")
            
            if data is not None and not data.empty and len(data) > 5:
                # Calculate average volume
                avg_volume = data['Volume'].mean()
                recent_volume = data['Volume'].iloc[-5:].mean()
                
                # Calculate volume ratio
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Find volume spikes (days with volume > 2x average)
                volume_spikes = (data['Volume'] > 2 * avg_volume).sum()
                
                # Calculate price correlation with volume
                if 'Close' in data.columns and 'Volume' in data.columns:
                    price_vol_corr = data['Close'].corr(data['Volume'])
                else:
                    price_vol_corr = 0
                
                # Get current price and recent change
                current_price = data['Close'].iloc[-1]
                recent_change = ((current_price - data['Close'].iloc[-5]) / data['Close'].iloc[-5]) * 100 if len(data) >= 5 else 0
                
                results.append({
                    'symbol': symbol,
                    'current_price': current_price,
                    'recent_change': recent_change,
                    'avg_volume': avg_volume,
                    'recent_volume': recent_volume,
                    'volume_ratio': volume_ratio,
                    'volume_spikes': volume_spikes,
                    'price_vol_corr': price_vol_corr
                })
        except Exception as e:
            print(f"Error analyzing volume for {symbol}: {e}")
    
    # Create DataFrame
    df_volume = pd.DataFrame(results)
    
    # Sort by volume ratio (descending)
    if not df_volume.empty:
        df_volume = df_volume.sort_values('volume_ratio', ascending=False)
    
    return df_volume