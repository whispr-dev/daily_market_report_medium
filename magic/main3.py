import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime, timedelta
from io import BytesIO
import base64
from sendemail import send_email

# Load stock universe
stocks = pd.read_csv('stocks_universe.csv')['Ticker'].tolist()

# Today's date
today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# DataFrames to store results
high_52week = []
ma_cross_200 = []
magic_reversal_signals = []
error_stocks = []

# Fetching stock data
def fetch_stock_data(ticker, period="1y"):
    try:
        stock = yf.download(ticker, period=period)
        return stock if not stock.empty else None
    except Exception as e:
        error_stocks.append((ticker, str(e)))
        return None

# Magic Reversal Indicator
def magic_reversal(stock_df):
    stock_df['prev_close'] = stock_df['Close'].shift(1)
    condition_bullish = (stock_df['Close'] > stock_df['Open']) & (stock_df['prev_close'] < stock_df['Open'])
    condition_bearish = (stock_df['Close'] < stock_df['Open']) & (stock_df['prev_close'] > stock_df['Open'])
    signal = condition_bullish | condition_bearish
    return stock_df[signal]

# Generate candlestick chart
def plot_candlestick(stock_df, ticker):
    fig, ax = plt.subplots(figsize=(10,5))
    stock_df['Date'] = mdates.date2num(stock_df.index)
    ohlc = stock_df[['Date', 'Open', 'High', 'Low', 'Close']].values
    from mplfinance.original_flavor import candlestick_ohlc
    candlestick_ohlc(ax, ohlc, width=0.6, colorup='green', colordown='red')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.set_title(f'{ticker} Magic Reversal Candlestick Chart')
    plt.xticks(rotation=45)
    plt.grid(True)
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img_base64

# Check each stock
for ticker in stocks:
    data = fetch_stock_data(ticker)

    if data is None:
        continue

    # Check 52-week high
    if data['Close'].iloc[-1] >= data['Close'].rolling(window=252).max().iloc[-1]:
        high_52week.append(ticker)

    # Check moving average crossover
    data['MA200'] = data['Close'].rolling(window=200).mean()
    if data['Close'][-2] < data['MA200'][-2] and data['Close'][-1] > data['MA200'][-1]:
        ma_cross_200.append(ticker)

    # Check Magic Reversal
    magic_signal = magic_reversal(data.tail(3))
    if not magic_signal.empty:
        magic_reversal_signals.append((ticker, magic_signal))

# Generate Magic Reversal chart for first found ticker
magic_reversal_chart = None
if magic_reversal_signals:
    ticker_chart, df_chart = magic_reversal_signals[0]
    magic_reversal_chart = plot_candlestick(df_chart, ticker_chart)

# Prepare HTML
html_template = open('email_template.html', 'r').read()

# Replacing placeholders
html_template = html_template.replace('{{DATE}}', today)

html_template = html_template.replace('{{52_WEEK_HIGH}}',
    ', '.join(high_52week) if high_52week else 'No stocks found.')

html_template = html_template.replace('{{MAGIC_REVERSAL_SIGNALS}}',
    ', '.join([t[0] for t in magic_reversal_signals]) if magic_reversal_signals else 'No Magic Reversal signals found today, fren!')

html_template = html_template.replace('{{MA_CROSS_200}}',
    ', '.join(ma_cross_200) if ma_cross_200 else 'No stocks found.')

html_template = html_template.replace('{{ERROR_STOCKS}}',
    '<br>'.join([f"{t[0]} - {t[1]}" for t in error_stocks]) if error_stocks else 'No errors.')

if magic_reversal_chart:
    img_tag = f'<img src="data:image/png;base64,{magic_reversal_chart}" alt="Magic Reversal Candlestick">'
else:
    img_tag = "<p>No Magic Reversal chart available today.</p>"

html_template = html_template.replace('{{MAGIC_REVERSAL_CHART}}', img_tag)

# Save for debugging
with open('local_output.html', 'w') as f:
    f.write(html_template)

# Send email
send_email(subject='📈 Daily Stock Report 📉', body_html=html_template)

print("Done, fren! Email sent.")
