
import pandas as pd
import numpy as np
from mod.fetcher import get_stock_data

def detect_volatility_squeezes(tickers, period="6mo", squeeze_threshold=0.1):
    squeeze_candidates = []

    for ticker in tickers:
        try:
            df = get_stock_data(ticker, period=period)
            if df is None or len(df) < 50:
                continue

            df['20sma'] = df['close'].rolling(window=20).mean()
            df['stddev'] = df['close'].rolling(window=20).std()
            df['upper_bb'] = df['20sma'] + 2 * df['stddev']
            df['lower_bb'] = df['20sma'] - 2 * df['stddev']
            df['bb_width'] = df['upper_bb'] - df['lower_bb']
            df['atr'] = df['high'] - df['low']
            df['atr'] = df['atr'].rolling(window=14).mean()

            # Normalize widths
            df['bb_norm'] = df['bb_width'] / df['20sma']
            df['atr_norm'] = df['atr'] / df['20sma']

            recent = df.dropna().iloc[-1]
            bb_val = recent['bb_norm']
            atr_val = recent['atr_norm']

            bb_thresh = df['bb_norm'].quantile(squeeze_threshold)
            atr_thresh = df['atr_norm'].quantile(squeeze_threshold)

            if bb_val < bb_thresh and atr_val < atr_thresh:
                squeeze_candidates.append({
                    "ticker": ticker,
                    "bb_width": round(bb_val, 4),
                    "atr_norm": round(atr_val, 4)
                })

        except Exception as e:
            print(f"Volatility squeeze error for {ticker}: {e}")
            continue

    return squeeze_candidates
