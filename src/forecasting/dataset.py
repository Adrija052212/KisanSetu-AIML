import numpy as np
import pandas as pd


SERIES_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade"
]


# ============================================================
# 1. Calendar Features
# ============================================================

def create_calendar_features(data, date_column="Date"):
    data = data.copy()

    date = pd.to_datetime(data[date_column])

    data["day_of_week"] = date.dt.dayofweek
    data["day_of_month"] = date.dt.day
    data["month"] = date.dt.month
    data["quarter"] = date.dt.quarter
    data["day_of_year"] = date.dt.dayofyear
    data["week_of_year"] = date.dt.isocalendar().week.astype(int)

    return data


# ============================================================
# 2. Create Efficient Series IDs
# ============================================================

def create_series_ids(data, group_columns):
    data = data.copy()

    # Each unique combination of:
    # State + District + Market + Commodity + Variety + Grade
    # becomes one time-series ID.

    data["_series_id"] = (
        data[group_columns]
        .astype("string")
        .fillna("Unknown")
        .agg("||".join, axis=1)
        .factorize(sort=False)[0]
    )

    return data


# ============================================================
# 3. Fast Exact Calendar-Day Lags
# ============================================================

def create_calendar_lag_features(
    data,
    price_column="Modal_Price",
    date_column="Date",
    group_columns=None,
    lags=None
):
    if group_columns is None:
        group_columns = SERIES_COLUMNS

    if lags is None:
        lags = [1, 3, 7, 14, 30]

    data = data.copy()

    if "_series_id" not in data.columns:
        data = create_series_ids(data, group_columns)

    data[date_column] = pd.to_datetime(data[date_column])

    # Convert dates into integer day numbers.
    min_date = data[date_column].min()
    date_number = (
        data[date_column] - min_date
    ).dt.days.astype(np.int64)

    data["_date_number"] = date_number

    # Maximum possible date number + 1.
    multiplier = int(data["_date_number"].max()) + 1

    # Unique integer key:
    #
    # series_id * multiplier + date_number
    #
    # This uniquely identifies a series/date combination.

    keys = (
        data["_series_id"].astype(np.int64) * multiplier
        + data["_date_number"]
    )

    values = data[price_column].to_numpy(dtype=float)

    # Sort once.
    order = np.argsort(keys.to_numpy())

    sorted_keys = keys.to_numpy()[order]
    sorted_values = values[order]

    for lag in lags:

        target_keys = (
            data["_series_id"].to_numpy(dtype=np.int64) * multiplier
            + data["_date_number"].to_numpy(dtype=np.int64)
            - lag
        )

        positions = np.searchsorted(
            sorted_keys,
            target_keys
        )

        valid = (
            (positions < len(sorted_keys))
        )

        lag_values = np.full(
            len(data),
            np.nan,
            dtype=float
        )

        valid_positions = positions[valid]

        exact_match = (
            sorted_keys[valid_positions] == target_keys[valid]
        )

        valid_indices = np.where(valid)[0][exact_match]

        lag_values[valid_indices] = (
            sorted_values[valid_positions[exact_match]]
        )

        data[f"lag_{lag}"] = lag_values

    return data


# ============================================================
# 4. Rolling Features
# ============================================================

def create_rolling_features(
    data,
    price_column="Modal_Price",
    group_columns=None
):
    if group_columns is None:
        group_columns = SERIES_COLUMNS

    data = data.copy()

    # Previous-observation rolling features.
    #
    # We shift by one first so that the current price does not
    # enter the historical rolling statistics.

    grouped = data.groupby(
        group_columns,
        sort=False,
        dropna=False
    )[price_column]

    for window in [7, 14, 30]:

        data[f"rolling_mean_{window}"] = (
            grouped
            .transform(
                lambda x: x.shift(1).rolling(
                    window=window,
                    min_periods=1
                ).mean()
            )
        )

        data[f"rolling_std_{window}"] = (
            grouped
            .transform(
                lambda x: x.shift(1).rolling(
                    window=window,
                    min_periods=2
                ).std()
            )
        )

    return data


# ============================================================
# 5. Price Change Features
# ============================================================

def create_price_change_features(
    data,
    price_column="Modal_Price"
):
    data = data.copy()

    # These use calendar-day lag features.
    #
    # Current price is known at prediction time.
    # Therefore:
    #
    # current price - historical price
    #
    # is valid information.

    data["price_change_1"] = (
        data[price_column] - data["lag_1"]
    )

    data["price_change_7"] = (
        data[price_column] - data["lag_7"]
    )

    data["price_change_30"] = (
        data[price_column] - data["lag_30"]
    )

    return data


# ============================================================
# 6. Exact Calendar-Day Forecast Target
# ============================================================

