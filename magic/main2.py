import pandas as pd
import numpy as np
import yfinance as yf
from sendemail import send_email
from jinja2 import Template
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
import os

########################################
# 1. Magic Reversal Indicator Functions
########################################
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(df, period=14):
    close = df['Close']
    delta = close.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    gain = pd.Series(gain, index=df.index)
    loss = pd.Series(loss, index=df.index)
    avg_gain = ema(gain, period)
    avg_loss = ema(loss, period)
    rs = avg_gain / (avg_loss + 1e-10)
    return 100.0 - (100.0 / (1.0 + rs))

def stoch_rsi(df, rsi_period=14, stoch_length=14, k_smooth=3, d_smooth=3):
    rsi_vals = rsi(df, period=rsi_period)
    lowest_rsi = rsi_vals.rolling(stoch_length).min()
    highest_rsi = rsi_vals.rolling(stoch_length).max()
    stoch_rsi_raw = (rsi_vals - lowest_rsi) / (highest_rsi - lowest_rsi + 1e-10)
    stoch_rsi_raw = stoch_rsi_raw.fillna(0)

    k = stoch_rsi_raw.rolling(k_smooth).mean()
    d = k.rolling(d_smooth).mean()
    return k * 100, d * 100

def engulfing_patterns(df):
    open_ = df['Open']
    close_ = df['Close']
    open_prev = df['Open'].shift(1)
    close_prev = df['Close'].shift(1)

    bull_engulf = (
        (close_ > open_) &
        (close_prev < open_prev) &
        (close_ > open_prev) &
        (open_ < close_prev)
    )
    bear_engulf = (
        (close_ < open_) &
        (close_prev > open_prev) &
        (close_ < open_prev) &
        (open_ > close_prev)
    )
    return bull_engulf, bear_engulf

def moving_average(df, period=50):
    return df['Close'].rolling(period).mean()

def magic_reversal_indicator(df,
                             rsi_period=14,
                             rsi_ob=70,
                             rsi_os=30,
                             stoch_len=14,
                             k_smooth=3,
                             d_smooth=3,
                             ma_period=50,
                             use_trend_filter=True):
    df = df.copy()
    df['RSI'] = rsi(df, period=rsi_period)
    df['StochK'], df['StochD'] = stoch_rsi(df,
                                           rsi_period=rsi_period,
                                           stoch_length=stoch_len,
                                           k_smooth=k_smooth,
                                           d_smooth=d_smooth)
    bull_engulf, bear_engulf = engulfing_patterns(df)
    df['BullishEngulfing'] = bull_engulf
    df['BearishEngulfing'] = bear_engulf
    df['MA'] = moving_average(df, period=ma_period)
    df['AboveMA'] = df['Close'] > df['MA']

    df['StochCrossUp'] = (df['StochK'] > df['StochD']) & (df['StochK'].shift(1) <= df['StochD'].shift(1))
    df['StochCrossDown'] = (df['StochK'] < df['StochD']) & (df['StochK'].shift(1) >= df['StochD'].shift(1))

    bull_cond = ((df['RSI'] < rsi_os) &
                 (df['StochCrossUp']) &
                 (df['BullishEngulfing']))
    if use_trend_filter:
        bull_cond = bull_cond & (df['AboveMA'])
    df['BullishSignal'] = bull_cond

    bear_cond = ((df['RSI'] > rsi_ob) &
                 (df['StochCrossDown']) &
                 (df['BearishEngulfing']))
    if use_trend_filter:
        bear_cond = bear_cond & (~df['AboveMA'])
    df['BearishSignal'] = bear_cond

    return df

##################################
# 2. Plot Reversal Signals
##################################
def plot_magic_reversal(df):
    df_plot = df.tail(60)  # show last 60 bars
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(df_plot.index, df_plot['Close'], label='Close', color='blue', linewidth=1.5)

    # Mark bullish signals
    bull_idx = df_plot.index[df_plot['BullishSignal']]
    ax.scatter(bull_idx, df_plot.loc[bull_idx, 'Close'], marker='^', color='green', s=100, label='Bullish')

    # Mark bearish signals
    bear_idx = df_plot.index[df_plot['BearishSignal']]
    ax.scatter(bear_idx, df_plot.loc[bear_idx, 'Close'], marker='v', color='red', s=100, label='Bearish')

    ax.set_title('Magic Reversal Signals (Last 60 bars)')
    ax.grid(True)
    ax.legend(loc='best')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return chart_base64

