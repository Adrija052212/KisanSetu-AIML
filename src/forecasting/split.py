import pandas as pd


def chronological_split(
    df,
    date_column="Date",
    train_ratio=0.70,
    validation_ratio=0.15,
    test_ratio=0.15
):
    """
    Split a time-series dataset chronologically.

    The split is performed using global dates, meaning every
    time series follows the same train/validation/test boundaries.

    Parameters
    ----------
    df : pandas.DataFrame
        Forecasting dataset.

    date_column : str
        Name of the date column.

    train_ratio : float
        Proportion of dates used for training.

    validation_ratio : float
        Proportion of dates used for validation.

    test_ratio : float
        Proportion of dates used for testing.

    Returns
    -------
    train_df, validation_df, test_df
    """

    if date_column not in df.columns:
        raise ValueError(
            f"Missing date column: {date_column}"
        )

    total_ratio = (
        train_ratio
        + validation_ratio
        + test_ratio
    )

    if abs(total_ratio - 1.0) > 1e-9:
        raise ValueError(
            "train_ratio + validation_ratio + test_ratio "
            "must equal 1.0"
        )

    if (
        train_ratio <= 0
        or validation_ratio <= 0
        or test_ratio <= 0
    ):
        raise ValueError(
            "All split ratios must be greater than 0."
        )

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[date_column]
    )

    data = data.sort_values(
        date_column
    ).reset_index(drop=True)

    # Get unique calendar dates.
    unique_dates = (
        data[date_column]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    number_of_dates = len(unique_dates)

    if number_of_dates < 3:
        raise ValueError(
            "Not enough unique dates for a chronological split."
        )

    # Determine date boundaries.
    train_end_index = int(
        number_of_dates * train_ratio
    ) - 1

    validation_end_index = int(
        number_of_dates
        * (train_ratio + validation_ratio)
    ) - 1

    train_end_index = max(
        0,
        min(train_end_index, number_of_dates - 3)
    )

    validation_end_index = max(
        train_end_index + 1,
        min(
            validation_end_index,
            number_of_dates - 2
        )
    )

    train_end_date = unique_dates.iloc[
        train_end_index
    ]

    validation_end_date = unique_dates.iloc[
        validation_end_index
    ]

    # Actual split.
    train_df = data[
        data[date_column] <= train_end_date
    ].copy()

    validation_df = data[
        (data[date_column] > train_end_date)
        & (data[date_column] <= validation_end_date)
    ].copy()

    test_df = data[
        data[date_column] > validation_end_date
    ].copy()

    return (
        train_df,
        validation_df,
        test_df
    )


def print_split_summary(
    train_df,
    validation_df,
    test_df,
    date_column="Date"
):
    """
    Print a summary of the chronological split.
    """

    print("\nChronological Split Summary")
    print("-" * 60)

    datasets = [
        ("TRAIN", train_df),
        ("VALIDATION", validation_df),
        ("TEST", test_df)
    ]

    total_rows = (
        len(train_df)
        + len(validation_df)
        + len(test_df)
    )

    for name, dataset in datasets:

        if len(dataset) == 0:
            print(f"{name}: EMPTY")
            continue

        start_date = dataset[date_column].min()
        end_date = dataset[date_column].max()

        print(
            f"{name:<12}"
            f"Rows: {len(dataset):>10,}    "
            f"Dates: {start_date.date()} → {end_date.date()}"
        )

    print("-" * 60)
    print(f"Total rows: {total_rows:,}")

    # Verify there is no temporal overlap.
    if len(train_df) > 0 and len(validation_df) > 0:

        if train_df[date_column].max() >= validation_df[date_column].min():
            raise ValueError(
                "Temporal overlap detected between "
                "TRAIN and VALIDATION."
            )

    if len(validation_df) > 0 and len(test_df) > 0:

        if validation_df[date_column].max() >= test_df[date_column].min():
            raise ValueError(
                "Temporal overlap detected between "
                "VALIDATION and TEST."
            )

    print("Temporal overlap check: PASSED")


def save_split_info(
    train_df,
    validation_df,
    test_df,
    output_path="data/processed/split_summary.csv",
    date_column="Date"
):
    """
    Save train/validation/test date information.
    """

    summary = pd.DataFrame([
        {
            "split": "train",
            "rows": len(train_df),
            "start_date": train_df[date_column].min(),
            "end_date": train_df[date_column].max()
        },
        {
            "split": "validation",
            "rows": len(validation_df),
            "start_date": validation_df[date_column].min(),
            "end_date": validation_df[date_column].max()
        },
        {
            "split": "test",
            "rows": len(test_df),
            "start_date": test_df[date_column].min(),
            "end_date": test_df[date_column].max()
        }
    ])

    summary.to_csv(
        output_path,
        index=False
    )

    print(
        f"Split summary saved to: {output_path}"
    )