import pandas as pd
import numpy as np
from typing import Union, List, Optional, Dict, Any
import warnings

OHLC_COLUMNS = {
    'open': ['open', 'Open', 'OPEN'],
    'high': ['high', 'High', 'HIGH'],
    'low': ['low', 'Low', 'LOW'],
    'close': ['close', 'Close', 'CLOSE', 'c'],
}

DATE_COL_VARIANTS = ['datetime', 'date_time', 'timestamp', 'time', 'date']
DATE_ONLY_VARIANTS = ['date']
TIME_ONLY_VARIANTS = ['time']

def standardize_ohlc_columns(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    df = df.copy()
    col_map = {}
    original_cols = df.columns.tolist()

    for std_col, variants in OHLC_COLUMNS.items():
        for variant in variants:
            if variant in df.columns:
                col_map[variant] = std_col
                break

    if col_map and verbose:
        print(f"📝 Column Renaming Operations:")
        for old_col, new_col in col_map.items():
            print(f"   • '{old_col}' → '{new_col}'")

    df.rename(columns=col_map, inplace=True)

    if verbose:
        renamed_cols = [col for col in original_cols if col in col_map]
        print(f"✅ Standardized {len(renamed_cols)} OHLC columns")

    return df

def parse_datetime_columns(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    df = df.copy()
    original_shape = df.shape
    original_cols = df.columns.tolist()

    dt_col = next((col for col in DATE_COL_VARIANTS if col in df.columns), None)
    if dt_col:
        if verbose:
            print(f"🕐 Found datetime column: '{dt_col}'")
            print(f"   • Sample values: {df[dt_col].head(3).tolist()}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce', utc=True)

        null_count = df[dt_col].isnull().sum()
        if null_count > 0:
            raise ValueError(f"Datetime parsing failed for {null_count} rows in column '{dt_col}'")

        df.rename(columns={dt_col: 'datetime'}, inplace=True)
        df.set_index('datetime', inplace=True)
        result_df = df.sort_index()

        if verbose:
            print(f"   • Parsed {len(result_df)} datetime entries")
            print(f"   • Date range: {result_df.index.min()} to {result_df.index.max()}")
            print(f"   • Timezone: {result_df.index.tz}")

        return result_df

    date_col = next((col for col in DATE_ONLY_VARIANTS if col in df.columns), None)
    time_col = next((col for col in TIME_ONLY_VARIANTS if col in df.columns), None)
    if date_col and time_col:
        if verbose:
            print(f"🕐 Found separate date/time columns: '{date_col}' + '{time_col}'")

        combined = df[date_col].astype(str) + ' ' + df[time_col].astype(str)
        df['datetime'] = pd.to_datetime(combined, errors='coerce', utc=True)

        null_count = df['datetime'].isnull().sum()
        if null_count > 0:
            raise ValueError(f"Datetime parsing failed for {null_count} rows combining date and time columns")

        df.set_index('datetime', inplace=True)
        df.drop(columns=[date_col, time_col], inplace=True)
        result_df = df.sort_index()

        if verbose:
            print(f"   • Combined and parsed {len(result_df)} datetime entries")
            print(f"   • Removed columns: ['{date_col}', '{time_col}']")

        return result_df

    if date_col:
        if verbose:
            print(f"🕐 Found date-only column: '{date_col}' (daily data)")

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        null_count = df[date_col].isnull().sum()
        if null_count > 0:
            raise ValueError(f"Date parsing failed for {null_count} rows in column '{date_col}'")

        df.rename(columns={date_col: 'datetime'}, inplace=True)
        df.set_index('datetime', inplace=True)
        result_df = df.sort_index()

        if verbose:
            print(f"   • Parsed {len(result_df)} date entries")

        return result_df

    raise ValueError("No recognizable datetime/date columns found. Provide a datetime column or date+time columns.")

def drop_zero_columns(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    original_cols = df.columns.tolist()
    zero_cols = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and (df[col] == 0).all():
            zero_cols.append(col)

    if zero_cols:
        df = df.drop(columns=zero_cols)
        if verbose:
            print(f"🗑️  Dropped zero-value columns: {zero_cols}")
            print(f"   • Removed {len(zero_cols)} columns")
    elif verbose:
        print("ℹ️  No zero-value columns found to drop")

    return df

def validate_ohlc_data(df: pd.DataFrame, present_ohlc: List[str], verbose: bool = False) -> None:
    if verbose:
        print(f"🔍 Validating OHLC columns: {present_ohlc}")

    for col in present_ohlc:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            raise ValueError(f"Missing values found in column '{col}': {null_count} nulls")

        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' must be numeric, found: {df[col].dtype}")

        if verbose:
            print(f"   ✅ '{col}': {len(df)} values, type={df[col].dtype}")

    if set(['open', 'high', 'low', 'close']).issubset(present_ohlc):
        high_violations = (~(df['high'] >= df[['open', 'close', 'low']].min(axis=1))).sum()
        low_violations = (~(df['low'] <= df[['open', 'close', 'high']].max(axis=1))).sum()

        if high_violations > 0:
            raise ValueError(f"High price less than open/close/low detected in {high_violations} rows")

        if low_violations > 0:
            raise ValueError(f"Low price greater than open/close/high detected in {low_violations} rows")

        if verbose:
            print(f"   ✅ Price relationships validated for {len(df)} rows")

def print_dataframe_summary(df: pd.DataFrame, title: str = "DataFrame Summary") -> None:
    print(f"\n📊 {title}")
    print(f"   • Shape: {df.shape} (rows: {df.shape[0]:,}, columns: {df.shape[1]})")
    print(f"   • Index: {type(df.index).__name__}")

    if hasattr(df.index, 'tz') and df.index.tz:
        print(f"   • Timezone: {df.index.tz}")

    if len(df) > 0 and hasattr(df.index, 'min'):
        try:
            print(f"   • Index range: {df.index.min()} to {df.index.max()}")
        except:
            pass

    print(f"   • Columns: {list(df.columns)}")
    print(f"   • Data types:")
    for col, dtype in df.dtypes.items():
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
        print(f"     - {col}: {dtype} (nulls: {null_count}, {null_pct:.1f}%)")

    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    print(f"   • Memory usage: {memory_mb:.2f} MB")

def validate_and_standardize(
    df: Union[pd.DataFrame, str],
    required_cols: Optional[List[str]] = None,
    drop_zero_cols: bool = False,
    verbose: bool = True
) -> pd.DataFrame:
    if verbose:
        print("🚀 Starting data validation and standardization...")

    original_input_type = "DataFrame" if isinstance(df, pd.DataFrame) else "CSV file"

    if isinstance(df, str):
        if verbose:
            print(f"📁 Loading data from: {df}")
        try:
            df = pd.read_csv(df)
            if verbose:
                print(f"   ✅ Successfully loaded CSV file")
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {df}")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")

    if verbose:
        print_dataframe_summary(df, "Original Data")

    df = standardize_ohlc_columns(df, verbose=verbose)
    df = parse_datetime_columns(df, verbose=verbose)

    present_ohlc = [col for col in ['open', 'high', 'low', 'close'] if col in df.columns]

    if required_cols:
        missing = set(required_cols) - set(present_ohlc)
        if missing:
            raise ValueError(f"Missing required OHLC columns: {missing}")
        if verbose:
            print(f"✅ All required OHLC columns present: {required_cols}")

    if present_ohlc:
        validate_ohlc_data(df, present_ohlc, verbose=verbose)
    elif verbose:
        print("ℹ️  No OHLC columns found for validation")

    if drop_zero_cols:
        df = drop_zero_columns(df, verbose=verbose)

    if verbose:
        print_dataframe_summary(df, "Final Processed Data")

        print(f"\n🎉 Validation and standardization complete!")
        print(f"   • Input: {original_input_type}")
        print(f"   • Processed: {len(df):,} rows × {len(df.columns)} columns")
        if present_ohlc:
            print(f"   • OHLC columns validated: {present_ohlc}")
        print(f"   • Ready for quantitative analysis! 📈")

    return df
