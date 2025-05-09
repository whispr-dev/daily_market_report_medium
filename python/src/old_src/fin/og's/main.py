import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pandas_datareader import data as pdr

import base64
import io
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from jinja2 import Environment, FileSystemLoader
from sendemail import send_email
from datetime import datetime, timedelta

def img_to_base64(fig):
    """Utility to convert a Matplotlib figure to base64-encoded PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_candlestick_chart():
    """Download 6mo of ^GSPC, produce a candlestick chart, return base64."""
    df = yf.download("^GSPC", period="6mo", interval="1d", progress=False)
    if df.empty:
        print("Warning: ^GSPC candlestick data is empty.")
        return None

    # Some versions of yfinance return multi-index columns, so flatten
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # We only need these columns for mplfinance
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    for c in required_cols:
        if c not in df.columns:
            print(f"Warning: {c} column missing in ^GSPC for candlestick chart.")
            return None

    # Coerce to numeric
    df = df[required_cols].apply(pd.to_numeric, errors='coerce').dropna()

    df.index.name = 'Date'
    try:
        fig, _ = mpf.plot(df, type='candle', style='charles', volume=True, returnfig=True)
        return img_to_base64(fig)
    except Exception as e:
        print("Candlestick plot error:", e)
        return None

def generate_sector_heatmap(df_universe):
    # Force numeric
    df_universe['pct_change'] = pd.to_numeric(df_universe['pct_change'], errors='coerce')
    df_universe.dropna(subset=['pct_change', 'sector'], inplace=True)

    pivoted = df_universe.pivot_table(
        index='sector', 
        columns='symbol', 
        values='pct_change', 
        aggfunc='mean'
    )

    if pivoted.empty:
        print("Warning: Sector heatmap data is empty. Skipping.")
        return None

    # Convert pivoted to float
    pivoted = pivoted.apply(pd.to_numeric, errors='coerce').fillna(0)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivoted, annot=True, cmap='RdYlGn', center=0, fmt=".2f", linewidths=.5, ax=ax)
    plt.title("Sector Performance - Daily % Change")

    return img_to_base64(fig)

def generate_macro_chart():
    """
    Download 6 months of data for S&P (Close or Adj Close),
    BTC-USD, and US M2 from FRED. Then produce a single line chart
    comparing them all. Also does a simple 6-month forecast for the S&P.
    """
    end = datetime.today()
    start = end - timedelta(days=180)

    df_spx = yf.download("^GSPC", start=start, progress=False)
    df_btc = yf.download("BTC-USD", start=start, progress=False)

    # US M2 from FRED
    try:
        df_m2 = pdr.DataReader("M2SL", "fred", start)
    except Exception as e:
        print("Warning: M2SL DataReader error:", e)
        df_m2 = pd.DataFrame()

    # Flatten if multi-index
    if isinstance(df_spx.columns, pd.MultiIndex):
        df_spx.columns = df_spx.columns.droplevel(1)
    if isinstance(df_btc.columns, pd.MultiIndex):
        df_btc.columns = df_btc.columns.droplevel(1)

    # Pick Close or Adj Close if available
    spx_col = "Adj Close" if "Adj Close" in df_spx.columns else "Close"
    btc_col = "Adj Close" if "Adj Close" in df_btc.columns else "Close"

    # If either is empty, skip
    if df_spx.empty or spx_col not in df_spx.columns:
        print("Warning: ^GSPC macro chart missing data.")
        return None
    if df_btc.empty or btc_col not in df_btc.columns:
        print("Warning: BTC macro chart missing data.")
        return None
    if df_m2.empty or 'M2SL' not in df_m2.columns:
        print("Warning: M2 data is empty. Skipping M2 in macro chart.")
        df_m2['M2SL'] = np.nan

    df = pd.DataFrame({
        "S&P 500": df_spx[spx_col],
        "BTC": df_btc[btc_col],
        "M2": df_m2["M2SL"]
    })

    df = df.ffill().dropna(how='any')
    if df.empty:
        print("Warning: Not enough macro data to plot.")
        return None

    # Optional short forecast for S&P
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        model = ExponentialSmoothing(df["S&P 500"], trend='add', seasonal=None)
        fit = model.fit()
        forecast_steps = 60  # ~3 months
        forecast = fit.forecast(steps=forecast_steps)
    except Exception as e:
        print("Forecast error:", e)
        forecast = None

    fig, ax = plt.subplots(figsize=(10, 5))
    df.plot(ax=ax, linewidth=1.5)

    if forecast is not None and not forecast.empty:
        forecast.index = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=forecast_steps, freq='B')
        forecast_df = pd.DataFrame({"S&P 500 Forecast": forecast})
        forecast_df.plot(ax=ax, style="--", color="blue")

    ax.set_title("Macro Trends: S&P 500 vs BTC vs M2 (6mo + short forecast)")
    ax.set_ylabel("Value")
    ax.grid(True)

    return img_to_base64(fig)

def main():
    # 1) Read CSV, ensure 'symbol' column
    df_universe = pd.read_csv("stocks_universe.csv")
    df_universe.columns = df_universe.columns.str.strip().str.lower()

    if 'symbol' not in df_universe.columns:
        raise KeyError("The 'symbol' column is missing from stocks_universe.csv")

    # 2) Build daily % change for each symbol => populate df_universe['pct_change']
    changes = []
    for sym in df_universe['symbol']:
        try:
            data = yf.download(sym, period='2d', progress=False)
            if data.empty:
                changes.append(np.nan)
                continue
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
        except:
            changes.append(np.nan)

    df_universe['pct_change'] = changes

    # 3) Determine 52-week highs and 200d cross
    fifty_two_week_high = []
    crossover_200d = []
    fails = []
    for sym in df_universe['symbol']:
        try:
            df_data = yf.download(sym, period='1y', progress=False)
            if df_data.empty: 
                raise ValueError("No data returned")

            # prefer Adj Close
            if 'Adj Close' in df_data.columns:
                closes = df_data['Adj Close'].dropna()
            else:
                closes = df_data['Close'].dropna()

            if len(closes) < 2:
                raise ValueError("Not enough data")

            current_price = closes.iloc[-1]
            max_52wk = closes.max()
            if np.isclose(current_price, max_52wk, atol=0.01) or current_price >= max_52wk:
                fifty_two_week_high.append(sym)

            if len(closes) >= 200:
                ma200 = closes.rolling(200).mean()
                if current_price > ma200.iloc[-1]:
                    crossover_200d.append(sym)
        except Exception as e:
            fails.append((sym, str(e)))

    # 4) Gather S&P 500 stats for the email
    spx = yf.download("^GSPC", period='2d', progress=False)
    sp500_value = 0
    sp500_pct_change = 0
    sp500_date = ""
    if not spx.empty and 'Close' in spx.columns:
        sp500_value = spx['Close'].iloc[-1]
        sp500_date = str(spx.index[-1].date())
        if len(spx) > 1:
            sp500_pct_change = (spx['Close'].iloc[-1] - spx['Close'].iloc[-2]) / spx['Close'].iloc[-2] * 100.0

    # 5) Generate charts
    candle_b64 = generate_candlestick_chart()
    heatmap_b64 = generate_sector_heatmap(df_universe)
    macro_b64 = generate_macro_chart()

    # 6) Render template
    env = Environment(loader=FileSystemLoader("."))
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

    # 7) Send email
    send_email("Daily Stonk Market Report", html_output)

if __name__ == "__main__":
    main()
