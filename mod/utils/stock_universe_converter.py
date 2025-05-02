'''
Utility module to convert between different formats of stock universe data.
'''
import pandas as pd

def ensure_dataframe(universe):
    '''
    Convert any stock universe format to a DataFrame.
    
    Args:
        universe: List of tickers or DataFrame
        
    Returns:
        DataFrame with 'symbol' column
    '''
    if isinstance(universe, pd.DataFrame):
        # If already a DataFrame, ensure it has a 'symbol' column
        if 'symbol' not in universe.columns and len(universe.columns) > 0:
            # If there are columns but no 'symbol', use the first column
            universe = universe.rename(columns={universe.columns[0]: 'symbol'})
        return universe
    elif isinstance(universe, list):
        # Convert list to DataFrame
        return pd.DataFrame({'symbol': universe})
    else:
        # For any other type, try to convert to list then DataFrame
        try:
            tickers = list(universe)
            return pd.DataFrame({'symbol': tickers})
        except:
            # Default to empty DataFrame with symbol column
            return pd.DataFrame(columns=['symbol'])

def get_symbols_list(universe):
    '''
    Get a list of ticker symbols from any stock universe format.
    
    Args:
        universe: List of tickers or DataFrame
        
    Returns:
        List of ticker symbols
    '''
    if isinstance(universe, pd.DataFrame):
        if 'symbol' in universe.columns:
            return universe['symbol'].tolist()
        elif len(universe.columns) > 0:
            return universe[universe.columns[0]].tolist()
        else:
            return []
    elif isinstance(universe, list):
        return universe
    else:
        # For any other type, try to convert to list
        try:
            return list(universe)
        except:
            return []
