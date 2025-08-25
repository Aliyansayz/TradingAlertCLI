import yfinance as yf
import pandas as pd

def fetch_eurusd_data(period='7d', interval='1h'):
    """
    Fetch EURUSD data from yfinance.
    
    Args:
        period: Data period (default '7d')
        interval: Data interval (default '1h')
        
    Returns:
        pandas.DataFrame: OHLC data for EURUSD
    """
    target_symbol = 'EURUSD=X'
    
    eurusd_data = yf.download(target_symbol, period=period, interval=interval)
    
    # Flatten the MultiIndex columns if they exist
    if isinstance(eurusd_data.columns, pd.MultiIndex):
        eurusd_data.columns = ['_'.join(col).strip() for col in eurusd_data.columns.values]
        # Remove trailing underscores if they exist (from the empty string in the tuple)
        eurusd_data.columns = [col[:-1] if col.endswith('_') else col for col in eurusd_data.columns]

    # Remove the '_EURUSD=X' suffix from column names
    eurusd_data.columns = [col.replace(f'_{target_symbol}', '') for col in eurusd_data.columns]

    eurusd_data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)

    return eurusd_data

# Example usage - commented out to prevent automatic execution
# if __name__ == "__main__":
#     data = fetch_eurusd_data()
#     print(data)