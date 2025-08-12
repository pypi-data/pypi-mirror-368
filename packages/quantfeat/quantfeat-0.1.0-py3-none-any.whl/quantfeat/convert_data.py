import pandas as pd

def resample(df, rule, start=None, end=None):
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df.set_index('datetime', inplace=True)
    elif not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have a datetime index or a 'datetime' column.")

    if start or end:
        df = df.loc[start:end]

    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }

    return df.resample(rule).apply(ohlc_dict).dropna()
