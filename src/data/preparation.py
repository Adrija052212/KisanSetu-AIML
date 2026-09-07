import pandas as pd


SERIES_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade"
]


REQUIRED_COLUMNS = SERIES_COLUMNS + [
    "Date",
    "Min_Price",
    "Max_Price",
    "Modal_Price",
    "Price_Unit"
]


def prepare_market_data(df):

    data = df.copy()

    print(f"Original rows: {len(data):,}")

    # --------------------------------------------------
    # 1. Clean text columns
    # --------------------------------------------------

    text_columns = [
        "State",
        "District",
        "Market",
        "Commodity_Group",
        "Commodity",
        "Variety",
        "Grade",
        "Price_Unit",
        "Arrival_Unit"
    ]

    for column in text_columns:

        if column in data.columns:

            data[column] = (
                data[column]
                .astype("string")
                .str.strip()
            )

    # --------------------------------------------------
    # 2. Handle missing categorical values
    # --------------------------------------------------

    data["Variety"] = data["Variety"].fillna("Unknown")
    data["Grade"] = data["Grade"].fillna("Unknown")

    # --------------------------------------------------
    # 3. Convert date
    # --------------------------------------------------

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    invalid_dates = data["Date"].isna().sum()

    print(f"Invalid dates: {invalid_dates:,}")

    data = data.dropna(
        subset=["Date"]
    )

    # --------------------------------------------------
    # 4. Convert prices to numeric
    # --------------------------------------------------

    price_columns = [
        "Min_Price",
        "Max_Price",
        "Modal_Price"
    ]

    for column in price_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Remove rows with missing prices

    before = len(data)

    data = data.dropna(
        subset=price_columns
    )

    print(
        f"Rows removed due to missing prices: "
        f"{before - len(data):,}"
    )

    # --------------------------------------------------
    # 5. Remove negative prices
    # --------------------------------------------------

    before = len(data)

    data = data[
        (data["Min_Price"] >= 0)
        & (data["Max_Price"] >= 0)
        & (data["Modal_Price"] >= 0)
    ]

    print(
        f"Rows removed due to negative prices: "
        f"{before - len(data):,}"
    )

    # --------------------------------------------------
    # 6. Check price ordering
    # --------------------------------------------------

    before = len(data)

    data = data[
        (data["Min_Price"] <= data["Modal_Price"])
        & (data["Modal_Price"] <= data["Max_Price"])
    ]

    print(
        f"Rows removed due to invalid price ordering: "
        f"{before - len(data):,}"
    )

    # --------------------------------------------------
    # 7. Keep only Rs./Quintal
    # --------------------------------------------------

    data["Price_Unit"] = (
        data["Price_Unit"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    print("\nPrice units:")
    print(data["Price_Unit"].value_counts(dropna=False))

    # For forecasting, target must have one consistent unit

    data = data[
        data["Price_Unit"] == "Rs./Quintal"
    ].copy()

    # --------------------------------------------------
    # 8. Arrival quantity
    # --------------------------------------------------

    if "Arrival_Quantity" in data.columns:

        data["Arrival_Quantity"] = pd.to_numeric(
            data["Arrival_Quantity"],
            errors="coerce"
        )

        negative_arrivals = (
            data["Arrival_Quantity"] < 0
        ).sum()

        print(
            f"Negative arrival quantities: "
            f"{negative_arrivals:,}"
        )

        data.loc[
            data["Arrival_Quantity"] < 0,
            "Arrival_Quantity"
        ] = pd.NA

    # --------------------------------------------------
    # 9. Remove completely duplicated rows
    # --------------------------------------------------

    before = len(data)

    data = data.drop_duplicates()

    print(
        f"Exact duplicate rows removed: "
        f"{before - len(data):,}"
    )

    # --------------------------------------------------
    # 10. Check duplicate series + date
    # --------------------------------------------------

    duplicate_columns = (
        SERIES_COLUMNS + ["Date"]
    )

    duplicate_count = data.duplicated(
        subset=duplicate_columns
    ).sum()

    print(
        f"Duplicate series-date rows: "
        f"{duplicate_count:,}"
    )

    if duplicate_count > 0:

        raise ValueError(
            "Duplicate records found for the same "
            "series and date."
        )

    # --------------------------------------------------
    # 11. Sort
    # --------------------------------------------------

    data = data.sort_values(
        SERIES_COLUMNS + ["Date"]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # Final report
    # --------------------------------------------------

    print("\nFinal dataset:")
    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")

    print(
        f"Date range: "
        f"{data['Date'].min().date()} "
        f"to "
        f"{data['Date'].max().date()}"
    )

    print(
        f"Unique series: "
        f"{data[SERIES_COLUMNS].drop_duplicates().shape[0]:,}"
    )

    return data