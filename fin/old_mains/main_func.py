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
            if 'sector' not in df_universe.columns:
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
        for sym in df_universe['symbol']:
            try:
                data = yf.download(sym, period='2d', progress=False)
                if data.empty:
                    changes.append(np.nan)
                    continue
                    
                # Handle multi-index columns
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [col[1] if col[1] else col[0] for col in data.columns]
                
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
        
        for sym in df_universe['symbol']:
            try:
                df_data = yf.download(sym, period='1y', progress=False)
                if df_data.empty: 
                    fails.append((sym, "No data returned"))
                    continue

                # Handle multi-index columns
                if isinstance(df_data.columns, pd.MultiIndex):
                    df_data.columns = [col[1] if col[1] else col[0] for col in df_data.columns]

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
                    # Check if price crossed above MA recently
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
                    spx.columns = [col[1] if col[1] else col[0] for col in spx.columns]
                
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
        print("Generating charts...")
        candle_b64 = generate_candlestick_chart()
        heatmap_b64 = generate_sector_heatmap(df_universe)
        macro_b64 = generate_macro_chart()

        # 6) Render template
        print("Rendering HTML template...")
        env = Environment(loader=FileSystemLoader("."))
        try:
            template = env.get_template("email_template.html")
            
            html_output = template.render(
                sp500_value=sp500_value,
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