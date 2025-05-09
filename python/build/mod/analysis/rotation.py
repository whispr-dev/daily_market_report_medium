from mod.fetcher import get_stock_data
import pandas as pd

def rank_relative_strength(tickers, benchmark='SPY', days=21):
    rankings = []

    try:
        df_bench = get_stock_data(benchmark, period='3mo')
        if df_bench is None or len(df_bench) < days:
            raise Exception("Benchmark data insufficient")

        bench_return = (df_bench['close'].iloc[-1] - df_bench['close'].iloc[-days]) / df_bench['close'].iloc[-days]

        for ticker in tickers:
            try:
                df = get_stock_data(ticker, period='3mo')
                if df is None or len(df) < days:
                    continue

                stock_return = (df['close'].iloc[-1] - df['close'].iloc[-days]) / df['close'].iloc[-days]
                rs_score = stock_return - bench_return

                rankings.append({
                    "ticker": ticker,
                    "stock_return": round(stock_return * 100, 2),
                    "bench_return": round(bench_return * 100, 2),
                    "rs_score": round(rs_score * 100, 2)
                })

            except Exception as e:
                print(f"RS error for {ticker}: {e}")
                continue

    except Exception as e:
        print(f"Benchmark fetch failed: {e}")

    # Sort best performers first
    return sorted(rankings, key=lambda x: x['rs_score'], reverse=True)
