import pandas as pd

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data

from src.forecasting.dataset import (
    build_forecasting_dataset,
    prepare_features_and_target
)


# Change this to your actual SIH dataset path.
DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"


def main():

    # ---------------------------------------------------------
    # 1. Load raw market data
    # ---------------------------------------------------------

    print("Loading full market dataset...")
    print("-" * 60)

    df = load_market_data(DATA_PATH)

    print(f"Raw rows: {len(df):,}")

    # ---------------------------------------------------------
    # 2. Standardize source column names
    # ---------------------------------------------------------

    df = standardize_market_data(df)

    print("Columns standardized successfully.")

    # ---------------------------------------------------------
    # 3. Prepare / clean market data
    # ---------------------------------------------------------

    data = prepare_market_data(df)

    print(f"Prepared rows: {len(data):,}")

    # ---------------------------------------------------------
    # 4. Build multi-series forecasting dataset
    # ---------------------------------------------------------

    print("\nBuilding multi-series forecasting dataset...")
    print("-" * 60)

    forecast_df = build_forecasting_dataset(
        data,
        price_column="Modal_Price",
        date_column="Date",
        group_columns=None,
        horizon=1
    )

    print(
        f"Forecasting dataset rows: "
        f"{len(forecast_df):,}"
    )

    print(
        f"Forecasting dataset columns: "
        f"{len(forecast_df.columns):,}"
    )

    # ---------------------------------------------------------
    # 5. Check target availability
    # ---------------------------------------------------------

    target = "target_1d"

    print("\nTarget Availability")
    print("-" * 60)

    available_targets = forecast_df[target].notna().sum()
    missing_targets = forecast_df[target].isna().sum()

    print(
        f"Available targets: "
        f"{available_targets:,}"
    )

    print(
        f"Missing targets: "
        f"{missing_targets:,}"
    )

    # ---------------------------------------------------------
    # 6. Prepare global model features
    # ---------------------------------------------------------

    print("\nPreparing global model features...")
    print("-" * 60)

    X, y, clean_data = prepare_features_and_target(
        forecast_df,
        target_column=target,
        include_categorical=True
    )

    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")

    print(
        f"\nNumber of features: "
        f"{X.shape[1]:,}"
    )

    print(
        f"Missing values in X: "
        f"{X.isna().sum().sum():,}"
    )

    print(
        f"Missing values in y: "
        f"{y.isna().sum():,}"
    )

    # ---------------------------------------------------------
    # 7. Inspect feature names
    # ---------------------------------------------------------

    print("\nFirst 10 feature names")
    print("-" * 60)

    print(
        X.columns[:10].tolist()
    )

    print("\nLast 10 feature names")
    print("-" * 60)

    print(
        X.columns[-10:].tolist()
    )

    # ---------------------------------------------------------
    # 8. Basic multi-series information
    # ---------------------------------------------------------

    series_columns = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade"
    ]

    print("\nMulti-Series Information")
    print("-" * 60)

    number_of_series = (
        data[series_columns]
        .drop_duplicates()
        .shape[0]
    )

    print(
        f"Unique time series: "
        f"{number_of_series:,}"
    )

    print(
        f"Unique commodities: "
        f"{data['Commodity'].nunique():,}"
    )

    print(
        f"Unique markets: "
        f"{data['Market'].nunique():,}"
    )

    print(
        f"Unique states: "
        f"{data['State'].nunique():,}"
    )

    print(
        f"Date range: "
        f"{data['Date'].min().date()} "
        f"→ "
        f"{data['Date'].max().date()}"
    )

    # ---------------------------------------------------------
    # 9. Final status
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("MULTI-SERIES DATASET TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()