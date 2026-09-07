import pandas as pd
import numpy as np

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data


# ============================================================
# CONFIGURATION
# ============================================================

RAW_FILE = "data/raw/SIH_Cleaned_Dataset.xlsx"

OUTPUT_FILE = (
    "data/processed/time_series_baseline_results.csv"
)

SERIES_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade"
]


# ============================================================
# 1. LOAD + STANDARDIZE + PREPARE DATA
# ============================================================

def prepare_base_dataset():

    print("Loading raw data...")

    raw_data = load_market_data(RAW_FILE)

    print(f"Raw rows: {len(raw_data):,}")

    print("Standardizing columns...")

    standardized_data = standardize_market_data(
        raw_data
    )

    print("Preparing market data...")

    prepared_data = prepare_market_data(
        standardized_data
    )

    prepared_data["Date"] = pd.to_datetime(
        prepared_data["Date"],
        errors="coerce"
    )

    prepared_data["Modal_Price"] = pd.to_numeric(
        prepared_data["Modal_Price"],
        errors="coerce"
    )

    prepared_data = prepared_data.dropna(
        subset=["Date", "Modal_Price"]
    )

    prepared_data = prepared_data.sort_values(
        SERIES_COLUMNS + ["Date"]
    ).reset_index(drop=True)

    print(
        f"Prepared rows: {len(prepared_data):,}"
    )

    print(
        f"Date range: "
        f"{prepared_data['Date'].min().date()} → "
        f"{prepared_data['Date'].max().date()}"
    )

    return prepared_data


# ============================================================
# 2. CREATE SERIES ID
# ============================================================

def create_series_ids(df):

    data = df.copy()

    data["Series_ID"] = (
        data[SERIES_COLUMNS]
        .fillna("Unknown")
        .astype(str)
        .agg("||".join, axis=1)
    )

    return data


# ============================================================
# 3. CREATE EXACT NEXT-DAY TARGET
# ============================================================

def create_target_1d(df):

    data = df.copy()

    # Lookup table:
    # (Series_ID, Date) -> Modal_Price

    price_lookup = (
        data[
            ["Series_ID", "Date", "Modal_Price"]
        ]
        .drop_duplicates(
            ["Series_ID", "Date"]
        )
        .set_index(
            ["Series_ID", "Date"]
        )["Modal_Price"]
    )

    # Exact calendar next-day date
    next_day = data["Date"] + pd.Timedelta(days=1)

    lookup_index = pd.MultiIndex.from_arrays(
        [
            data["Series_ID"].values,
            next_day.values
        ],
        names=["Series_ID", "Date"]
    )

    data["Target_1D"] = (
        price_lookup.reindex(
            lookup_index
        ).values
    )

    return data


# ============================================================
# 4. CREATE EXACT HISTORICAL PRICE LOOKUP
# ============================================================

def create_price_lookup(df):

    lookup = (
        df[
            ["Series_ID", "Date", "Modal_Price"]
        ]
        .drop_duplicates(
            ["Series_ID", "Date"]
        )
        .set_index(
            ["Series_ID", "Date"]
        )["Modal_Price"]
    )

    return lookup


# ============================================================
# 5. CREATE CHRONOLOGICAL SPLIT
# ============================================================

def create_chronological_split(df):

    unique_dates = np.sort(
        df["Date"].dropna().unique()
    )

    n_dates = len(unique_dates)

    train_end = int(n_dates * 0.70)

    validation_end = int(n_dates * 0.85)

    train_dates = unique_dates[
        :train_end
    ]

    validation_dates = unique_dates[
        train_end:validation_end
    ]

    test_dates = unique_dates[
        validation_end:
    ]

    train = df[
        df["Date"].isin(train_dates)
    ].copy()

    validation = df[
        df["Date"].isin(validation_dates)
    ].copy()

    test = df[
        df["Date"].isin(test_dates)
    ].copy()

    print("\nChronological split:")

    print(
        f"TRAIN      : {len(train):,} rows | "
        f"{train['Date'].min().date()} → "
        f"{train['Date'].max().date()}"
    )

    print(
        f"VALIDATION : {len(validation):,} rows | "
        f"{validation['Date'].min().date()} → "
        f"{validation['Date'].max().date()}"
    )

    print(
        f"TEST       : {len(test):,} rows | "
        f"{test['Date'].min().date()} → "
        f"{test['Date'].max().date()}"
    )

    return train, validation, test


