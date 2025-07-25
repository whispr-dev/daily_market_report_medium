def safe_download(symbol, period=None, start=None, end=None, interval='1d'):
    """Safely download data with better error handling."""
    try:
        # If using end parameter, make sure to specify start as well
        if end is not None and start is None:
            print(f"Warning: When using 'end' parameter, 'start' should also be specified for {symbol}")
            # Default to 1 year before end date
            end_date = pd.to_datetime(end)
            start = (end_date - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
        
        df = yf.download(symbol, period=period, start=start, end=end, 
                        interval=interval, progress=False)
        
        if df.empty:
            print(f"Warning: No data returned for {symbol}")
            return None
            
        return df
    except Exception as e:
        print(f"Error downloading {symbol}: {e}")
        return None