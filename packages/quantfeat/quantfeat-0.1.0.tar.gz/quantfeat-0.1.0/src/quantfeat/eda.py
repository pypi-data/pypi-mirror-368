import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import json
from pathlib import Path
from typing import Union, Dict, List, Optional, Tuple

warnings.filterwarnings('ignore')

# Cell 1: Table_Formatting_Utilities
def _create_border(width: int, style: str = 'double') -> str:
    styles = {
        'double': ('╔', '═', '╗'),
        'single': ('┌', '─', '┐'),
        'thick': ('┏', '━', '┓')
    }
    char_start, char_mid, char_end = styles.get(style, ('+', '-', '+'))
    return f"{char_start}{char_mid * (width - 2)}{char_end}"

def _create_bottom_border(width: int, style: str = 'double') -> str:
    styles = {
        'double': ('╚', '═', '╝'),
        'single': ('└', '─', '┘'),
        'thick': ('┗', '━', '┛')
    }
    char_start, char_mid, char_end = styles.get(style, ('+', '-', '+'))
    return f"{char_start}{char_mid * (width - 2)}{char_end}"

def _create_separator(width: int, style: str = 'double') -> str:
    styles = {
        'double': ('╠', '═', '╣'),
        'single': ('├', '─', '┤'),
        'thick': ('┣', '━', '┫')
    }
    char_start, char_mid, char_end = styles.get(style, ('+', '-', '+'))
    return f"{char_start}{char_mid * (width - 2)}{char_end}"

def _format_table(title: str, headers: List[str], rows: List[List], col_widths: Optional[List[int]] = None, style: str = 'double') -> str:
    if not rows:
        return f"\n{title}\nNo data available\n"

    if col_widths is None:
        col_widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) + 4 for i, h in enumerate(headers)]

    total_width = sum(col_widths) + len(headers) + 1
    result = [
        '',
        _create_border(total_width, style),
        f'║{title.center(total_width - 2)}║',
        _create_separator(total_width, style)
    ]

    header_line = '║' + ''.join(f'{str(h).center(col_widths[i])}║' for i, h in enumerate(headers))
    result.append(header_line)
    result.append(_create_separator(total_width, style))

    for row in rows:
        row_line = '║'
        for i, cell in enumerate(row):
            cell_str = f"{cell:.6f}" if isinstance(cell, float) and abs(cell) < 0.01 and cell != 0 else (f"{cell:.4f}" if isinstance(cell, float) else str(cell))
            row_line += f'{cell_str.center(col_widths[i])}║'
        result.append(row_line)

    result.append(_create_bottom_border(total_width, style))
    result.append('')
    return '\n'.join(result)


# Cell 2: Core_Analysis_Functions
def _load_data(data: Union[str, Path, pd.DataFrame], verbose: True) -> pd.DataFrame:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("Loading and standardizing data...")
    df = pd.read_csv(data) if isinstance(data, (str, Path)) else data.copy()
    df.columns = [col.lower().strip() for col in df.columns]
    datetime_col = next((col for col in ['datetime', 'date', 'timestamp', 'time'] if col in df.columns), None)
    if datetime_col:
        df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
        df = df.dropna(subset=[datetime_col]).set_index(datetime_col).sort_index()
        if verbose:
            print(f"Datetime index set from column: {datetime_col}")
    elif not pd.api.types.is_datetime64_any_dtype(df.index) and verbose:
        print("Warning: No datetime index or column found")
    return df

