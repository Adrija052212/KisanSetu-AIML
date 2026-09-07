from pathlib import Path

import pandas as pd
import numpy as np

from src.forecasting.dataset import (
    build_forecasting_dataset,
    prepare_features_and_target
)


# =========================================================
# 1. LOAD DATA
# =========================================================

file_path = Path(
    "data/processed/selected_cabbage_series.csv"
)

print("Loading selected cabbage series...")
print("-" * 60)

df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"])

df = (
    df.sort_values("Date")
      .reset_index(drop=True)
)

print(f"Original observations: {len(df):,}")


# =========================================================
# 2. BUILD FORECASTING DATASET
# =========================================================

forecast_df = build_forecasting_dataset(
    df,
    price_column="Modal_Price",
    date_column="Date",
    horizon=1
)

X, y, clean_data = prepare_features_and_target(
    forecast_df,
    target_column="target_1d"
)

print(f"Usable observations: {len(clean_data):,}")


# =========================================================
# 3. CHRONOLOGICAL SPLIT
# =========================================================

n = len(clean_data)

train_end = int(n * 0.70)
validation_end = int(n * 0.85)

train = clean_data.iloc[:train_end].copy()

validation = clean_data.iloc[
    train_end:validation_end
].copy()

test = clean_data.iloc[
    validation_end:
].copy()


print("\nChronological Split")
print("-" * 60)

print(
    f"Training:   {len(train):3d} observations"
)

print(
    f"Validation: {len(validation):3d} observations"
)

print(
    f"Test:       {len(test):3d} observations"
)

print()

print(
    f"Training period:   "
    f"{train['Date'].min().date()} → "
    f"{train['Date'].max().date()}"
)

print(
    f"Validation period: "
    f"{validation['Date'].min().date()} → "
    f"{validation['Date'].max().date()}"
)

print(
    f"Test period:       "
    f"{test['Date'].min().date()} → "
    f"{test['Date'].max().date()}"
)


# =========================================================
# 4. NAIVE BASELINE
# =========================================================

print("\nNaive Baseline")
print("-" * 60)

print(
    "Prediction rule:"
)

print(
    "Tomorrow's price = Today's price"
)

# Naive persistence baseline:
# Tomorrow's price = today's observed price.
#
# Since target_1d represents tomorrow's price,
# the current Modal_Price is the correct baseline input.

actual = test["target_1d"].to_numpy()

predicted = test["Modal_Price"].to_numpy()


# =========================================================
# 5. METRICS
# =========================================================

errors = actual - predicted

absolute_errors = np.abs(errors)

squared_errors = errors ** 2


mae = absolute_errors.mean()

rmse = np.sqrt(
    squared_errors.mean()
)

# Avoid division by zero
non_zero_actual = actual != 0

mape = (
    np.mean(
        np.abs(
            (
                actual[non_zero_actual]
                - predicted[non_zero_actual]
            )
            / actual[non_zero_actual]
        )
    )
    * 100
)


# Directional accuracy

actual_change = np.diff(
    np.concatenate(
        [[test.iloc[0]["lag_1"]], actual]
    )
)

predicted_change = (
    predicted
    - test["lag_1"].to_numpy()
)

actual_direction = np.sign(actual_change)

predicted_direction = np.sign(
    predicted_change
)

directional_accuracy = (
    actual_direction
    == predicted_direction
).mean() * 100


# =========================================================
# 6. PRINT RESULTS
# =========================================================

print(f"MAE:  ₹{mae:,.2f}")

print(f"RMSE: ₹{rmse:,.2f}")

print(f"MAPE: {mape:.2f}%")

print(
    f"Directional Accuracy: "
    f"{directional_accuracy:.2f}%"
)


# =========================================================
# 7. SAMPLE PREDICTIONS
# =========================================================

results = pd.DataFrame({
    "Date": test["Date"].values,
    "Today's_Day_Price": test["Modal_Price"].values,
    "Actual_Next_Day_Price": actual,
    "Naive_Prediction": predicted,
    "Absolute_Error": absolute_errors
})

print("\nSample Test Predictions")
print("-" * 60)

print(
    results.head(15).to_string(
        index=False
    )
)


# =========================================================
# 8. SAVE RESULTS
# =========================================================

output_path = Path(
    "data/processed/naive_baseline_results.csv"
)

results.to_csv(
    output_path,
    index=False
)

print("\nBaseline predictions saved to:")
print(output_path)


print("\n" + "=" * 60)
print("NAIVE BASELINE EVALUATION COMPLETED")
print("=" * 60)