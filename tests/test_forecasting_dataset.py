from pathlib import Path
import pandas as pd

from src.forecasting.dataset import (
    build_forecasting_dataset,
    prepare_features_and_target
)


# =========================================================
# Load data
# =========================================================

file_path = Path(
    "data/processed/selected_cabbage_series.csv"
)

print("Loading selected cabbage series...")
print("-" * 60)

df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date").reset_index(drop=True)

print(f"Original observations: {len(df):,}")


# =========================================================
# Build forecasting dataset
# =========================================================

print("\nBuilding forecasting dataset...")
print("-" * 60)

forecast_df = build_forecasting_dataset(
    df,
    price_column="Modal_Price",
    date_column="Date",
    group_columns=None,
    horizon=1
)

print(
    f"Forecasting dataset rows: {len(forecast_df):,}"
)


# =========================================================
# Prepare X and y
# =========================================================

X, y, clean_data = prepare_features_and_target(
    forecast_df,
    target_column="target_1d"
)


# =========================================================
# Display results
# =========================================================

print("\nUsable forecasting observations")
print("-" * 60)

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")

print("\nFeature columns:")
for column in X.columns:
    print(f"  - {column}")


# =========================================================
# Check target alignment
# =========================================================

print("\nTarget Alignment Check")
print("-" * 60)

print(
    clean_data[
        [
            "Date",
            "Modal_Price",
            "lag_1",
            "lag_7",
            "target_1d"
        ]
    ].head(10).to_string(index=False)
)


# =========================================================
# Check for NaN
# =========================================================

print("\nMissing Values")
print("-" * 60)

print(
    X.isna().sum().sum(),
    "missing values in X"
)

print(
    y.isna().sum(),
    "missing values in y"
)


# =========================================================
# Verify target is tomorrow's price
# =========================================================

print("\nExact Target Verification")
print("-" * 60)

for i in range(min(5, len(clean_data))):

    current_date = clean_data.iloc[i]["Date"]

    target_date = current_date + pd.Timedelta(days=1)

    target_price = clean_data.iloc[i]["target_1d"]

    actual_next_day = df.loc[
        df["Date"] == target_date,
        "Modal_Price"
    ]

    if len(actual_next_day) == 1:

        expected_price = actual_next_day.iloc[0]

        if target_price == expected_price:
            print(
                f"PASS: {current_date.date()} "
                f"→ {target_date.date()} "
                f"→ ₹{target_price:,.0f}"
            )

        else:
            raise AssertionError(
                f"Target mismatch on {current_date.date()}"
            )


# =========================================================
# Save forecasting dataset
# =========================================================

output_path = Path(
    "data/processed/cabbage_forecasting_dataset.csv"
)

clean_data.to_csv(
    output_path,
    index=False
)

print("\nForecasting dataset saved to:")
print(output_path)


# =========================================================
# Final
# =========================================================

print("\n" + "=" * 60)
print("FORECASTING DATASET TEST PASSED")
print("=" * 60)