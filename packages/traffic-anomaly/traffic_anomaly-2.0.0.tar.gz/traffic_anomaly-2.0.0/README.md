# Traffic Anomaly

<!-- Package Info -->
[![PyPI](https://img.shields.io/pypi/v/traffic_anomaly)](https://pypi.org/project/traffic_anomaly/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/traffic_anomaly)](https://pypi.org/project/traffic_anomaly/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/traffic_anomaly)](https://pypi.org/project/traffic_anomaly/)

<!-- Repository Info -->
[![GitHub License](https://img.shields.io/github/license/ShawnStrasser/traffic-anomaly)](https://github.com/ShawnStrasser/traffic-anomaly/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/ShawnStrasser/traffic-anomaly)](https://github.com/ShawnStrasser/traffic-anomaly/issues)
[![GitHub stars](https://img.shields.io/github/stars/ShawnStrasser/traffic-anomaly)](https://github.com/ShawnStrasser/traffic-anomaly/stargazers)

<!-- Status -->
[![Unit Tests](https://github.com/ShawnStrasser/traffic-anomaly/actions/workflows/pr-tests.yml/badge.svg)](https://github.com/ShawnStrasser/traffic-anomaly/actions/workflows/pr-tests.yml)
[![codecov](https://codecov.io/gh/ShawnStrasser/traffic-anomaly/badge.svg)](https://codecov.io/gh/ShawnStrasser/traffic-anomaly)

`traffic-anomaly` is a production ready Python package for robust decomposition, anomaly detection, and change point detection on multiple time series at once. It uses Ibis to integrate with any SQL backend in a production pipeline, or run locally with the included DuckDB backend.

**Tested on:** Windows, macOS, and Ubuntu with Python 3.9-3.13

Designed for real world messy traffic data (volumes, travel times), `traffic-anomaly` uses medians to decompose time series into trend, daily, weekly, and residual components. Anomalies are then classified using Z-score or GEH statistics, and change points identify structural shifts in the data. Median Absolute Deviation may be used for further robustness. Missing data are handled, and time periods without sufficient data can be thrown out. Try it out, sample data included! [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1BvMvgheWO3QlB6iSRLhromebwtYjyl4O?usp=sharing)



# Installation & Usage

```bash
pip install traffic_anomaly
```
    
```python
from traffic_anomaly import *
from traffic_anomaly import sample_data

# Load sample data
travel_times = sample_data.travel_times

decomp = decompose(
    data=travel_times, # Pandas DataFrame or Ibis Table (for compatibility with any SQL backend)
    datetime_column='timestamp',
    value_column='travel_time',
    entity_grouping_columns=['id', 'group'],
    freq_minutes=60, # Frequency of the time series in minutes
    rolling_window_days=7, # Rolling window size in days. Should be a multiple of 7 for traffic data
    drop_days=7, # Should be at least 7 for traffic data
    min_rolling_window_samples=56, # Minimum number of samples in the rolling window, set to 0 to disable.
    min_time_of_day_samples=7, # Minimum number of samples for each time of day (like 2:00pm), set to 0 to disable
    drop_extras=False, # lets keep seasonal/trend for visualization below
    to_sql=False # Return SQL queries instead of Pandas DataFrames for running on SQL backends
)
decomp.head(3)
```
| id         | timestamp           | travel_time | group           | median    | season_day | season_week | resid      | prediction |
|------------|---------------------|-------------|-----------------|-----------|------------|-------------|------------|------------|
| 448838574  | 2022-09-29 06:00:00 | 24.8850     | SE SUNNYSIDE RD | 24.963749 | -4.209375  | 0.57875     | 3.5518772  | 21.333122  |
| 448838574  | 2022-09-22 06:00:00 | 20.1600     | SE SUNNYSIDE RD | 24.842501 | -4.209375  | 0.57875     | -1.0518752 | 21.211876  |
| 448838574  | 2022-09-15 06:00:00 | 22.2925     | SE SUNNYSIDE RD | 24.871250 | -4.209375  | 0.57875     | 1.0518752  | 21.240623  |

Here's a plot showing what it looks like to decompose a time series. The sum of components is equal to the original data. After extracting the trend and seasonal components, what is left are residuals that are more stationary so they're easier to work with.

![Example](example_plot.png)

```python
# Apply anomaly detection
anomaly = traffic_anomaly.anomaly(
    decomposed_data=decomp, # Decomposed time series as a Pandas DataFrame or Ibis Table
    datetime_column='timestamp',
    value_column='travel_time',
    entity_grouping_columns=['id'],
    entity_threshold=3.5 # Threshold for entity-level anomaly detection (z-score or GEH statistic)
)
anomaly.head(3)
```
| id         | timestamp           | travel_time | group          | prediction | anomaly |
|------------|----------------------|-------------|----------------|------------|---------|
| 448838575  | 2022-09-09 06:00:00  | 19.3575     | SE SUNNYSIDE RD| 16.926249  | False   |
| 448838575  | 2022-09-09 07:00:00  | 22.5200     | SE SUNNYSIDE RD| 20.826252  | False   |
| 448838575  | 2022-09-09 08:00:00  | 23.0350     | SE SUNNYSIDE RD| 22.712502  | False   |

The image below is showing an example application on actual traffic counts. Note that this package does not produce plots.

![ExampleAnomaly](anomaly1.png)

# Changepoint Detection

`traffic_anomaly` includes robust changepoint detection that identifies significant changes, such as when traffic patterns shift due to construction, equipment failure, or events like school starting up in the Fall. Changepoints represent moments when the underlying statistical properties of the data change. This functionality is meant for detecting long term / persistent changes, whereas anomaly detection is for short term / transient changes.

```python
# Load changepoint sample data  
changepoint_data = sample_data.changepoints_input

# Apply change point detection
changepoints = traffic_anomaly.changepoint(
    data=changepoint_data,  # Pandas DataFrame or Ibis Table
    value_column='travel_time_seconds',
    entity_grouping_column='ID',
    datetime_column='TimeStamp',
    rolling_window_days=14,  # Size of analysis window
    robust=True,  # Use robust (Winsorized) variance for better outlier handling
    score_threshold=5,  # Threshold for change point detection (lower = more sensitive)
    min_separation_days=3  # Minimum days between detected change points
)
changepoints.head(3)
```

| ID         | TimeStamp           | score | avg_before | avg_after | avg_diff |
|------------|---------------------|-------|------------|-----------|----------|
| 448838574  | 2022-09-15 14:00:00 | 2.34  | 45.2       | 52.8      | 7.6      |
| 448838575  | 2022-09-22 08:00:00 | 1.89  | 38.1       | 29.4      | -8.7     |
| 448838576  | 2022-10-01 16:00:00 | 3.12  | 41.5       | 48.9      | 7.4      |

The image below shows an example of changepoint detection on traffic data, highlighting where significant structural changes occur in the time series.

![ExampleChangepoint](changepoint.png)

The change point detection algorithm:
- Uses variance-based scoring to identify periods where data patterns shift
- Can operate in robust mode (recommended) which uses Winsorized variance for better handling of outliers
- Provides before/after averages to quantify the magnitude and direction of changes
- Filters results to local peaks with minimum separation to avoid detecting noise

## Parameters

- `robust=True`: Uses Winsorized variance (clips extreme values) for more stable detection
- `score_threshold`: Higher values detect fewer, more significant change points
- `rolling_window_days`: Size of the analysis window (split between before/after periods)
- `min_separation_days`: Prevents detecting multiple change points too close together

# Considerations

The seasonal components are not allowed to change over time, therefore, it is important to limit the number of weeks included in the model, especially if there is yearly seasonality (and there is). The recommended use for application over a long date range is to run the model incrementally over a rolling window of about 6 weeks.

Because traffic data anomalies usually skew higher, forecasts made by this model are systemically low because in a right tailed distribution the median will be lower than the mean. This is by design, as the model is meant primarily for anomaly detection and not forecasting.

# Notes On Anomaly Detection

`traffic_anomaly` can classify two separate types of anomalies:

1. Entity-Level Anomalies are detected for individual entities based on their own historical patterns, without considering the group context.
2. Group-Level Anomalies are detected for entities when compared to the behavior of other entities within the same group. Group-level anomalies are more rare because in order to be considered for classification as a group-level anomaly, a time period must also have been classified as an entity-level anomaly.

Why is that needed? Well, say you're data is vehicle travel times within a city and there is a snow storm. Travel times across the city drop, and if you're looking at roadway segments in isolation, everything is an anomaly. That's nice, but what if you're only interested in things that are broken? That's where group-level anomalies come in. They are more rare, but they are more likely to be actionable. Probably not much you can do about that snow storm...

# Future Plans/Support
Potentially support Holidays and add a yearly component. Additional changes are not likely unless there is a specific need. Please open an issue if you have a feature request or find a bug.