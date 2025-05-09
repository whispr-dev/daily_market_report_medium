def get_instrument_metadata(symbol):
    """Get metadata about a financial instrument."""
    try:
        ticker = yf.Ticker(symbol)
        metadata = ticker.history_metadata
        return {
            'currency': metadata.get('currency', 'Unknown'),
            'exchange': metadata.get('exchangeName', 'Unknown'),
            'type': metadata.get('instrumentType', 'Unknown'),
            'timezone': metadata.get('timezone', 'Unknown')
        }
    except Exception as e:
        print(f"Error getting metadata for {symbol}: {e}")
        return None