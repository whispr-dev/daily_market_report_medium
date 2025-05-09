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
            
            if tech['error']:
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