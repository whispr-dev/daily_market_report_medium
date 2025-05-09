import pandas as pd
from mod.analysis.indicators import calculate_ewo, detect_reversal_signals
from mod.fetcher import get_stock_data

def get_multi_timeframe_signals(tickers, days_back=365):
    signals = []

    for ticker in tickers:
        try:
            df = get_stock_data(ticker, period="1y")
            if df is None or df.empty:
                continue

            df['date'] = pd.to_datetime(df.index)
            df = df.sort_index()

            # Weekly data
            df_weekly = df.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

            # Daily reversal signals
            daily_reversals = detect_reversal_signals(df)

            # Weekly reversal signals
            weekly_reversals = detect_reversal_signals(df_weekly)

            # Look for agreement
            if (
                daily_reversals.get("bullish") and
                weekly_reversals.get("bullish")
            ):
                signals.append({
                    "ticker": ticker,
                    "signal": "bullish",
                    "source": "multi-timeframe"
                })

            elif (
                daily_reversals.get("bearish") and
                weekly_reversals.get("bearish")
            ):
                signals.append({
                    "ticker": ticker,
                    "signal": "bearish",
                    "source": "multi-timeframe"
                })

        except Exception as e:
            print(f"MTF error on {ticker}: {e}")
            continue

    return signals
