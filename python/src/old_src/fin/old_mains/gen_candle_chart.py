def generate_candlestick_chart():
    """Download 6mo of ^GSPC, produce a candlestick chart, return base64."""
    try:
        df = yf.download("^GSPC", period="6mo", interval="1d", progress=False)
        if df.empty:
            print("Warning: ^GSPC candlestick data is empty.")
            return None

        # Handle multi-index columns in yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[1] if col[1] else col[0] for col in df.columns]

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
        fig, _ = mpf.plot(df, type='candle', style='charles', volume=True, 
                         title="S&P 500 - 6 Month Candlestick Chart",
                         returnfig=True, figsize=(10, 6))
        return img_to_base64(fig)
    except Exception as e:
        print("Candlestick plot error:", e)
        return None