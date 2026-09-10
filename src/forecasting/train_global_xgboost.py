import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from xgboost import XGBRegressor

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data

from src.forecasting.dataset import build_forecasting_dataset
from src.forecasting.split import (
    chronological_split,
    print_split_summary
)

from src.forecasting.baseline import (
    calculate_metrics,
    print_metrics
)


DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"


def main():

    # ========================================================
    # 1. Load and prepare data
    # ========================================================

    print("=" * 60)
    print("GLOBAL XGBOOST PRICE FORECASTING")
    print("=" * 60)

    print("\nLoading market dataset...")
    print("-" * 60)

    df = load_market_data(DATA_PATH)

    print(f"Raw rows: {len(df):,}")

    df = standardize_market_data(df)

    data = prepare_market_data(df)

    print(f"Prepared rows: {len(data):,}")

    # ========================================================
    # 2. Build forecasting dataset
    # ========================================================

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

    # We can only train/evaluate where tomorrow's
    # price is actually available.

    forecast_df = forecast_df[
        forecast_df["target_1d"].notna()
    ].copy()

    print(
        f"Rows with available target: "
        f"{len(forecast_df):,}"
    )

    # ========================================================
    # 3. Chronological split
    # ========================================================

    print("\nCreating chronological split...")
    print("-" * 60)

    train_df, validation_df, test_df = chronological_split(
        forecast_df,
        date_column="Date",
        train_ratio=0.70,
        validation_ratio=0.15,
        test_ratio=0.15
    )

    print_split_summary(
        train_df,
        validation_df,
        test_df
    )

    # ========================================================
    # 4. Define features
    # ========================================================

    numeric_features = [
        "current_price",
        "lag_1",
        "lag_3",
        "lag_7",
        "lag_14",
        "lag_30",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_14",
        "rolling_std_14",
        "rolling_mean_30",
        "rolling_std_30",
        "price_change_1",
        "price_change_7",
        "price_change_30",
        "Arrival_Quantity",
        "day_of_week",
        "day_of_month",
        "month",
        "quarter",
        "day_of_year",
        "week_of_year"
    ]

    categorical_features = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade"
    ]

    # ========================================================
    # 5. Separate X and y
    # ========================================================

    X_train = train_df[
        numeric_features + categorical_features
    ].copy()

    X_validation = validation_df[
        numeric_features + categorical_features
    ].copy()

    X_test = test_df[
        numeric_features + categorical_features
    ].copy()

    y_train = train_df["target_1d"]

    y_validation = validation_df["target_1d"]

    y_test = test_df["target_1d"]

    # ========================================================
    # 6. Preprocessing
    # ========================================================

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                )
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True
                )
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                numeric_features
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_features
            )
        ]
    )

    # ========================================================
    # 7. XGBoost model
    # ========================================================

    xgb_model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        eval_metric="mae",
        tree_method="hist",
        n_jobs=-1,
        random_state=42
    )

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "regressor",
                xgb_model
            )
        ]
    )

    # ========================================================
    # 8. Train
    # ========================================================

    print("\nTraining Global XGBoost...")
    print("-" * 60)

    model.fit(
        X_train,
        y_train
    )

    print("Training completed.")

    # ========================================================
    # 9. Predictions
    # ========================================================

    print("\nGenerating predictions...")
    print("-" * 60)

    train_predictions = model.predict(
        X_train
    )

    validation_predictions = model.predict(
        X_validation
    )

    test_predictions = model.predict(
        X_test
    )

    # ========================================================
    # 10. Metrics
    # ========================================================

    train_metrics = calculate_metrics(
        y_train,
        train_predictions,
        train_df["current_price"]
    )

    validation_metrics = calculate_metrics(
        y_validation,
        validation_predictions,
        validation_df["current_price"]
    )

    test_metrics = calculate_metrics(
        y_test,
        test_predictions,
        test_df["current_price"]
    )

    print_metrics(
        "TRAIN — Global XGBoost",
        train_metrics
    )

    print_metrics(
        "VALIDATION — Global XGBoost",
        validation_metrics
    )

    print_metrics(
        "TEST — Global XGBoost",
        test_metrics
    )

    # ========================================================
    # 11. Compare with Naive baseline
    # ========================================================

    naive_test_mae = 130.08

    improvement = (
        (naive_test_mae - test_metrics["MAE"])
        / naive_test_mae
    ) * 100

    print("\nComparison with Naive Baseline")
    print("-" * 60)

    print(
        f"Naive Test MAE:   "
        f"₹{naive_test_mae:.2f}"
    )

    print(
        f"XGBoost Test MAE: "
        f"₹{test_metrics['MAE']:.2f}"
    )

    print(
        f"Improvement:      "
        f"{improvement:.2f}%"
    )

    if test_metrics["MAE"] < naive_test_mae:

        print(
            "\nRESULT: XGBoost "
            "BEATS the Naive baseline."
        )

    else:

        print(
            "\nRESULT: XGBoost "
            "does NOT beat the Naive baseline."
        )

    # ========================================================
    # 12. Save results
    # ========================================================

    results = pd.DataFrame([
        {
            "Model": "Global XGBoost",
            "Split": "Train",
            **train_metrics
        },
        {
            "Model": "Global XGBoost",
            "Split": "Validation",
            **validation_metrics
        },
        {
            "Model": "Global XGBoost",
            "Split": "Test",
            **test_metrics
        }
    ])

    output_path = (
        "data/processed/"
        "global_xgboost_results.csv"
    )

    results.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nResults saved to: "
        f"{output_path}"
    )

    print("\n" + "=" * 60)
    print(
        "GLOBAL XGBOOST "
        "TEST COMPLETED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()