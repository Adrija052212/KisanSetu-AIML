import pandas as pd


PRICE_COLUMNS = [
    "Min_Price",
    "Max_Price",
    "Modal_Price"
]

TEXT_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety"
]


def clean_market_data(df):
    """
    Clean agricultural market-price data for the KisanSetu ML pipeline.

    The function:
    - creates a copy of the original DataFrame
    - removes completely empty rows
    - removes duplicate records
    - converts Date to datetime
    - converts price columns to numeric
    - removes rows with invalid dates
    - removes rows with invalid or negative prices
    - removes rows with impossible price ordering
    - cleans whitespace from text columns
    - sorts the data chronologically

    Parameters:
        df (pandas.DataFrame): Raw market-price dataset.

    Returns:
        pandas.DataFrame: Cleaned market-price dataset.
    """

    print("\nStarting data cleaning...")
    print("-" * 40)

    # Work on a copy so that the original DataFrame is not modified
    cleaned_df = df.copy()

    initial_rows = len(cleaned_df)

    # ---------------------------------------------------------
    # 1. Remove completely empty rows
    # ---------------------------------------------------------
    cleaned_df = cleaned_df.dropna(how="all")

    removed_empty = initial_rows - len(cleaned_df)

    if removed_empty > 0:
        print(f"Removed {removed_empty} completely empty rows.")

    # ---------------------------------------------------------
    # 2. Remove exact duplicate rows
    # ---------------------------------------------------------
    before_duplicates = len(cleaned_df)

    cleaned_df = cleaned_df.drop_duplicates()

    removed_duplicates = (
        before_duplicates - len(cleaned_df)
    )

    if removed_duplicates > 0:
        print(f"Removed {removed_duplicates} duplicate rows.")

    # ---------------------------------------------------------
    # 3. Clean text columns
    # ---------------------------------------------------------
    for column in TEXT_COLUMNS:

        # Only process the column if it exists
        if column in cleaned_df.columns:

            cleaned_df[column] = (
                cleaned_df[column]
                .astype("string")
                .str.strip()
            )

            # Convert empty strings to missing values
            cleaned_df[column] = (
                cleaned_df[column]
                .replace("", pd.NA)
            )

    # ---------------------------------------------------------
    # 4. Convert Date column to datetime
    # ---------------------------------------------------------
    if "Date" in cleaned_df.columns:

        cleaned_df["Date"] = pd.to_datetime(
            cleaned_df["Date"],
            errors="coerce"
        )

        invalid_dates = cleaned_df["Date"].isna().sum()

        if invalid_dates > 0:
            print(
                f"Removed {invalid_dates} rows with invalid dates."
            )

            cleaned_df = cleaned_df.dropna(
                subset=["Date"]
            )

    # ---------------------------------------------------------
    # 5. Convert price columns to numeric
    # ---------------------------------------------------------
    for column in PRICE_COLUMNS:

        if column in cleaned_df.columns:

            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

    # ---------------------------------------------------------
    # 6. Remove rows with missing price values
    # ---------------------------------------------------------
    existing_price_columns = [
        column
        for column in PRICE_COLUMNS
        if column in cleaned_df.columns
    ]

    if existing_price_columns:

        before_missing_prices = len(cleaned_df)

        cleaned_df = cleaned_df.dropna(
            subset=existing_price_columns
        )

        removed_missing_prices = (
            before_missing_prices - len(cleaned_df)
        )

        if removed_missing_prices > 0:
            print(
                f"Removed {removed_missing_prices} rows "
                f"with missing price values."
            )

    # ---------------------------------------------------------
    # 7. Remove negative prices
    # ---------------------------------------------------------
    if existing_price_columns:

        negative_price_mask = (
            cleaned_df[existing_price_columns] < 0
        ).any(axis=1)

        negative_prices = negative_price_mask.sum()

        if negative_prices > 0:
            print(
                f"Removed {negative_prices} rows "
                f"with negative prices."
            )

            cleaned_df = cleaned_df[
                ~negative_price_mask
            ]

    # ---------------------------------------------------------
    # 8. Check price ordering
    # ---------------------------------------------------------
    required_price_columns = all(
        column in cleaned_df.columns
        for column in PRICE_COLUMNS
    )

    if required_price_columns:

        invalid_order_mask = (
            (cleaned_df["Min_Price"] >
             cleaned_df["Modal_Price"])
            |
            (cleaned_df["Modal_Price"] >
             cleaned_df["Max_Price"])
        )

        invalid_order = invalid_order_mask.sum()

        if invalid_order > 0:
            print(
                f"Removed {invalid_order} rows "
                f"with invalid price ordering."
            )

            cleaned_df = cleaned_df[
                ~invalid_order_mask
            ]

    # ---------------------------------------------------------
    # 9. Sort chronologically
    # ---------------------------------------------------------
    if "Date" in cleaned_df.columns:

        cleaned_df = cleaned_df.sort_values(
            by="Date"
        )

    # ---------------------------------------------------------
    # 10. Reset the index
    # ---------------------------------------------------------
    cleaned_df = cleaned_df.reset_index(
        drop=True
    )

    final_rows = len(cleaned_df)

    total_removed = initial_rows - final_rows

    print("-" * 40)
    print(f"Initial rows: {initial_rows}")
    print(f"Final rows:   {final_rows}")
    print(f"Total removed: {total_removed}")
    print("Data cleaning completed.")

    return cleaned_df