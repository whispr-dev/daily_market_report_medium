import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime
from sendemail import send_email
import base64
from io import BytesIO

# Load stocks list
stocks = pd.read_csv('stocks_universe.csv')['Symbol'].tolist()

# Get today's date explicitly
today = datetime.today().strftime('%Y-%m-%d')

# Get data for ^GSPC for 6-month plot
spy = yf.download('^GSPC', period='6mo', interval='1d')
latest_close = float(spy['Adj Close'][-1])
latest_date = spy.index[-1].strftime('%Y-%m-%d')

html_content = f"""
<html>
<head>
    <title>S&P 500 Daily Report</title>
</head>
<body>
    <h1 style="color: #0000FF;">S&P 500 Ticker ^GSPC {latest_close:.2f} Date: {latest_date}</h1>
"""

# Check for 52-week high
spy_52week = yf.download('^GSPC', period='1y', interval='1d')
is_52week_high = latest_close >= spy['Adj Close'].max()
html_content += f"<h2>52-week high</h2><p>{'52-week high reached!' if is_52week_high else 'No stocks found.'}</p>"

# Trend chart for S&P 500
spy['Adj Close'].plot(title='S&P 500 - Last 6 Months')
plt.grid(True)
plt.title("S&P 500 - Last 6 Months")
plt.ylabel("Adjusted Close Price")
plt.xlabel("Date")
plt.tight_layout()
plt.savefig("sp500_trend.png")
plt.close()

html_content += f"<h3>S&P 500 Trend (6 Months)</h3><img src='sp500_trend.png'>"

# Load your stocks from CSV
stocks_df = pd.read_csv('stocks_universe.csv')
stocks = stocks_df.iloc[:, 0].tolist()  # Assumes Tickers are in the first column

magic_reversal_signals = []
cross_over_ma200 = []
errors = []

for ticker in stocks_df:
    try:
        df = yf.download(ticker, period="1y", interval="1d")
        
        if df.empty or len(df) < 200:
            continue  # Skip insufficient data
        
        df['MA200'] = df['Adj Close'].rolling(window=200).mean()

        # Magic Reversal logic
        df['change'] = df['Adj Close'].pct_change()
        df['prev_change'] = df['change'].shift(1)
        df['reversal_signal'] = (df['change'] < 0) & (df['change'].shift(-1) > 0)

        if df['change'].iloc[-1] < -0.03 and df['change'].iloc[-2] < 0:
            html_content += f"<h3>Magic Reversal Signal: {stock}</h3>"
            mpf.plot(df.tail(30), type='candle', mav=(5, 10), volume=True, savefig=f"{stock}_magic_reversal.png")
            html_content += f"<img src='{stock}_magic_reversal.png'>"

        # Cross over MA200 logic
        prev_close, current_close = df['Adj Close'].iloc[-2], df['Adj Close'].iloc[-1]
        prev_ma200 = df['MA200'].iloc[-2]
        curr_ma200 = df['MA200'].iloc[-1]

        if latest_close > curr_ma200 and df['Adj Close'].iloc[-2] < df['MA200'].iloc[-2]:
            html_content += f"<h3>{stock} crossed above MA200!</h3>"
        elif latest_close < curr_ma200 and df['Adj Close'].iloc[-2] > df['MA200'].iloc[-2]:
            html_content += f"<h3>{stock} crossed below MA200!</h3>"

    except Exception as e:
        html_content += f"<p>Error fetching data for {stock}: {str(e)}</p>"

# Final HTML and email setup
html_content += "</body></html>"

# Load your email template and insert dynamic content
with open('email_template.html', 'r') as f:
    email_template = f.read()

email_template = email_template.replace("{{content}}", html_content)

# Save to file
with open('local_output.html', 'w') as file:
    file.write(email_template)

# Send the email with HTML content
send_email("your_email@example.com", "Daily Stock Report", email_template, attachments=["sp500_trend.png"])

print("Done, fren! Check your email!")
