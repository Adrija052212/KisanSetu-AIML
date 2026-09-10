import pandas as pd


# Columns that our KisanSetu market-price dataset is expected to have
REQUIRED_COLUMNS = [
    "Date",
    "State",
    "District",
    "Market",
    "Commodity_Group",
    "Commodity",
    "Variety",
    "Grade",
    "Min_Price",
    "Max_Price",
    "Modal_Price",
    "Price_Unit",
    "Arrival_Quantity",
    "Arrival_Unit"
]


def validate_columns(df):
    """
    Check whether all required columns are present.

    Parameters:
        df (pandas.DataFrame): Dataset to validate.

    Returns:
        bool: True if all required columns exist.
    """

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        print("Missing required columns:")
        for column in missing_columns:
            print(f"  - {column}")

        return False

    return True


def validate_prices(df):
    """
    Check whether price columns contain valid numeric values
    and whether the minimum, modal and maximum prices
    follow the expected order.

    Parameters:
        df (pandas.DataFrame): Dataset to validate.

    Returns:
        bool: True if prices are valid.
    """

    price_columns = [
        "Min_Price",
        "Max_Price",
        "Modal_Price"
    ]

    valid = True

    # Check whether price columns are numeric
    for column in price_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"ERROR: {column} contains non-numeric values.")
            valid = False

    # Stop here if the columns themselves are not numeric
    if not valid:
        return False

    # Check for negative prices
    negative_prices = (
        (df["Min_Price"] < 0) |
        (df["Max_Price"] < 0) |
        (df["Modal_Price"] < 0)
    ).sum()

    if negative_prices > 0:
        print(
            f"ERROR: {negative_prices} rows contain negative prices."
        )
        valid = False

    # Check price ordering
    invalid_order = (
        (df["Min_Price"] > df["Modal_Price"]) |
        (df["Modal_Price"] > df["Max_Price"])
    ).sum()

    if invalid_order > 0:
        print(
            f"ERROR: {invalid_order} rows have invalid price ordering."
        )
        valid = False

    return valid


def validate_dates(df):
    """
    Check whether the Date column can be interpreted as dates.

    Parameters:
        df (pandas.DataFrame): Dataset to validate.

    Returns:
        bool: True if the dates are valid.
    """

    converted_dates = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    invalid_dates = converted_dates.isna().sum()

    if invalid_dates > 0:
        print(
            f"ERROR: {invalid_dates} rows contain invalid dates."
        )
        return False

    return True


def validate_empty_rows(df):
    """
    Check whether the dataset contains completely empty rows.

    Parameters:
        df (pandas.DataFrame): Dataset to validate.

    Returns:
        bool: True if there are no completely empty rows.
    """

    empty_rows = df.isna().all(axis=1).sum()

    if empty_rows > 0:
        print(
            f"ERROR: {empty_rows} completely empty rows found."
        )
        return False

    return True


def validate_duplicates(df):
    """
    Check for completely duplicated rows.

    Parameters:
        df (pandas.DataFrame): Dataset to validate.

    Returns:
        bool: True if no duplicate rows are found.
    """

    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        print(
            f"WARNING: {duplicate_rows} duplicate rows found."
        )
        return False

    return True


def validate_dataset(df):
    """
    Run all validation checks on the dataset.

    Parameters:
        df (pandas.DataFrame): Dataset to validate.

    Returns:
        bool: True if all validation checks pass.
    """

    print("\nStarting dataset validation...")
    print("-" * 40)

    # Check columns first
    columns_valid = validate_columns(df)

    # If required columns are missing, other checks cannot be performed
    if not columns_valid:
        print("\nDataset validation FAILED.")
        return False

    dates_valid = validate_dates(df)
    prices_valid = validate_prices(df)
    empty_rows_valid = validate_empty_rows(df)
    duplicates_valid = validate_duplicates(df)

    all_valid = (
        columns_valid
        and dates_valid
        and prices_valid
        and empty_rows_valid
        and duplicates_valid
    )

    print("-" * 40)

    if all_valid:
        print("Dataset validation PASSED.")
    else:
        print("Dataset validation FAILED.")

    return all_valid