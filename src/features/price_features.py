import pandas as pd


SERIES_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade"
]


def create_time_features(df):

    df = df.copy()

    df["day"] = df["Date"].dt.day
    df["month"] = df["Date"].dt.month
    df["year"] = df["Date"].dt.year
    df["day_of_week"] = df["Date"].dt.dayofweek
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)

    return df


def create_lag_features(
    df,
    group_columns=None,
    target_column="Modal_Price"
):

    df = df.copy()

    if group_columns is None:
        group_columns = SERIES_COLUMNS

    df = df.sort_values(
        group_columns + ["Date"]
    ).copy()

    grouped = df.groupby(
        group_columns,
        dropna=False
    )[target_column]

    for lag in [1, 3, 7, 14, 30]:

        df[f"lag_{lag}"] = grouped.shift(lag)

    return df


def create_rolling_features(
    df,
    group_columns=None,
    target_column="Modal_Price"
):

    df = df.copy()

    if group_columns is None:
        group_columns = SERIES_COLUMNS

    df = df.sort_values(
        group_columns + ["Date"]
    ).copy()

    grouped = df.groupby(
        group_columns,
        dropna=False
    )[target_column]

    for window in [7, 14, 30]:

        df[f"rolling_mean_{window}"] = (
            grouped
            .transform(
                lambda x:
                x.shift(1)
                .rolling(window)
                .mean()
            )
        )

        df[f"rolling_std_{window}"] = (
            grouped
            .transform(
                lambda x:
                x.shift(1)
                .rolling(window)
                .std()
            )
        )

    return df


def create_price_change_features(
    df,
    group_columns=None,
    target_column="Modal_Price"
):

    df = df.copy()

    if group_columns is None:
        group_columns = SERIES_COLUMNS

    df = df.sort_values(
        group_columns + ["Date"]
    ).copy()

    grouped = df.groupby(
        group_columns,
        dropna=False
    )[target_column]

    lag_1 = grouped.shift(1)
    lag_7 = grouped.shift(7)
    lag_30 = grouped.shift(30)

    df["price_change_1d"] = (
        (df[target_column] - lag_1)
        / lag_1
    ) * 100

    df["price_change_7d"] = (
        (df[target_column] - lag_7)
        / lag_7
    ) * 100

    df["price_change_30d"] = (
        (df[target_column] - lag_30)
        / lag_30
    ) * 100

    return df


def create_forecasting_target(
    df,
    horizon=1,
    group_columns=None,
    target_column="Modal_Price"
):

    df = df.copy()

    if group_columns is None:
        group_columns = SERIES_COLUMNS

    if horizon < 1:
        raise ValueError(
            "Horizon must be at least 1 day."
        )

    required_columns = (
        group_columns
        + ["Date", target_column]
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

    df["Date"] = pd.to_datetime(df["Date"])

    df["_target_date"] = (
        df["Date"]
        + pd.Timedelta(days=horizon)
    )

    future_prices = df[
        group_columns
        + ["Date", target_column]
    ].copy()

    future_prices = future_prices.rename(
        columns={
            "Date": "_target_date",
            target_column: f"target_{horizon}d"
        }
    )

    df = df.merge(
        future_prices,
        on=group_columns + ["_target_date"],
        how="left"
    )

    df = df.drop(
        columns=["_target_date"]
    )

    return df