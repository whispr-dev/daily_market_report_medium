import pandas as pd
import yfinance as yf
from sendemail import send_email
from jinja2 import Template
from datetime import datetime, timedelta

def main():
    # Read the stocks and filter to the ones needed
    stocks = pd.read_csv('stocks_universe.csv')
    stocks = stocks[
        (stocks['CapCategory'] == 'mega') |
        (stocks['sector'].isin(['Technology', 'Financial Services']))
    ]

    # Config
    errors = []
    l_52w_high = []
    crossover_sma = []
    crossover_sma_days = 200
    data = {
        'crossover_sma_days': crossover_sma_days,
    }

    # Calculate start date (~2 years ago)
    current_date = datetime.now()
    start_date = (current_date + timedelta(days=-2*365)).strftime("%Y-%m-%d")

    # Loop over each stock
    for idx, row in stocks.iterrows():
        stock = row['symbol']
        try:
            # 1) Download this ticker individually, with Adj Close
            df = yf.download(stock, start=start_date, auto_adjust=False)

            # If we get an empty DF or no 'Adj Close', skip
            if df.empty or 'Adj Close' not in df.columns:
                errors.append({'stock': stock, 'error': "No Adj Close data returned"})
                continue

            # 2) If for some weird reason we have a multi-level column index, slice it
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(stock, level=1, axis=1)

            # 3) Clean up and sort by the index (Date)
            df.drop_duplicates(inplace=True)
            df.sort_index(inplace=True)

            # 4) Calculate daily percent change
            df['pct_change'] = df['Adj Close'].pct_change()

            # 5) Calculate 52-week rolling high
            df['roll_max'] = df['Adj Close'].rolling(window=252, min_periods=1).max()
            df['52W_high'] = df['Adj Close'] == df['roll_max']
            df['52W_high_count'] = df['52W_high'].rolling(window=22, min_periods=1).sum()

            # If we just hit a new 52W high on the last day
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

            # 6) Check for a 200-day SMA crossover
            sma_col = f"sma_{crossover_sma_days}"
            df[sma_col] = df['Adj Close'].rolling(window=crossover_sma_days, min_periods=1).mean()

            if len(df) >= 2:
                # If we crossed above the SMA between yesterday and today
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

    # 7) Grab S&P 500 data (for reference)
    data['sp_pct_change'] = 0
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
    except Exception as e:
        errors.append('Could not get SP500 data')
        data['sp_pct_change'] = 0

    # 8) Create the email body and send
    with open('email_template.html', 'r') as file:
        html_template = file.read()

    from jinja2 import Template
    template = Template(html_template)
    html_output = template.render(
        data_52w_high=l_52w_high,
        data_crossover=crossover_sma,
        errors=errors,
        data=data
    )

    send_email("Daily Stonks Email", html_output)

# Run the script when invoked
if __name__ == "__main__":
    main()