def profile(df: pd.DataFrame, verbose: bool) -> Dict:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                     DATA PROFILING ANALYSIS                   ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    missing = df.isnull().sum()
    zeros = (df == 0).sum()
    profile_data = {
        'shape': df.shape, 'columns': list(df.columns), 'dtypes': df.dtypes.apply(lambda x: x.name).to_dict(),
        'missing_count': missing.to_dict(), 'missing_pct': (missing / len(df) * 100).to_dict(),
        'zero_count': zeros.to_dict(), 'zero_pct': (zeros / len(df) * 100).to_dict(),
        'duplicates': int(df.duplicated().sum())
    }

    if verbose:
        basic_info = [['Total Rows', f"{df.shape[0]:,}"], ['Total Columns', f"{df.shape[1]}"],
                      ['Duplicate Rows', f"{profile_data['duplicates']:,}"],
                      ['Memory Usage (MB)', f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}"]]
        print(_format_table("DATASET OVERVIEW", ['Metric', 'Value'], basic_info))
        column_info = [[col.upper(), str(df[col].dtype), f"{missing[col]:,}", f"{missing[col] / len(df) * 100:.2f}%",
                        f"{zeros[col]:,}", f"{zeros[col] / len(df) * 100:.2f}%"] for col in df.columns]
        print(_format_table("COLUMN ANALYSIS", ['Column', 'Data Type', 'Missing Count', 'Missing %', 'Zero Count', 'Zero %'], column_info))
    return profile_data

def price_stats(df: pd.DataFrame, verbose: bool = True) -> Dict:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                    PRICE STATISTICS ANALYSIS                  ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    price_cols = [col for col in ['open', 'high', 'low', 'close', 'price'] if col in df.columns]
    if not price_cols:
        if verbose: print("No price columns found in dataset")
        return {}
    if verbose: print(f"Analyzing price columns: {', '.join(price_cols)}")

    res = {}
    for col in price_cols:
        s = df[col].dropna()
        res[col] = {
            'count': int(len(s)), 'mean': float(s.mean()), 'median': float(s.median()), 'std': float(s.std()),
            'min': float(s.min()), 'max': float(s.max()), 'range': float(s.max() - s.min()),
            'skew': float(s.skew()), 'kurtosis': float(s.kurtosis()),
            'percentiles': {f"{int(k*100)}%": float(v) for k, v in s.quantile([0.01, 0.05, 0.25, 0.75, 0.95, 0.99]).items()}
        }
    if verbose:
        summary = [[c.upper(), f"{s['count']:,}", f"{s['mean']:.6f}", f"{s['median']:.6f}", f"{s['std']:.6f}",
                    f"{s['min']:.6f}", f"{s['max']:.6f}", f"{s['range']:.6f}", f"{s['skew']:.4f}", f"{s['kurtosis']:.4f}"]
                   for c, s in res.items()]
        print(_format_table("PRICE STATISTICS SUMMARY", ['Column', 'Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range', 'Skewness', 'Kurtosis'], summary))
        for col, stats in res.items():
            perc_data = [[p, f"{v:.6f}"] for p, v in stats['percentiles'].items()]
            print(_format_table(f"PERCENTILES - {col.upper()}", ['Percentile', 'Value'], perc_data, style='single'))

    if 'high' in df.columns and 'low' in df.columns:
        invalid = (df['high'] < df['low']).sum()
        res['data_quality'] = {'invalid_high_low': int(invalid), 'pct_invalid': float(invalid / len(df) * 100)}
        if verbose:
            quality = [['Invalid High < Low', f"{invalid:,}"], ['Percentage Invalid', f"{invalid / len(df) * 100:.4f}%"]]
            print(_format_table("DATA QUALITY CHECK", ['Metric', 'Value'], quality))
    return res

def returns(df: pd.DataFrame, verbose: True) -> Dict:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                    RETURN ANALYTICS ENGINE                     ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    price_col = next((col for col in ['close', 'price', 'adj_close'] if col in df.columns), None)
    if not price_col:
        if verbose: print("No suitable price column found for return calculation")
        return {}
    if verbose: print(f"Computing returns using: {price_col}")

    ret = df[price_col].pct_change().dropna()
    clean = lambda val: float(val) if pd.notnull(val) else 0.0
    percentiles = {f"{int(k*100)}%": clean(v) for k, v in ret.quantile([0.01, 0.05, 0.1, 0.25, 0.75, 0.9, 0.95, 0.99]).items()}
    res = {
        'count': len(ret), 'mean': clean(ret.mean()), 'median': clean(ret.median()), 'std': clean(ret.std()),
        'min': clean(ret.min()), 'max': clean(ret.max()), 'range': clean(ret.max() - ret.min()),
        'skew': clean(ret.skew()), 'kurtosis': clean(ret.kurtosis()), 'positive_count': int((ret > 0).sum()),
        'negative_count': int((ret < 0).sum()), 'zero_count': int((ret == 0).sum()),
        'positive_ratio': clean((ret > 0).mean()), 'percentiles': percentiles,
        'rolling_volatility': {}
    }
    for w in [10, 20, 30, 60]:
        rolling_std = ret.rolling(w).std()
        res['rolling_volatility'][w] = {'mean': clean(rolling_std.mean()), 'std': clean(rolling_std.std()),
                                        'min': clean(rolling_std.min()), 'max': clean(rolling_std.max())}
    if verbose:
        metrics = [['Total Observations', f"{res['count']:,}"], ['Mean Return', f"{res['mean']:.8f}"], ['Median Return', f"{res['median']:.8f}"],
                   ['Std Dev Return', f"{res['std']:.8f}"], ['Minimum Return', f"{res['min']:.8f}"], ['Maximum Return', f"{res['max']:.8f}"],
                   ['Return Range', f"{res['range']:.8f}"], ['Skewness', f"{res['skew']:.6f}"], ['Kurtosis', f"{res['kurtosis']:.6f}"]]
        print(_format_table("RETURN PERFORMANCE METRICS", ['Metric', 'Value'], metrics))
        counts = [['Positive Returns', f"{res['positive_count']:,}"], ['Negative Returns', f"{res['negative_count']:,}"],
                  ['Zero Returns', f"{res['zero_count']:,}"], ['Positive Ratio', f"{res['positive_ratio']:.2%}"]]
        print(_format_table("RETURN COUNT ANALYSIS", ['Metric', 'Value'], counts))
        perc_data = [[p, f"{v:.8f}"] for p, v in sorted(res['percentiles'].items(), key=lambda x: float(x[0][:-1]))]
        print(_format_table("RETURN PERCENTILES", ['Percentile', 'Return Value'], perc_data))
        vol_data = [[f"{w} Periods", f"{s['mean']:.8f}", f"{s['std']:.8f}", f"{s['min']:.8f}", f"{s['max']:.8f}"]
                    for w, s in res['rolling_volatility'].items()]
        print(_format_table("ROLLING STANDARD DEVIATION ANALYSIS", ['Window', 'Mean Std', 'Std of Std', 'Min Std', 'Max Std'], vol_data))
    return res

def volume_stats(df: pd.DataFrame, verbose: True) -> Optional[Dict]:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if 'volume' not in df.columns:
        if verbose:
            print("\n╔════════════════════════════════════════════════════════════════╗")
            print("║                   VOLUME DATA NOT AVAILABLE                   ║")
            print("╚════════════════════════════════════════════════════════════════╝")
        return None
    if verbose:
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                    VOLUME ANALYSIS ENGINE                     ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    vol = df['volume'].dropna()
    res = {
        'count': int(len(vol)), 'mean': float(vol.mean()), 'median': float(vol.median()), 'std': float(vol.std()),
        'min': float(vol.min()), 'max': float(vol.max()), 'range': float(vol.max() - vol.min()),
        'zero_count': int((vol == 0).sum()), 'skew': float(vol.skew()), 'kurtosis': float(vol.kurtosis()),
        'percentiles': {f"{int(k*100)}%": float(v) for k, v in vol.quantile([0.05, 0.25, 0.5, 0.75, 0.95]).items()}
    }
    if verbose:
        metrics = [['Total Observations', f"{res['count']:,}"], ['Mean Volume', f"{res['mean']:,.0f}"], ['Median Volume', f"{res['median']:,.0f}"],
                   ['Std Dev Volume', f"{res['std']:,.0f}"], ['Minimum Volume', f"{res['min']:,.0f}"], ['Maximum Volume', f"{res['max']:,.0f}"],
                   ['Volume Range', f"{res['range']:,.0f}"], ['Zero Volume Count', f"{res['zero_count']:,}"],
                   ['Zero Volume %', f"{res['zero_count']/res['count']*100:.2f}%"], ['Skewness', f"{res['skew']:.6f}"], ['Kurtosis', f"{res['kurtosis']:.6f}"]]
        print(_format_table("VOLUME STATISTICS", ['Metric', 'Value'], metrics))
        perc_data = [[p, f"{v:,.0f}"] for p, v in sorted(res['percentiles'].items(), key=lambda x: float(x[0][:-1]))]
        print(_format_table("VOLUME PERCENTILES", ['Percentile', 'Volume'], perc_data))

    if 'close' in df.columns:
        ret = df['close'].pct_change().dropna()
        vol_aligned = vol.reindex(ret.index).dropna()
        if not vol_aligned.empty:
            corr = float(ret.loc[vol_aligned.index].corr(vol_aligned))
            res['vol_price_corr'] = corr
            if verbose:
                print(_format_table("VOLUME-PRICE RELATIONSHIP", ['Metric', 'Value'], [['Volume-Price Return Correlation', f"{corr:.6f}"]] ))
    return res

# Cell 3: Visualization_Functions
def plot_time_series(df: pd.DataFrame, verbose: True) -> None:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                 GENERATING VISUALIZATIONS                      ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    price_col = next((col for col in ['close', 'price', 'adj_close'] if col in df.columns), None)
    if not price_col:
        if verbose: print("No price column available for visualization")
        return

    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('COMPREHENSIVE TIME SERIES ANALYSIS', fontsize=16, weight='bold')

    returns = df[price_col].pct_change().dropna()
    axs[0, 0].plot(df.index, df[price_col], color='navy', alpha=0.8, lw=1)
    axs[0, 0].set_title(f'{price_col.upper()} PRICE EVOLUTION', fontweight='bold')
    axs[0, 1].hist(returns, bins=50, color='darkgreen', alpha=0.7, edgecolor='black')
    axs[0, 1].axvline(returns.mean(), color='red', ls='--', lw=2, label=f'Mean: {returns.mean():.6f}')
    axs[0, 1].axvline(returns.median(), color='orange', ls='--', lw=2, label=f'Median: {returns.median():.6f}')
    axs[0, 1].set_title('RETURN DISTRIBUTION', fontweight='bold')
    axs[0, 1].legend()
    axs[1, 0].plot(returns.rolling(20).std(), color='purple', alpha=0.8, lw=1)
    axs[1, 0].set_title('20-PERIOD ROLLING STANDARD DEVIATION', fontweight='bold')
    axs[1, 1].hist(df[price_col].dropna(), bins=50, color='maroon', alpha=0.7, edgecolor='black')
    axs[1, 1].set_title('PRICE LEVEL DISTRIBUTION', fontweight='bold')

    for ax in axs.flat:
        ax.grid(True, alpha=0.3)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    if 'volume' in df.columns:
        fig, axs = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('VOLUME ANALYSIS', fontsize=16, weight='bold')
        axs[0].plot(df.index, df['volume'], color='teal', alpha=0.7, lw=0.8)
        axs[0].set_title('VOLUME EVOLUTION OVER TIME', fontweight='bold')
        axs[1].hist(df['volume'].dropna(), bins=50, color='orange', alpha=0.7, edgecolor='black')
        axs[1].set_title('VOLUME DISTRIBUTION', fontweight='bold')
        for ax in axs.flat:
            ax.grid(True, alpha=0.3)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

def corr_heatmap(df: pd.DataFrame, verbose: True) -> None:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                  CORRELATION HEATMAP ANALYSIS                 ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    numeric_cols = df.select_dtypes(include=np.number)
    if len(numeric_cols.columns) < 2:
        if verbose: print("Insufficient numeric columns for correlation analysis")
        return

    corr = numeric_cols.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt='.3f', cmap='RdBu_r', center=0, square=True,
                linewidths=0.5, cbar_kws={'shrink': 0.8}, mask=np.triu(np.ones_like(corr, dtype=bool)))
    plt.title('FEATURE CORRELATION MATRIX', fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()

    if verbose:
        corr_pairs = corr.unstack().sort_values(kind="quicksort", ascending=False).drop_duplicates()
        corr_pairs = corr_pairs[corr_pairs != 1.0].head(10)
        pair_data = [[f"{i[0]} vs {i[1]}", f"{v:.6f}"] for i, v in corr_pairs.items()]
        print(_format_table("TOP CORRELATION COEFFICIENTS", ['Variable Pair', 'Correlation'], pair_data))

# Cell 4: Orchestrator_Function
def _print_final_summary(results: Dict, verbose: True) -> None:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if not verbose: return
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║                    EXECUTIVE SUMMARY REPORT                   ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    summary_data = []
    if 'profile' in results:
        prof = results['profile']
        summary_data.extend([
            ['Dataset Dimensions', f"{prof['shape'][0]:,} rows × {prof['shape'][1]} columns"],
            ['Missing Data Points', f"{sum(prof['missing_count'].values()):,}"],
            ['Duplicate Rows', f"{prof['duplicates']:,}"]
        ])
    if 'returns' in results:
        ret = results['returns']
        summary_data.extend([
            ['Mean Return', f"{ret['mean']:.8f}"], ['Return Std Deviation', f"{ret['std']:.8f}"],
            ['Return Skewness', f"{ret['skew']:.4f}"], ['Positive Return Ratio', f"{ret['positive_ratio']:.2%}"]
        ])
    if 'volume' in results and results['volume']:
        vol = results['volume']
        summary_data.extend([['Mean Volume', f"{vol['mean']:,.0f}"], ['Zero Volume Count', f"{vol['zero_count']:,}"]])
    print(_format_table("KEY PERFORMANCE INDICATORS", ['Metric', 'Value'], summary_data))
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║                  ANALYSIS COMPLETED SUCCESSFULLY              ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

def perform_quantitative_eda(data: Union[str, pd.DataFrame], verbose: bool = True, show_plots: bool = True) -> Dict:
    if verbose is not False:
        verbose = True
    else:
        verbose = False
    if verbose:
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║              INITIALIZING QUANTITATIVE DATA ANALYZER          ║")
        print("╚════════════════════════════════════════════════════════════════╝")

    df = _load_data(data, verbose)
    if verbose: print(f"Data loaded successfully: {df.shape[0]:,} rows × {df.shape[1]} columns")

    results = {}
    results['profile'] = profile(df, verbose)
    results['price_stats'] = price_stats(df, verbose)
    results['returns'] = returns(df, verbose)
    results['volume'] = volume_stats(df, verbose)

    if show_plots:
        plot_time_series(df, verbose)
        corr_heatmap(df, verbose)

    _print_final_summary(results, verbose)

    if verbose:
        print("\n" + "="*80)
        print("JSON RESULTS (for programmatic access):")
        print("="*80)
        print(json.dumps(results, indent=2, default=str))
        print("="*80)

    return results