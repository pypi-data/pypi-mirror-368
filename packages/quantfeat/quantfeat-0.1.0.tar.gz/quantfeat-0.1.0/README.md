
# QuantFeat

QuantFeat is a Python package for quantitative financial analysis, including EDA, returns, volatility, and data conversion utilities for time series data.

## Installation

Install the latest release from PyPI:

```bash
pip install quantfeat
```

## Usage

Import the modules you need:

```python
from quantfeat import eda, returns, volatility, convert_data
```

### Data Resampling

Convert raw data to a desired frequency (e.g., hourly):

```python
import pandas as pd
data = pd.read_csv("your_data.csv")
df = convert_data.resample(data, "1H", start="2020-01-01", end="2025-08-01")
```

### Exploratory Data Analysis (EDA)

Profile your dataset and get price/volume/returns stats:

```python
eda.profile(df)
eda.price_stats(df)
eda.returns(df)
eda.volume_stats(df)
```

Generate plots and heatmaps:

```python
eda.plot_time_series(df)
eda.corr_heatmap(df)
```

Run a full EDA pipeline (with summary and plots):

```python
eda.perform_quantitative_eda(df)
```

### Returns Calculation

Compute simple/log/lagged/rolling returns:

```python
from quantfeat import returns
returns.simple_returns(df)
returns.log_returns(df)
returns.lagged_returns(df, n=5)
returns.rolling_returns(df, window=20)
```

### Volatility Estimation

Estimate volatility using various models:

```python
from quantfeat import volatility
volatility.realized_volatility(df, window=20)
volatility.parkinson_volatility(df, window=20)
volatility.garman_klass_volatility(df, window=20)
volatility.rogers_satchell_volatility(df, window=20)
volatility.yang_zhang_volatility(df, window=20)
```

### Data Validation

Check and standardize your data:

```python
from quantfeat import validate
validate.validate_and_standardize(df)
```

## Documentation

See function docstrings or source for detailed arguments and options.

## License

MIT