def create_forecasting_target(
    data,
    price_column="Modal_Price",
    date_column="Date",
    group_columns=None,
    horizon=1
):
    if group_columns is None:
        group_columns = SERIES_COLUMNS

    data = data.copy()

    if "_series_id" not in data.columns:
        data = create_series_ids(data, group_columns)

    data[date_column] = pd.to_datetime(data[date_column])

    min_date = data[date_column].min()

    data["_date_number"] = (
        data[date_column] - min_date
    ).dt.days.astype(np.int64)

    multiplier = int(data["_date_number"].max()) + 1

    keys = (
        data["_series_id"].astype(np.int64) * multiplier
        + data["_date_number"]
    )

    values = data[price_column].to_numpy(dtype=float)

    order = np.argsort(keys.to_numpy())

    sorted_keys = keys.to_numpy()[order]
    sorted_values = values[order]

    future_keys = (
        data["_series_id"].to_numpy(dtype=np.int64) * multiplier
        + data["_date_number"].to_numpy(dtype=np.int64)
        + horizon
    )

    positions = np.searchsorted(
        sorted_keys,
        future_keys
    )

    target_values = np.full(
        len(data),
        np.nan,
        dtype=float
    )

    valid = positions < len(sorted_keys)

    valid_positions = positions[valid]

    exact_match = (
        sorted_keys[valid_positions] == future_keys[valid]
    )

    valid_indices = np.where(valid)[0][exact_match]

    target_values[valid_indices] = (
        sorted_values[valid_positions[exact_match]]
    )

    data[f"target_{horizon}d"] = target_values

    return data


# ============================================================
# 7. Complete Forecasting Dataset
# ============================================================

def build_forecasting_dataset(
    df,
    price_column="Modal_Price",
    date_column="Date",
    group_columns=None,
    horizon=1
):
    if group_columns is None:
        group_columns = SERIES_COLUMNS

    required_columns = (
        group_columns
        + [date_column, price_column]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df.copy()

    print("Sorting data by time series and date...")

    data[date_column] = pd.to_datetime(
        data[date_column]
    )

    data = data.sort_values(
        group_columns + [date_column]
    ).reset_index(drop=True)

    print("Creating series IDs...")

    data = create_series_ids(
        data,
        group_columns
    )

    # Current price is known when making the prediction.
    data["current_price"] = data[price_column]

    print("Creating calendar features...")

    data = create_calendar_features(
        data,
        date_column
    )

    print("Creating calendar-day lag features...")

    data = create_calendar_lag_features(
        data,
        price_column=price_column,
        date_column=date_column,
        group_columns=group_columns,
        lags=[1, 3, 7, 14, 30]
    )

    print("Creating rolling features...")

    data = create_rolling_features(
        data,
        price_column=price_column,
        group_columns=group_columns
    )

    print("Creating price-change features...")

    data = create_price_change_features(
        data,
        price_column=price_column
    )

    print("Creating forecasting target...")

    data = create_forecasting_target(
        data,
        price_column=price_column,
        date_column=date_column,
        group_columns=group_columns,
        horizon=horizon
    )

    # Remove internal helper columns.
    data = data.drop(
        columns=[
            "_series_id",
            "_date_number"
        ],
        errors="ignore"
    )

    print("Forecasting dataset construction complete.")

    return data


# ============================================================
# 8. Prepare Features and Target
# ============================================================

def prepare_features_and_target(
    data,
    target_column="target_1d",
    include_categorical=True
):
    data = data.copy()

    numeric_features = [
        "current_price",
        "lag_1",
        "lag_3",
        "lag_7",
        "lag_14",
        "lag_30",

        "rolling_mean_7",
        "rolling_std_7",

        "rolling_mean_14",
        "rolling_std_14",

        "rolling_mean_30",
        "rolling_std_30",

        "price_change_1",
        "price_change_7",
        "price_change_30",

        "Arrival_Quantity",

        "day_of_week",
        "day_of_month",
        "month",
        "quarter",
        "day_of_year",
        "week_of_year"
    ]

    numeric_features = [
        column
        for column in numeric_features
        if column in data.columns
    ]

    categorical_features = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade"
    ]

    categorical_features = [
        column
        for column in categorical_features
        if column in data.columns
    ]

    # Only rows with a known future target can be used for training.
    clean_data = data[
        data[target_column].notna()
    ].copy()

    X_numeric = clean_data[
        numeric_features
    ].copy()

    # Numeric conversion.
    for column in X_numeric.columns:
        X_numeric[column] = pd.to_numeric(
            X_numeric[column],
            errors="coerce"
        )

    # Fill missing numeric values.
    for column in X_numeric.columns:
        median_value = X_numeric[column].median()

        if pd.isna(median_value):
            median_value = 0

        X_numeric[column] = (
            X_numeric[column]
            .fillna(median_value)
        )

    if include_categorical:

        # One-hot encode categorical variables.
        #
        # This is still potentially large for Market/District,
        # but we keep it separate from dataset construction.
        # We can replace this with a more memory-efficient
        # encoding before training the global model.

        X_categorical = pd.get_dummies(
            clean_data[categorical_features],
            dtype=np.float32
        )

        X = pd.concat(
            [
                X_numeric.astype(np.float32),
                X_categorical
            ],
            axis=1
        )

    else:
        X = X_numeric.astype(np.float32)

    y = pd.to_numeric(
        clean_data[target_column],
        errors="coerce"
    )

    y = y.astype(np.float32)

    return X, y, clean_data