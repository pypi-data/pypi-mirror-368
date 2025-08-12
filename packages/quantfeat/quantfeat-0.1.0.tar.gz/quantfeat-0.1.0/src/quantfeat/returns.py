import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def simple_returns(data, target_feature='close', verbose=True):
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("data must be CSV file path or pandas DataFrame")

    if target_feature not in df.columns:
        raise ValueError(f"Data must contain '{target_feature}' column")

    values = df[target_feature].values.astype(float)
    returns = np.full(len(df), np.nan)
    returns[1:] = values[1:] / values[:-1] - 1

    result_df = df.copy()
    result_df['simple_returns'] = returns

    if verbose:
        print(f"Added simple returns column using '{target_feature}' feature, count={np.sum(~np.isnan(returns))}")
        plt.figure(figsize=(10, 4))
        plt.plot(result_df.index, result_df['simple_returns'], label=f'Simple Returns ({target_feature})')
        plt.xlabel('Time')
        plt.ylabel('Simple Returns')
        plt.title(f'Simple Returns Over Time - {target_feature}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    return result_df

def log_returns(data, target_feature='close', verbose=True):
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("data must be CSV file path or pandas DataFrame")

    if target_feature not in df.columns:
        raise ValueError(f"Data must contain '{target_feature}' column")

    values = df[target_feature].values.astype(float)
    log_r = np.full(len(df), np.nan)
    log_r[1:] = np.log(values[1:] / values[:-1])

    result_df = df.copy()
    result_df['log_returns'] = log_r

    if verbose:
        print(f"Added log returns column using '{target_feature}' feature, count={np.sum(~np.isnan(log_r))}")
        plt.figure(figsize=(10, 4))
        plt.plot(result_df.index, result_df['log_returns'], label=f'Log Returns ({target_feature})')
        plt.xlabel('Time')
        plt.ylabel('Log Returns')
        plt.title(f'Log Returns Over Time - {target_feature}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    return result_df

def lagged_returns(data, n=22, target_feature='close', verbose=True):
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("data must be CSV file path or pandas DataFrame")

    if target_feature not in df.columns:
        raise ValueError(f"Data must contain '{target_feature}' column")

    values = df[target_feature].values.astype(float)

    if n < 1 or n >= len(values):
        raise ValueError("n must be >= 1 and < number of data points")

    lagged_r = np.full(len(values), np.nan)
    lagged_r[n:] = values[n:] / values[:-n] - 1

    result_df = df.copy()
    column_name = f'lagged_returns_{n}'
    result_df[column_name] = lagged_r

    if verbose:
        print(f"Added {column_name} column using '{target_feature}' feature, count={np.sum(~np.isnan(lagged_r))}")
        plt.figure(figsize=(10, 4))
        plt.plot(result_df.index, result_df[column_name], label=f'Lagged Returns (n={n}, {target_feature})')
        plt.xlabel('Time')
        plt.ylabel('Lagged Returns')
        plt.title(f'Lagged Returns Over Time (n={n}) - {target_feature}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    return result_df

def rolling_returns(data, n=22, target_feature='close', verbose=True):
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("data must be CSV file path or pandas DataFrame")

    if target_feature not in df.columns:
        raise ValueError(f"Data must contain '{target_feature}' column")

    values = df[target_feature].values.astype(float)

    if n < 1 or n >= len(values):
        raise ValueError("n must be >= 1 and < number of data points")

    roll_r = np.full(len(values), np.nan)
    roll_r[n:] = values[n:] / values[:-n] - 1

    result_df = df.copy()
    column_name = f'rolling_returns_{n}'
    result_df[column_name] = roll_r

    if verbose:
        print(f"Added {column_name} column using '{target_feature}' feature, count={np.sum(~np.isnan(roll_r))}")
        plt.figure(figsize=(10, 4))
        plt.plot(result_df.index, result_df[column_name], label=f'Rolling Returns (n={n}, {target_feature})')
        plt.xlabel('Time')
        plt.ylabel('Rolling Returns')
        plt.title(f'Rolling Returns Over Time (n={n}) - {target_feature}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    return result_df
