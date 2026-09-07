from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.forecasting.dataset import (
    build_forecasting_dataset,
    prepare_features_and_target
)


DATA_PATH = Path("data/processed/selected_cabbage_series.csv")
MODEL_PATH = Path("models/price_forecasting/xgboost_cabbage.joblib")
RESULT_PATH = Path("data/processed/xgboost_results.csv")


def calculate_mape(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    non_zero = actual != 0

    return (
        np.mean(
            np.abs(
                (actual[non_zero] - predicted[non_zero])
                / actual[non_zero]
            )
        )
        * 100
    )


def main():

    print("Loading selected cabbage series...")
    print("-" * 60)

    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date").reset_index(drop=True)

    print(f"Original observations: {len(df):,}")

    # ---------------------------------------------------------
    # Build forecasting dataset
    # ---------------------------------------------------------

    forecast_df = build_forecasting_dataset(
        df,
        price_column="Modal_Price",
        date_column="Date",
        group_columns=None,
        horizon=1
    )

    X, y, clean_data = prepare_features_and_target(
        forecast_df,
        target_column="target_1d"
    )

    print(f"Usable observations: {len(X):,}")

    # ---------------------------------------------------------
    # Chronological train / validation / test split
    # ---------------------------------------------------------

    n = len(X)

    train_end = int(n * 0.70)
    validation_end = int(n * 0.85)

    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]

    X_validation = X.iloc[train_end:validation_end]
    y_validation = y.iloc[train_end:validation_end]

    X_test = X.iloc[validation_end:]
    y_test = y.iloc[validation_end:]

    train_data = clean_data.iloc[:train_end]
    validation_data = clean_data.iloc[train_end:validation_end]
    test_data = clean_data.iloc[validation_end:]

    print("\nChronological Split")
    print("-" * 60)

    print(f"Training:   {len(X_train)} observations")
    print(f"Validation: {len(X_validation)} observations")
    print(f"Test:       {len(X_test)} observations")

    print(
        f"\nTraining period:   "
        f"{train_data['Date'].min().date()} → "
        f"{train_data['Date'].max().date()}"
    )

    print(
        f"Validation period: "
        f"{validation_data['Date'].min().date()} → "
        f"{validation_data['Date'].max().date()}"
    )

    print(
        f"Test period:       "
        f"{test_data['Date'].min().date()} → "
        f"{test_data['Date'].max().date()}"
    )

    # ---------------------------------------------------------
    # Train XGBoost
    # ---------------------------------------------------------

    print("\nTraining XGBoost...")
    print("-" * 60)

    model = XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    print("Model training completed.")

    # ---------------------------------------------------------
    # Validation evaluation
    # ---------------------------------------------------------

    validation_predictions = model.predict(X_validation)

    validation_mae = mean_absolute_error(
        y_validation,
        validation_predictions
    )

    validation_rmse = np.sqrt(
        mean_squared_error(
            y_validation,
            validation_predictions
        )
    )

    validation_mape = calculate_mape(
        y_validation,
        validation_predictions
    )

    print("\nValidation Performance")
    print("-" * 60)

    print(f"MAE:  ₹{validation_mae:.2f}")
    print(f"RMSE: ₹{validation_rmse:.2f}")
    print(f"MAPE: {validation_mape:.2f}%")

    # ---------------------------------------------------------
    # Test evaluation
    # ---------------------------------------------------------

    test_predictions = model.predict(X_test)

    test_mae = mean_absolute_error(
        y_test,
        test_predictions
    )

    test_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            test_predictions
        )
    )

    test_mape = calculate_mape(
        y_test,
        test_predictions
    )

    # Directional accuracy
    current_prices = test_data["current_price"].to_numpy()

    actual_direction = np.sign(
        y_test.to_numpy() - current_prices
    )

    predicted_direction = np.sign(
        test_predictions - current_prices
    )

    directional_accuracy = (
        actual_direction == predicted_direction
    ).mean() * 100

    print("\nXGBoost Test Performance")
    print("-" * 60)

    print(f"MAE:                 ₹{test_mae:.2f}")
    print(f"RMSE:                ₹{test_rmse:.2f}")
    print(f"MAPE:                {test_mape:.2f}%")
    print(f"Directional Accuracy: {directional_accuracy:.2f}%")

    # ---------------------------------------------------------
    # Feature importance
    # ---------------------------------------------------------

    feature_importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_
    }).sort_values(
        "Importance",
        ascending=False
    )

    print("\nTop Feature Importances")
    print("-" * 60)

    print(
        feature_importance.head(10).to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Save predictions
    # ---------------------------------------------------------

    results = pd.DataFrame({
        "Date": test_data["Date"].values,
        "Today's_Price": current_prices,
        "Actual_Next_Day_Price": y_test.values,
        "XGBoost_Prediction": test_predictions
    })

    results["Absolute_Error"] = np.abs(
        results["Actual_Next_Day_Price"]
        - results["XGBoost_Prediction"]
    )

    print("\nSample Test Predictions")
    print("-" * 60)

    print(
        results.head(15).to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Save model
    # ---------------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    RESULT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results.to_csv(
        RESULT_PATH,
        index=False
    )

    print("\nModel saved to:")
    print(MODEL_PATH)

    print("\nPredictions saved to:")
    print(RESULT_PATH)

    print("\n" + "=" * 60)
    print("XGBOOST EVALUATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()