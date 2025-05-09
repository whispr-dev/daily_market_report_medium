import pandas as pd
import yfinance as yf
from sendemail import send_email
from jinja2 import Template
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64

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

def main():
    stocks = pd.read_csv('stocks_universe.csv')
    stocks = stocks[
        (stocks['CapCategory'] == 'mega') |
        (stocks['sector'].isin(['Technology', 'Financial Services']))
    ]

    errors = []
    l_52w_high = []
    crossover_sma = []
    crossover_sma_days = 200
    data = {
        'crossover_sma_days': crossover_sma_days,
    }

    current_date = datetime.now()
    start_date = (current_date + timedelta(days=-2*365)).strftime("%Y-%m-%d")

    for idx, row in stocks.iterrows():
        stock = row['symbol']
        try:
            df = yf.download(stock, start=start_date, auto_adjust=False)

            if df.empty or 'Adj Close' not in df.columns:
                errors.append({'stock': stock, 'error': "No Adj Close data returned"})
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(stock, level=1, axis=1)

            df.drop_duplicates(inplace=True)
            df.sort_index(inplace=True)

            df['pct_change'] = df['Adj Close'].pct_change()
            df['roll_max'] = df['Adj Close'].rolling(window=252, min_periods=1).max()
            df['52W_high'] = df['Adj Close'] == df['roll_max']
            df['52W_high_count'] = df['52W_high'].rolling(window=22, min_periods=1).sum()

            if len(df) > 0 and df['52W_high'].iloc[-1]:
                l_52w_high.append({
                    'ticker': stock,
                    'name': row['shortName'],
                    'sector_industry': f'{row["sector"]} / {row["industry"]}',
                    'cap': row['CapCategory'],
                    'close': round(df['Adj Close'].iloc[-1], 2),
                    'pct_change': round(df['pct_change'].iloc[-1] * 100, 2),
                    'last_month_52highs': df['52W_high_count'].iloc[-1]
                })

            sma_col = f"sma_{crossover_sma_days}"
            df[sma_col] = df['Adj Close'].rolling(window=crossover_sma_days, min_periods=1).mean()

            if len(df) >= 2:
                if (
                    df['Adj Close'].iloc[-1] > df[sma_col].iloc[-1] and
                    df['Adj Close'].iloc[-2] < df[sma_col].iloc[-2]
                ):
                    crossover_sma.append({
                        'ticker': stock,
                        'name': row['shortName'],
                        'sector_industry': f'{row["sector"]} / {row["industry"]}',
                        'cap': row['CapCategory'],
                        'close': round(df['Adj Close'].iloc[-1], 2),
                        'pct_change': round(df['pct_change'].iloc[-1] * 100, 2)
                    })

        except Exception as e:
            errors.append({'stock': stock, 'error': str(e)})

    # S&P 500 Analysis & Plot
    sp500_plot_base64 = ""
    try:
        df_spx = yf.download('^GSPC', start=start_date, auto_adjust=False)
        if df_spx.empty or 'Adj Close' not in df_spx.columns:
            errors.append({'stock': '^GSPC', 'error': "No Adj Close data returned"})
        else:
            df_spx.drop_duplicates(inplace=True)
            df_spx.sort_index(inplace=True)
            df_spx['pct_change'] = df_spx['Adj Close'].pct_change()
            data['sp500'] = round(df_spx['Adj Close'].iloc[-1], 2)
            data['sp_pct_change'] = round(df_spx['pct_change'].iloc[-1] * 100, 2)

            sp500_plot_base64 = generate_sp500_plot(df_spx)

    except Exception as e:
        errors.append({'stock': '^GSPC', 'error': str(e)})
        data['sp_pct_change'] = 0

    # Render Email
    with open('email_template.html', 'r') as file:
        html_template = file.read()

    template = Template(html_template)
    html_output = template.render(
        data_52w_high=l_52w_high,
        data_crossover=crossover_sma,
        errors=errors,
        data=data,
        sp500_plot=sp500_plot_base64
    )

    # Optional: Write a local HTML copy for preview
    with open("local_output.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    # Send the email
#   send_email("PwrUp Stonks Email!", html_output)

if __name__ == "__main__":
    main()
