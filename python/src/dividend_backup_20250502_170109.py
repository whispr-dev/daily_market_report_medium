"""
Module for dividend analysis.
"""
import pandas as pd
import numpy as np
import yfinance as yf

def analyze_dividend_history(ticker, period="5y"):
    """
    Analyze the dividend history for a given stock.
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Period to analyze (default: "5y")
        
    Returns:
        dict: Dictionary with dividend analysis
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Get dividend data
        dividends = stock.dividends
        
        if dividends.empty:
            return {
                "has_dividends": False,
                "message": f"{ticker} does not pay dividends."
            }
        
        # Calculate annual dividend rate
        current_year = pd.Timestamp.now().year
        recent_dividends = dividends[dividends.index.year >= (current_year - 1)]
        
        if recent_dividends.empty:
            annual_rate = 0
        else:
            annual_rate = recent_dividends.sum()
        
        # Get stock info for current price
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        # Calculate dividend yield
        if current_price > 0 and annual_rate > 0:
            dividend_yield = (annual_rate / current_price) * 100
        else:
            dividend_yield = 0
        
        # Calculate dividend growth
        years = sorted(dividends.groupby(dividends.index.year).sum().index.tolist())
        yearly_dividends = dividends.groupby(dividends.index.year).sum()
        
        if len(years) >= 2:
            growth_rates = []
            for i in range(1, len(years)):
                prev_year = years[i-1]
                curr_year = years[i]
                
                prev_dividend = yearly_dividends.loc[prev_year]
                curr_dividend = yearly_dividends.loc[curr_year]
                
                if prev_dividend > 0:
                    growth_rate = ((curr_dividend / prev_dividend) - 1) * 100
                    growth_rates.append(growth_rate)
            
            avg_growth_rate = np.mean(growth_rates) if growth_rates else 0
        else:
            avg_growth_rate = 0
        
        # Get payout dates
        payout_frequency = len(dividends[dividends.index.year == current_year-1]) if current_year > 2023 else len(dividends[dividends.index.year == 2023])
        
        # Get ex-dividend date
        try:
            ex_dividend_date = info.get('exDividendDate', None)
            if ex_dividend_date:
                ex_dividend_date = pd.Timestamp(ex_dividend_date, unit='s').strftime('%Y-%m-%d')
        except:
            ex_dividend_date = None
        
        return {
            "has_dividends": True,
            "annual_rate": annual_rate,
            "dividend_yield": dividend_yield,
            "payout_frequency": payout_frequency,
            "avg_growth_rate": avg_growth_rate,
            "ex_dividend_date": ex_dividend_date,
            "dividend_history": dividends.to_dict()
        }
    except Exception as e:
        return {
            "has_dividends": False,
            "error": str(e),
            "message": f"Error analyzing dividends for {ticker}."
        }

def get_current_bid_ask_spreads(ticker):
    """
    Get the current bid-ask spread for a stock.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary with bid-ask spread information
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Get stock info
        info = stock.info
        
        # Extract bid and ask data
        bid = info.get('bid', None)
        ask = info.get('ask', None)
        bid_size = info.get('bidSize', None)
        ask_size = info.get('askSize', None)
        
        if bid is None or ask is None:
            return {
                "ticker": ticker,
                "has_spread_data": False,
                "message": "Bid-ask data not available."
            }
        
        # Calculate spread
        spread = ask - bid
        spread_percent = (spread / ask) * 100 if ask > 0 else 0
        
        return {
            "ticker": ticker,
            "has_spread_data": True,
            "bid": bid,
            "ask": ask,
            "bid_size": bid_size,
            "ask_size": ask_size,
            "spread": spread,
            "spread_percent": spread_percent
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "has_spread_data": False,
            "error": str(e),
            "message": f"Error getting bid-ask spread for {ticker}."
        }