# ============================================================
# 6. GET EXACT CALENDAR-DAY PRICE
# ============================================================

def get_price(
    lookup,
    series_id,
    date
):

    try:

        return lookup.loc[
            (series_id, date)
        ]

    except KeyError:

        return np.nan


# ============================================================
# 7. GENERATE BASELINE PREDICTIONS
# ============================================================

def generate_baseline_predictions(
    df,
    price_lookup
):

    results = []

    for row in df.itertuples(
        index=False
    ):

        series_id = row.Series_ID

        current_date = row.Date

        current_price = row.Modal_Price

        actual_next_day = row.Target_1D

        # ----------------------------------------------------
        # NAIVE
        #
        # Tomorrow's price = today's price
        # ----------------------------------------------------

        naive_prediction = current_price

        # ----------------------------------------------------
        # MA3
        #
        # Tomorrow's price =
        # average of today + previous 2 days
        #
        # All dates must exist exactly.
        # ----------------------------------------------------

        ma3_prices = []

        for days_back in range(0, 3):

            historical_date = (
                current_date
                - pd.Timedelta(
                    days=days_back
                )
            )

            price = get_price(
                price_lookup,
                series_id,
                historical_date
            )

            ma3_prices.append(price)

        if all(
            pd.notna(price)
            for price in ma3_prices
        ):

            ma3_prediction = np.mean(
                ma3_prices
            )

        else:

            ma3_prediction = np.nan

        # ----------------------------------------------------
        # MA7
        #
        # Tomorrow's price =
        # average of today + previous 6 days
        # ----------------------------------------------------

        ma7_prices = []

        for days_back in range(0, 7):

            historical_date = (
                current_date
                - pd.Timedelta(
                    days=days_back
                )
            )

            price = get_price(
                price_lookup,
                series_id,
                historical_date
            )

            ma7_prices.append(price)

        if all(
            pd.notna(price)
            for price in ma7_prices
        ):

            ma7_prediction = np.mean(
                ma7_prices
            )

        else:

            ma7_prediction = np.nan

        # ----------------------------------------------------
        # SEASONAL NAIVE 7D
        #
        # Tomorrow's price =
        # price exactly 7 calendar days ago
        # ----------------------------------------------------

        seasonal_date = (
            current_date
            - pd.Timedelta(days=7)
        )

        seasonal_prediction = get_price(
            price_lookup,
            series_id,
            seasonal_date
        )

        results.append(
            {
                "Series_ID": series_id,
                "Forecast_Date": current_date,

                "Actual_Next_Day":
                    actual_next_day,

                "Current_Price":
                    current_price,

                "Naive":
                    naive_prediction,

                "MA3":
                    ma3_prediction,

                "MA7":
                    ma7_prediction,

                "Seasonal_Naive_7D":
                    seasonal_prediction
            }
        )

    return pd.DataFrame(results)


# ============================================================
# 8. CALCULATE METRICS
# ============================================================

