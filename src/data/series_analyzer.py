import pandas as pd


DEFAULT_GROUP_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade"
]


def analyze_time_series(
    df,
    group_columns=None,
    date_column="Date"
):
    """
    Analyze the quality and continuity of individual
    agricultural price time series.
    """

    if group_columns is None:
        group_columns = DEFAULT_GROUP_COLUMNS

    required_columns = group_columns + [date_column]

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

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=group_columns + [date_column]
    )

    results = []

    grouped = data.groupby(
        group_columns,
        dropna=False
    )

    for group_values, group_df in grouped:

        dates = (
            group_df[date_column]
            .drop_duplicates()
            .sort_values()
        )

        observations = len(dates)

        start_date = dates.min()
        end_date = dates.max()

        calendar_span_days = (
            end_date - start_date
        ).days + 1

        if observations > 1:

            gaps = dates.diff().dt.days.dropna()

            median_gap_days = gaps.median()
            max_gap_days = gaps.max()

            consecutive_day_pairs = (
                gaps == 1
            ).sum()

            continuity_pct = (
                consecutive_day_pairs
                / len(gaps)
            ) * 100

        else:

            median_gap_days = None
            max_gap_days = None
            consecutive_day_pairs = 0
            continuity_pct = 0

        if not isinstance(group_values, tuple):
            group_values = (group_values,)

        row = dict(
            zip(group_columns, group_values)
        )

        row.update({
            "observations": observations,
            "start_date": start_date,
            "end_date": end_date,
            "calendar_span_days": calendar_span_days,
            "median_gap_days": median_gap_days,
            "max_gap_days": max_gap_days,
            "consecutive_day_pairs": consecutive_day_pairs,
            "continuity_pct": continuity_pct
        })

        results.append(row)

    return pd.DataFrame(results)


def print_series_summary(
    df,
    group_columns=None,
    date_column="Date"
):
    """
    Print an overall summary of the time-series dataset.
    """

    if group_columns is None:
        group_columns = DEFAULT_GROUP_COLUMNS

    print("\nTime-Series Summary")
    print("-" * 50)

    number_of_series = (
        df[group_columns]
        .drop_duplicates()
        .shape[0]
    )

    print(f"Total observations: {len(df):,}")
    print(f"Unique time series: {number_of_series:,}")

    if date_column in df.columns:

        dates = pd.to_datetime(
            df[date_column],
            errors="coerce"
        )

        print(f"Earliest date: {dates.min()}")
        print(f"Latest date:   {dates.max()}")

    duplicate_series_dates = df.duplicated(
        subset=group_columns + [date_column]
    ).sum()

    print(
        "Duplicate series-date rows: "
        f"{duplicate_series_dates:,}"
    )

    print("-" * 50)