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
        import traceback
        traceback.print_exc()
        return None


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
                
                df_data = yf.download(sym, period='1y', progress=False)
                if df_data.empty: 
                    fails.append((sym, "No data returned"))
                    continue

                # Handle multi-index columns
                if isinstance(df_data.columns, pd.MultiIndex):
                    df_data.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df_data.columns]

                # prefer Adj Close
                col = 'Adj Close' if 'Adj Close' in df_data.columns else 'Close'
                closes = df_data[col].dropna()

                if len(closes) < 2:
                    fails.append((sym, "Not enough data"))
                    continue

                current_price = closes.iloc[-1]
                max_52wk = closes.max()
                
                # Check for 52-week high
                if np.isclose(current_price, max_52wk, atol=0.01) or current_price >= max_52wk * 0.99:
                    fifty_two_week_high.append(sym)

                # Check for 200-day MA crossover (only if we have enough data)
                if len(closes) >= 200:
                    ma200 = closes.rolling(200).mean()
                    # Check if price crossed above MA recently (within last 5 days)
                    if (closes.iloc[-1] > ma200.iloc[-1]) and (closes.iloc[-5] <= ma200.iloc[-5]):
                        crossover_200d.append(sym)
                        
            except Exception as e:
                fails.append((sym, str(e)))

        # 4) Gather S&P 500 stats for the email
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

        # 5) Generate charts
        print("Generating candlestick chart...")
        candle_b64 = generate_candlestick_chart()
        
        print("Generating sector heatmap...")
        heatmap_b64 = generate_sector_heatmap(df_universe)
        
        print("Generating macro chart...")
        macro_b64 = generate_macro_chart()

        # 6) Render template
        print("Rendering HTML template...")
        env = Environment(loader=FileSystemLoader("."))
        try:
            template = env.get_template("email_template.html")
            
            html_output = template.render(
                sp500_value=f"{sp500_value:.2f}" if isinstance(sp500_value, float) else sp500_value,
                sp500_date=sp500_date,
                sp500_pct_change=sp500_pct_change,
                candle_chart=candle_b64,
                heatmap=heatmap_b64,
                macro_chart=macro_b64,
                fifty_two_week_high=fifty_two_week_high,
                crossover_200d=crossover_200d,
                failed_stocks=fails
            )
            
            # Save a local copy of the report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"report_{timestamp}.html"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(html_output)
            print(f"HTML report saved as {report_filename}")
            
            # 7) Send email
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
        import traceback
        traceback.print_exc()
    
    print("Daily Stonk Market Report generation completed.")

if __name__ == "__main__":
    main()import yfinance as yf