def calculate_metrics(
    actual,
    predicted,
    current_price
):

    mask = (
        actual.notna()
        & predicted.notna()
        & current_price.notna()
    )

    actual = actual[mask]

    predicted = predicted[mask]

    current_price = current_price[mask]

    if len(actual) == 0:

        return {
            "MAE": np.nan,
            "RMSE": np.nan,
            "MAPE": np.nan,
            "Directional_Accuracy": np.nan,
            "Observations": 0
        }

    # --------------------------------------------------------
    # MAE
    # --------------------------------------------------------

    errors = (
        actual.values
        - predicted.values
    )

    mae = np.mean(
        np.abs(errors)
    )

    # --------------------------------------------------------
    # RMSE
    # --------------------------------------------------------

    rmse = np.sqrt(
        np.mean(
            errors ** 2
        )
    )

    # --------------------------------------------------------
    # MAPE
    #
    # Ignore actual price = 0
    # --------------------------------------------------------

    non_zero = (
        actual.values != 0
    )

    if np.sum(non_zero) > 0:

        mape = np.mean(
            np.abs(
                (
                    actual.values[non_zero]
                    - predicted.values[non_zero]
                )
                / actual.values[non_zero]
            )
        ) * 100

    else:

        mape = np.nan

    # --------------------------------------------------------
    # DIRECTIONAL ACCURACY
    #
    # Compare tomorrow's movement relative to today's price.
    #
    # Actual direction:
    # actual tomorrow - current today
    #
    # Predicted direction:
    # predicted tomorrow - current today
    # --------------------------------------------------------

    actual_direction = np.sign(
        actual.values
        - current_price.values
    )

    predicted_direction = np.sign(
        predicted.values
        - current_price.values
    )

    directional_accuracy = (
        np.mean(
            actual_direction
            == predicted_direction
        )
        * 100
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "Directional_Accuracy":
            directional_accuracy,
        "Observations": len(actual)
    }


# ============================================================
# 9. EVALUATE SPLIT
# ============================================================

def evaluate_split(
    predictions,
    split_name
):

    results = []

    actual = predictions[
        "Actual_Next_Day"
    ]

    current_price = predictions[
        "Current_Price"
    ]

    models = [
        "Naive",
        "MA3",
        "MA7",
        "Seasonal_Naive_7D"
    ]

    for model in models:

        metrics = calculate_metrics(
            actual,
            predictions[model],
            current_price
        )

        results.append(
            {
                "Split": split_name,
                "Model": model,
                **metrics
            }
        )

    return results


# ============================================================
# 10. MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "TIME-SERIES BASELINE EVALUATION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    data = prepare_base_dataset()

    # --------------------------------------------------------
    # Create series IDs
    # --------------------------------------------------------

    data = create_series_ids(data)

    # --------------------------------------------------------
    # Create exact 1-day-ahead target
    # --------------------------------------------------------

    print(
        "\nCreating exact next-calendar-day target..."
    )

    data = create_target_1d(data)

    target_count = (
        data["Target_1D"]
        .notna()
        .sum()
    )

    print(
        f"Rows with next-day target: "
        f"{target_count:,}"
    )

    print(
        f"Rows without next-day target: "
        f"{len(data) - target_count:,}"
    )

    # --------------------------------------------------------
    # Remove rows that cannot be evaluated
    # --------------------------------------------------------

    data = data[
        data["Target_1D"].notna()
    ].copy()

    print(
        f"Forecasting rows: "
        f"{len(data):,}"
    )

    # --------------------------------------------------------
    # Chronological split
    # --------------------------------------------------------

    train, validation, test = (
        create_chronological_split(data)
    )

    # --------------------------------------------------------
    # Historical price lookup
    # --------------------------------------------------------

    price_lookup = create_price_lookup(
        data
    )

    # --------------------------------------------------------
    # Generate predictions
    # --------------------------------------------------------

    print(
        "\nGenerating TRAIN predictions..."
    )

    train_predictions = (
        generate_baseline_predictions(
            train,
            price_lookup
        )
    )

    print(
        "Generating VALIDATION predictions..."
    )

    validation_predictions = (
        generate_baseline_predictions(
            validation,
            price_lookup
        )
    )

    print(
        "Generating TEST predictions..."
    )

    test_predictions = (
        generate_baseline_predictions(
            test,
            price_lookup
        )
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    all_results = []

    all_results.extend(
        evaluate_split(
            train_predictions,
            "TRAIN"
        )
    )

    all_results.extend(
        evaluate_split(
            validation_predictions,
            "VALIDATION"
        )
    )

    all_results.extend(
        evaluate_split(
            test_predictions,
            "TEST"
        )
    )

    results_df = pd.DataFrame(
        all_results
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x:
                f"{x:.2f}"
        )
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()