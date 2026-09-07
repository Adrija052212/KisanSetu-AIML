import pandas as pd

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data

from src.forecasting.dataset import (
    build_forecasting_dataset
)

from src.forecasting.split import (
    chronological_split,
    print_split_summary,
    save_split_info
)


DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"


def main():

    print("Loading market dataset...")
    print("-" * 60)

    df = load_market_data(DATA_PATH)

    print(f"Raw rows: {len(df):,}")

    df = standardize_market_data(df)

    data = prepare_market_data(df)

    print(f"Prepared rows: {len(data):,}")

    print("\nBuilding forecasting dataset...")
    print("-" * 60)

    forecast_df = build_forecasting_dataset(
        data,
        price_column="Modal_Price",
        date_column="Date",
        group_columns=None,
        horizon=1
    )

    print(
        f"Forecasting rows: {len(forecast_df):,}"
    )

    # Only rows with a known future target can
    # participate in model evaluation.
    forecast_df = forecast_df[
        forecast_df["target_1d"].notna()
    ].copy()

    print(
        f"Rows with available target: "
        f"{len(forecast_df):,}"
    )

    print("\nCreating chronological split...")
    print("-" * 60)

    train_df, validation_df, test_df = (
        chronological_split(
            forecast_df,
            date_column="Date",
            train_ratio=0.70,
            validation_ratio=0.15,
            test_ratio=0.15
        )
    )

    print_split_summary(
        train_df,
        validation_df,
        test_df,
        date_column="Date"
    )

    save_split_info(
        train_df,
        validation_df,
        test_df,
        output_path="data/processed/split_summary.csv",
        date_column="Date"
    )

    print("\nChecking target availability...")
    print("-" * 60)

    print(
        f"Train target missing: "
        f"{train_df['target_1d'].isna().sum():,}"
    )

    print(
        f"Validation target missing: "
        f"{validation_df['target_1d'].isna().sum():,}"
    )

    print(
        f"Test target missing: "
        f"{test_df['target_1d'].isna().sum():,}"
    )

    print("\n" + "=" * 60)
    print("CHRONOLOGICAL SPLIT TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()