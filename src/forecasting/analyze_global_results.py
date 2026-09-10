import numpy as np
import pandas as pd

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data
from src.forecasting.dataset import build_forecasting_dataset
from src.forecasting.split import chronological_split


DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"
RF_RESULTS_PATH = "data/processed/global_random_forest_results.csv"


SERIES_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade"
]


def main():

    print("=" * 70)
    print("GLOBAL FORECASTING DIAGNOSTIC ANALYSIS")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. LOAD AND PREPARE DATA
    # ---------------------------------------------------------

    print("\nLoading market dataset...")
    print("-" * 70)

    raw_df = load_market_data(DATA_PATH)
    standardized_df = standardize_market_data(raw_df)
    prepared_df = prepare_market_data(standardized_df)

    print(f"Prepared rows: {len(prepared_df):,}")

    # ---------------------------------------------------------
    # 2. BUILD FORECASTING DATASET
    # ---------------------------------------------------------

    print("\nBuilding forecasting dataset...")
    print("-" * 70)

    forecasting_df = build_forecasting_dataset(
        prepared_df,
        horizon=1
    )

    forecasting_df = forecasting_df[
        forecasting_df["target_1d"].notna()
    ].copy()

    print(f"Rows with target: {len(forecasting_df):,}")

    # ---------------------------------------------------------
    # 3. CHRONOLOGICAL SPLIT
    # ---------------------------------------------------------

    print("\nCreating chronological split...")
    print("-" * 70)

    train_df, validation_df, test_df = chronological_split(
        forecasting_df
    )

    print(f"Train rows:      {len(train_df):,}")
    print(f"Validation rows: {len(validation_df):,}")
    print(f"Test rows:       {len(test_df):,}")

    # ---------------------------------------------------------
    # 4. BASIC DATASET ANALYSIS
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("1. DATASET OVERVIEW")
    print("=" * 70)

    print(f"\nTotal observations: {len(forecasting_df):,}")

    number_of_series = (
        forecasting_df[SERIES_COLUMNS]
        .drop_duplicates()
        .shape[0]
    )

    print(f"Unique series:      {number_of_series:,}")

    print(
        f"Unique commodities: "
        f"{forecasting_df['Commodity'].nunique():,}"
    )

    print(
        f"Unique markets:     "
        f"{forecasting_df['Market'].nunique():,}"
    )

    print(
        f"Unique states:      "
        f"{forecasting_df['State'].nunique():,}"
    )

    # ---------------------------------------------------------
    # 5. SERIES COVERAGE
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("2. TRAIN / TEST SERIES COVERAGE")
    print("=" * 70)

    train_series = set(
        train_df[SERIES_COLUMNS]
        .astype(str)
        .agg("||".join, axis=1)
        .unique()
    )

    test_series = set(
        test_df[SERIES_COLUMNS]
        .astype(str)
        .agg("||".join, axis=1)
        .unique()
    )

    common_series = train_series.intersection(test_series)
    unseen_test_series = test_series - train_series

    print(f"\nUnique train series:       {len(train_series):,}")
    print(f"Unique test series:        {len(test_series):,}")
    print(f"Series seen in both:       {len(common_series):,}")
    print(f"Unseen test series:        {len(unseen_test_series):,}")

    if len(test_series) > 0:
        unseen_percentage = (
            len(unseen_test_series) /
            len(test_series)
        ) * 100

        print(
            f"Unseen test series %:      "
            f"{unseen_percentage:.2f}%"
        )

    # ---------------------------------------------------------
    # 6. OBSERVATIONS PER SERIES
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("3. SERIES LENGTH ANALYSIS")
    print("=" * 70)

    series_counts = (
        forecasting_df
        .groupby(SERIES_COLUMNS)
        .size()
        .reset_index(name="observations")
    )

    print(
        f"\nMedian observations per series: "
        f"{series_counts['observations'].median():.0f}"
    )

    print(
        f"Mean observations per series:   "
        f"{series_counts['observations'].mean():.2f}"
    )

    print(
        f"Minimum observations:            "
        f"{series_counts['observations'].min()}"
    )

    print(
        f"Maximum observations:            "
        f"{series_counts['observations'].max()}"
    )

    print("\nSeries with fewer than 30 observations:")
    print(
        (
            series_counts["observations"] < 30
        ).sum()
    )

    print("Series with fewer than 60 observations:")
    print(
        (
            series_counts["observations"] < 60
        ).sum()
    )

    print("Series with fewer than 90 observations:")
    print(
        (
            series_counts["observations"] < 90
        ).sum()
    )

    # ---------------------------------------------------------
    # 7. PRICE DISTRIBUTION
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("4. PRICE DISTRIBUTION")
    print("=" * 70)

    prices = forecasting_df["Modal_Price"]

    print(f"\nMinimum price:  ₹{prices.min():,.2f}")
    print(f"25th percentile: ₹{prices.quantile(0.25):,.2f}")
    print(f"Median price:    ₹{prices.median():,.2f}")
    print(f"75th percentile: ₹{prices.quantile(0.75):,.2f}")
    print(f"Maximum price:   ₹{prices.max():,.2f}")

    print("\nPrice ranges:")

    price_bins = [
        0,
        500,
        1000,
        2000,
        5000,
        10000,
        25000,
        np.inf
    ]

    price_labels = [
        "< ₹500",
        "₹500–₹1,000",
        "₹1,000–₹2,000",
        "₹2,000–₹5,000",
        "₹5,000–₹10,000",
        "₹10,000–₹25,000",
        "> ₹25,000"
    ]

    price_ranges = pd.cut(
        prices,
        bins=price_bins,
        labels=price_labels,
        include_lowest=True
    )

    print(
        price_ranges
        .value_counts()
        .sort_index()
        .to_string()
    )

    # ---------------------------------------------------------
    # 8. COMMODITY DISTRIBUTION
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("5. COMMODITY DISTRIBUTION")
    print("=" * 70)

    commodity_counts = (
        forecasting_df["Commodity"]
        .value_counts()
    )

    print("\nObservations per commodity:")
    print(commodity_counts.to_string())

    # ---------------------------------------------------------
    # 9. TEST ERROR ANALYSIS
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("6. RANDOM FOREST TEST ERROR ANALYSIS")
    print("=" * 70)

    # Reproduce the Random Forest predictions from the
    # saved result file if prediction-level data exists.
    #
    # The current result file only contains aggregate metrics,
    # so we calculate diagnostic baselines directly from the
    # test data here.

    test_analysis = test_df.copy()

    test_analysis["actual"] = test_analysis["target_1d"]

    test_analysis["naive_prediction"] = (
        test_analysis["current_price"]
    )

    test_analysis["naive_error"] = (
        test_analysis["actual"] -
        test_analysis["naive_prediction"]
    )

    test_analysis["naive_abs_error"] = (
        test_analysis["naive_error"].abs()
    )

    test_analysis["actual_change"] = (
        test_analysis["actual"] -
        test_analysis["current_price"]
    )

    print(
        f"\nNaive test MAE: "
        f"₹{test_analysis['naive_abs_error'].mean():.2f}"
    )

    print(
        f"Naive test RMSE: "
        f"₹{np.sqrt((test_analysis['naive_error'] ** 2).mean()):.2f}"
    )

    # ---------------------------------------------------------
    # 10. COMMODITY-LEVEL NAIVE PERFORMANCE
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("7. NAIVE PERFORMANCE BY COMMODITY")
    print("=" * 70)

    commodity_performance = (
        test_analysis
        .groupby("Commodity")
        .agg(
            observations=("actual", "size"),
            mean_price=("actual", "mean"),
            naive_mae=("naive_abs_error", "mean"),
            naive_rmse=(
                "naive_error",
                lambda x: np.sqrt(np.mean(x ** 2))
            )
        )
        .sort_values("naive_mae")
    )

    print(
        commodity_performance
        .round(2)
        .to_string()
    )

    # ---------------------------------------------------------
    # 11. PRICE-RANGE NAIVE PERFORMANCE
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("8. NAIVE PERFORMANCE BY PRICE RANGE")
    print("=" * 70)

    test_analysis["price_range"] = pd.cut(
        test_analysis["actual"],
        bins=price_bins,
        labels=price_labels,
        include_lowest=True
    )

    price_performance = (
        test_analysis
        .groupby("price_range", observed=True)
        .agg(
            observations=("actual", "size"),
            mean_price=("actual", "mean"),
            naive_mae=("naive_abs_error", "mean")
        )
    )

    print(
        price_performance
        .round(2)
        .to_string()
    )

    # ---------------------------------------------------------
    # 12. LARGE ERROR ANALYSIS
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("9. LARGE NAIVE ERRORS")
    print("=" * 70)

    print(
        "\nPercentage of test predictions with absolute error >:"
    )

    for threshold in [100, 250, 500, 1000, 2500, 5000]:

        percentage = (
            test_analysis["naive_abs_error"] > threshold
        ).mean() * 100

        print(
            f"₹{threshold:>5}: "
            f"{percentage:>7.2f}%"
        )

    # ---------------------------------------------------------
    # 13. TARGET VOLATILITY
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("10. PRICE VOLATILITY")
    print("=" * 70)

    test_analysis["percentage_change"] = (
        (
            test_analysis["actual"] -
            test_analysis["current_price"]
        )
        /
        test_analysis["current_price"].replace(0, np.nan)
    ) * 100

    valid_changes = (
        test_analysis["percentage_change"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    print(
        f"\nMedian absolute daily change: "
        f"{valid_changes.abs().median():.2f}%"
    )

    print(
        f"Mean absolute daily change:   "
        f"{valid_changes.abs().mean():.2f}%"
    )

    print(
        f"95th percentile absolute change: "
        f"{valid_changes.abs().quantile(0.95):.2f}%"
    )

    print(
        f"Maximum absolute change: "
        f"{valid_changes.abs().max():.2f}%"
    )

    # ---------------------------------------------------------
    # 14. FINAL DIAGNOSIS
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("11. INITIAL DIAGNOSIS")
    print("=" * 70)

    print("\nThe analysis above will help us determine:")

    print(
        "\n1. Whether test series are sufficiently represented "
        "in training."
    )

    print(
        "2. Whether many series are too short for reliable "
        "forecasting."
    )

    print(
        "3. Whether a few high-price commodities dominate "
        "absolute error."
    )

    print(
        "4. Whether price volatility is too high for a simple "
        "one-day global model."
    )

    print(
        "5. Which commodities and price ranges are easiest "
        "or hardest to predict."
    )

    print("\n" + "=" * 70)
    print("GLOBAL DIAGNOSTIC ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()