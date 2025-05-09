def generate_macro_chart():
    """
    Download 6 months of data for S&P (Close or Adj Close),
    BTC-USD, and US M2 from FRED. Then produce a single line chart
    comparing them all. Also does a simple 6-month forecast for the S&P.
    """
    end = datetime.today()
    start = end - timedelta(days=180)
    
    # Get S&P 500 data
    try:
        df_spx = yf.download("^GSPC", start=start, progress=False)
        # Flatten if multi-index
        if isinstance(df_spx.columns, pd.MultiIndex):
            df_spx.columns = df_spx.columns.droplevel(0)
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
        # Flatten if multi-index
        if isinstance(df_btc.columns, pd.MultiIndex):
            df_btc.columns = df_btc.columns.droplevel(0)
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
            df_m2 = pd.DataFrame(index=df_spx.index)
            df_m2['M2SL'] = np.nan
    except Exception as e:
        print(f"Warning: M2SL DataReader error: {e}")
        # Create empty DataFrame with same index as S&P
        df_m2 = pd.DataFrame(index=df_spx.index)
        df_m2['M2SL'] = np.nan
    
    # Combine into a single DataFrame
    try:
        df = pd.DataFrame({
            "S&P 500": df_spx[spx_col],
            "BTC": df_btc[btc_col],
            "M2": df_m2["M2SL"]
        })
        
        # Forward fill missing values and drop any remaining NaNs
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
                    df_normalized[col] = df[col] / df[col].loc[first_valid] * 100
        
        # Only keep the columns that have data
        df_normalized = df_normalized.dropna(axis=1, how='all')
    except Exception as e:
        print(f"Error preparing data for macro chart: {e}")
        return None
    
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
    
    # Create the plot
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Plot the data
        for col in df_normalized.columns:
            df_normalized[col].dropna().plot(ax=ax, linewidth=1.5, label=col)
        
        # Add forecast if available
        if forecast is not None and not forecast.empty:
            last_date = df_normalized.index[-1]
            forecast_index = pd.date_range(
                last_date + pd.Timedelta(days=1), 
                periods=len(forecast), 
                freq='B'
            )
            forecast = pd.Series(forecast.values, index=forecast_index)
            forecast.plot(ax=ax, style="--", color="blue", label="S&P 500 Forecast")
        
        ax.set_title("Macro Trends: S&P 500 vs BTC vs M2 (6mo + short forecast)")
        ax.set_ylabel("Normalized Value (%)")
        ax.grid(True)
        ax.legend()
        
        return img_to_base64(fig)
    except Exception as e:
        print(f"Error creating macro chart: {e}")
        return None