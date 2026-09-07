import pandas as pd


COLUMN_MAPPING = {
    "State/UT": "State",
    "District": "District",
    "Market": "Market",
    "Commodity Group": "Commodity_Group",
    "Commodity": "Commodity",
    "Variety": "Variety",
    "Grade": "Grade",
    "Min Price": "Min_Price",
    "Max Price": "Max_Price",
    "Modal Price": "Modal_Price",
    "Price Unit": "Price_Unit",
    "Arrival Quantity": "Arrival_Quantity",
    "Arrival Unit": "Arrival_Unit",
    "Arrival Date": "Date"
}


def standardize_market_data(df):

    data = df.copy()

    # Check whether all original columns exist
    missing_columns = [
        column
        for column in COLUMN_MAPPING
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing source columns: {missing_columns}"
        )

    # Rename columns
    data = data.rename(columns=COLUMN_MAPPING)

    # Convert date
    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    return data