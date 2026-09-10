import pandas as pd

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data

from src.forecasting.dataset import (
    build_forecasting_dataset
)

from src.forecasting.split import (
    chronological_split,
    print_split_summary
)

from src.forecasting.baseline import (
    evaluate_naive_baseline,
    print_metrics
)


DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"


def main():

    # --------------------------------------------------------
    # Load and prepare data
    # --------------------------------------------------------

    print("Loading market dataset...")
    print("-" * 60)

    df = load_market_data(DATA_PATH)

    print(f"Raw rows: {len(df):,}")

    df = standardize_market_data(df)

    data = prepare_market_data(df)

    print(f"Prepared rows: {len(data):,}")

    # --------------------------------------------------------
    # Build forecasting dataset
    # --------------------------------------------------------

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
        f"Forecasting rows: "
        f"{len(forecast_df):,}"
    )

    # Only rows with a known future price.
    forecast_df = forecast_df[
        forecast_df["target_1d"].notna()
    ].copy()

    print(
        f"Rows with available target: "
        f"{len(forecast_df):,}"
    )

    # --------------------------------------------------------
    # Chronological split
    # --------------------------------------------------------

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
        test_df
    )

    # --------------------------------------------------------
    # Evaluate Naive baseline
    # --------------------------------------------------------

    print("\nEvaluating global Naive baseline...")
    print("-" * 60)

    train_metrics = evaluate_naive_baseline(
        train_df
    )

    validation_metrics = evaluate_naive_baseline(
        validation_df
    )

    test_metrics = evaluate_naive_baseline(
        test_df
    )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print_metrics(
        "TRAIN — Naive Baseline",
        train_metrics
    )

    print_metrics(
        "VALIDATION — Naive Baseline",
        validation_metrics
    )

    print_metrics(
        "TEST — Naive Baseline",
        test_metrics
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = pd.DataFrame([
        {
            "Model": "Naive",
            "Split": "Train",
            **train_metrics
        },
        {
            "Model": "Naive",
            "Split": "Validation",
            **validation_metrics
        },
        {
            "Model": "Naive",
            "Split": "Test",
            **test_metrics
        }
    ])

    output_path = (
        "data/processed/"
        "global_naive_baseline_results.csv"
    )

    results.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nResults saved to: {output_path}"
    )

    print("\n" + "=" * 60)
    print("GLOBAL NAIVE BASELINE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()