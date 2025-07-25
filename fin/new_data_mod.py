def generate_multi_asset_report():
    """Generate a comprehensive report covering multiple asset classes."""
    # Get equity data (already implemented)
    equity_data = get_equity_market_data()
    
    # Add currency data
    currency_data = get_currency_data(['EURUSD=X', 'USDJPY=X', 'GBPUSD=X'])
    
    # Add ETF data
    etf_data = get_etf_data(['GDX', 'SPY', 'QQQ'])
    
    # Combine into comprehensive report
    return {
        'equity': equity_data,
        'currency': currency_data,
        'etfs': etf_data
    }

def get_currency_data(symbols):
    """Extract currency data similar to what's in Ticker_currency.ipynb."""
    results = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        results[sym] = {
            'current_rate': ticker.fast_info['lastPrice'],
            'day_change': (ticker.fast_info['lastPrice'] - ticker.fast_info['previousClose']) / ticker.fast_info['previousClose'] * 100,
            '50d_avg': ticker.fast_info['fiftyDayAverage'],
            '200d_avg': ticker.fast_info['twoHundredDayAverage']
        }
    return results

def get_etf_data(symbols):
    """Extract ETF data similar to what's in Ticker_ETF.ipynb."""
    results = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        info = ticker.info
        results[sym] = {
            'name': info.get('longName', ''),
            'yield': info.get('yield', 0) * 100 if 'yield' in info else 0,
            'category': info.get('category', ''),
            'ytd_return': info.get('ytdReturn', 0) * 100 if 'ytdReturn' in info else 0,
            'total_assets': info.get('totalAssets', 0)
        }
    return results