####################################
# 3. Flatten Multi-Level Columns
####################################
def flatten_columns(df):
    """
    If yfinance or merges produce multi-index columns, flatten them.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)
    return df

###################################
# 4. S&P 500 Plot
###################################
def generate_sp500_plot(df_spx):
    plt.figure(figsize=(10, 4))
    plt.plot(df_spx.index, df_spx['Adj Close'], label='S&P 500', linewidth=2)
    plt.title('S&P 500 - Last 6 Months')
    plt.xlabel('Date')
    plt.ylabel('Adjusted Close Price')
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

###################################
# 5. MAIN
###################################
def main():
    # Read the main stock universe
    stocks = pd.read_csv('stocks_universe.csv')
    # Optional filters:
    stocks = stocks[
        (stocks['CapCategory'] == 'mega') |
        (stocks['sector'].isin(['Technology', 'Financial Services']))
    ]

    # Optional: read your "progressed" future data if you have it
    # Must have columns Date, Open, High, Low, Close, Volume or similar
    progressed_df = None
    if os.path.exists("my_progressed_data.csv"):
        progressed_df = pd.read_csv("my_progressed_data.csv", parse_dates=['Date'])
        progressed_df.set_index('Date', inplace=True)
        progressed_df = flatten_columns(progressed_df)  # if multi-index
        # Make sure columns are: 'Open','High','Low','Close','Volume' (rename if needed)
        # progressed_df = progressed_df.rename(columns={...})

    errors = []
    l_52w_high = []
    crossover_sma = []
    crossover_sma_days = 200
    data = {
        'crossover_sma_days': crossover_sma_days,
    }
    magic_signals = []

    current_date = datetime.now()
    # Real data end date: yesterday or today
    # Real data start date: 2 years ago
    start_date = (current_date - timedelta(days=2*365)).strftime("%Y-%m-%d")
    end_date = current_date.strftime("%Y-%m-%d")

    # Loop each stock
    for idx, row in stocks.iterrows():
        stock = row['symbol']
        try:
            # Download real data from yfinance
            df_real = yf.download(stock, start=start_date, end=end_date, auto_adjust=False)
            df_real = flatten_columns(df_real)
            df_real.drop_duplicates(inplace=True)
            df_real.sort_index(inplace=True)

            # Merge with progressed data if relevant
            if progressed_df is not None:
                # Filter the progressed df for this symbol if you store them separately
                # For example, if your CSV has a 'symbol' column, you'd do:
                #   df_future = progressed_df[progressed_df['Symbol'] == stock].copy()
                # Here we just assume the entire progressed_df is for this symbol:
                df_future = progressed_df.copy()  # adapt as needed

                # Combine
                df_combined = pd.concat([df_real, df_future], axis=0)
                df_combined = df_combined[~df_combined.index.duplicated(keep='last')]
                df_combined.sort_index(inplace=True)
            else:
                df_combined = df_real

            # If we still have no columns or it's empty, skip
            if df_combined.empty or 'Adj Close' not in df_combined.columns:
                errors.append({'stock': stock, 'error': "No Adj Close data returned"})
                continue

            # 1) 52-week high logic
            df_combined['pct_change'] = df_combined['Adj Close'].pct_change()
            df_combined['roll_max'] = df_combined['Adj Close'].rolling(window=252, min_periods=1).max()
            df_combined['52W_high'] = df_combined['Adj Close'] == df_combined['roll_max']
            df_combined['52W_high_count'] = df_combined['52W_high'].rolling(window=22, min_periods=1).sum()

            if len(df_combined) > 0 and df_combined['52W_high'].iloc[-1]:
                l_52w_high.append({
                    'ticker': stock,
                    'name': row['shortName'],
                    'sector_industry': f'{row["sector"]} / {row["industry"]}',
                    'cap': row['CapCategory'],
                    'close': round(df_combined['Adj Close'].iloc[-1], 2),
                    'pct_change': round(df_combined['pct_change'].iloc[-1]*100, 2),
                    'last_month_52highs': df_combined['52W_high_count'].iloc[-1]
                })

            # 2) 200-day crossover
            sma_col = f"sma_{crossover_sma_days}"
            df_combined[sma_col] = df_combined['Adj Close'].rolling(window=crossover_sma_days, min_periods=1).mean()

            if len(df_combined) >= 2:
                # Check the last 2 bars for cross
                if (df_combined['Adj Close'].iloc[-1] > df_combined[sma_col].iloc[-1]
                    and df_combined['Adj Close'].iloc[-2] < df_combined[sma_col].iloc[-2]):
                    crossover_sma.append({
                        'ticker': stock,
                        'name': row['shortName'],
                        'sector_industry': f'{row["sector"]} / {row["industry"]}',
                        'cap': row['CapCategory'],
                        'close': round(df_combined['Adj Close'].iloc[-1], 2),
                        'pct_change': round(df_combined['pct_change'].iloc[-1]*100, 2)
                    })

            # 3) Magic Reversal
            # For the indicator, we need single-level columns: 'Open','High','Low','Close'
            # yfinance already provides them, we just rename to be consistent:
            df_combined.rename(columns={'Open':'Open','High':'High','Low':'Low','Close':'Close'}, inplace=True)

            indicator_df = magic_reversal_indicator(df_combined)

            if len(indicator_df) > 1:
                last_bull = indicator_df['BullishSignal'].iloc[-1]
                last_bear = indicator_df['BearishSignal'].iloc[-1]
                if last_bull or last_bear:
                    chart_b64 = plot_magic_reversal(indicator_df)
                    signal_str = "Bullish" if last_bull else "Bearish"
                    magic_signals.append({
                        'ticker': stock,
                        'name': row['shortName'],
                        'sector_industry': f'{row["sector"]} / {row["industry"]}',
                        'signal': signal_str,
                        'chart_base64': chart_b64
                    })

        except Exception as e:
            errors.append({'stock': stock, 'error': str(e)})

    # ============== S&P 500 Plot ==============
    sp500_plot_base64 = ""
    try:
        df_spx = yf.download('^GSPC', start=start_date, end=end_date, auto_adjust=False)
        df_spx = flatten_columns(df_spx)
        if df_spx.empty or 'Adj Close' not in df_spx.columns:
            errors.append({'stock': '^GSPC', 'error': "No Adj Close data returned"})
        else:
            df_spx.drop_duplicates(inplace=True)
            df_spx.sort_index(inplace=True)
            df_spx['pct_change'] = df_spx['Adj Close'].pct_change()
            # Store last close & % change
            sp500_last = df_spx['Adj Close'].iloc[-1] if len(df_spx) else 0
            sp500_change = df_spx['pct_change'].iloc[-1] * 100 if len(df_spx) else 0
            data['sp500'] = round(sp500_last, 2)
            data['sp_pct_change'] = round(sp500_change, 2)

            sp500_plot_base64 = generate_sp500_plot(df_spx)
    except Exception as e:
        errors.append({'stock': '^GSPC', 'error': str(e)})
        data['sp_pct_change'] = 0

    # Prepare final data dict for the HTML
    data['crossover_sma_days'] = crossover_sma_days

    # Render HTML from email_template
    with open('email_template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()

    template = Template(html_template)
    html_output = template.render(
        data_52w_high=l_52w_high,
        data_crossover=crossover_sma,
        data_magic=magic_signals,
        errors=errors,
        data=data,
        sp500_plot=sp500_plot_base64
    )

    # Optionally write a local HTML copy
    with open("local_output.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    # Send it
    # send_email("PwrUp Stonks Email!", html_output)

if __name__ == "__main__":
    main()
