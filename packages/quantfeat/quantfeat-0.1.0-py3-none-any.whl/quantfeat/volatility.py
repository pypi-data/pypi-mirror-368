import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import gamma

def _load_data(data):
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("Data must be a CSV file path or a pandas DataFrame")
    if not {"open", "high", "low", "close"}.issubset(df.columns):
        raise ValueError("Data must contain columns: open, high, low, close")
    return df

def realized_volatility(data, window=22, verbose=True):
    df = _load_data(data)
    log_ret = np.log(df["close"] / df["close"].shift(1))
    df[f"realized_vol_{window}"] = log_ret.rolling(window).std(ddof=0)

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"realized_vol_{window}"], label="Realized Volatility")
        plt.title(f"Realized Volatility ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Volatility")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df

def parkinson_volatility(data, window=22, verbose=True):
    df = _load_data(data)
    rs = (np.log(df["high"] / df["low"])) ** 2
    factor = 1 / (4 * np.log(2))
    df[f"parkinson_vol_{window}"] = np.sqrt((factor * rs.rolling(window).mean()))

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"parkinson_vol_{window}"], label="Parkinson Volatility")
        plt.title(f"Parkinson Volatility ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Volatility")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df

def garman_klass_volatility(data, window=22, verbose=True):
    df = _load_data(data)
    term1 = 0.5 * (np.log(df["high"] / df["low"])) ** 2
    term2 = (2 * np.log(2) - 1) * (np.log(df["close"] / df["open"])) ** 2
    df[f"garman_klass_vol_{window}"] = np.sqrt((term1 - term2).rolling(window).mean())

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"garman_klass_vol_{window}"], label="Garman-Klass Volatility")
        plt.title(f"Garman-Klass Volatility ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Volatility")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df

def rogers_satchell_volatility(data, window=22, verbose=True):
    df = _load_data(data)
    log_ho = np.log(df["high"] / df["open"])
    log_lo = np.log(df["low"] / df["open"])
    log_co = np.log(df["close"] / df["open"])
    rs = (log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co))
    df[f"rogers_satchell_vol_{window}"] = np.sqrt(rs.rolling(window).mean())

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"rogers_satchell_vol_{window}"], label="Rogers-Satchell Volatility")
        plt.title(f"Rogers-Satchell Volatility ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Volatility")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df

def yang_zhang_volatility(data, window=22, k=None, verbose=True):
    df = _load_data(data)
    if k is None:
        k = 0.34 / (1.34 + (window + 1) / (window - 1))

    log_oo = np.log(df["open"] / df["close"].shift(1))
    log_co = np.log(df["close"] / df["open"])
    log_ho = np.log(df["high"] / df["open"])
    log_lo = np.log(df["low"] / df["open"])

    sigma_open = log_oo.rolling(window).var(ddof=0)
    sigma_close = log_co.rolling(window).var(ddof=0)
    sigma_rs = (log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)).rolling(window).mean()

    df[f"yang_zhang_vol_{window}"] = np.sqrt(sigma_open + k * sigma_rs + (1 - k) * sigma_close)

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"yang_zhang_vol_{window}"], label="Yang-Zhang Volatility")
        plt.title(f"Yang-Zhang Volatility ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Volatility")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df

def bipower_variation(data, window=22, verbose=True):
    df = _load_data(data)
    log_ret = np.log(df["close"] / df["close"].shift(1))

    abs_prod = (np.abs(log_ret) * np.abs(log_ret.shift(1)))
    bpv = (np.pi / 2) * abs_prod.rolling(window).mean()
    df[f"bpv_{window}"] = np.sqrt(bpv)

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"bpv_{window}"], label="Bipower Variation")
        plt.title(f"Bipower Variation ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Volatility")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df

def tripower_quarticity(data, window=22, verbose=True):
    df = _load_data(data)
    log_ret = np.log(df["close"] / df["close"].shift(1))

    mu_43 = (2 ** (2/3)) * (1 / np.sqrt(np.pi)) * \
            (gamma((4/3 + 1) / 2) / gamma(0.5))

    tpq_vals = (np.abs(log_ret) ** (4/3) *
                np.abs(log_ret.shift(1)) ** (4/3) *
                np.abs(log_ret.shift(2)) ** (4/3))

    tpq = (tpq_vals.rolling(window).mean()) * (mu_43 ** (-3))
    df[f"tpq_{window}"] = tpq

    if verbose:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df[f"tpq_{window}"], label="Tripower Quarticity")
        plt.title(f"Tripower Quarticity ({window}-period)")
        plt.xlabel("Time")
        plt.ylabel("Quarticity")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df
