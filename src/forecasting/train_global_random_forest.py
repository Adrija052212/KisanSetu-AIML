import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data
from src.forecasting.dataset import build_forecasting_dataset
from src.forecasting.split import chronological_split, print_split_summary
from src.forecasting.baseline import calculate_metrics, print_metrics


DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"
RESULT_PATH = "data/processed/global_random_forest_results.csv"

TARGET_COLUMN = "target_1d"

NUMERIC_FEATURES = [
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
    "week_of_year",
]

CATEGORICAL_FEATURES = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
]


def build_model():
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_leaf=2,
        max_features="sqrt",
        n_jobs=-1,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def prepare_xy(df):
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    available_features = [
        column for column in features
        if column in df.columns
    ]

    X = df[available_features].copy()
    y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")

    valid = y.notna()

    X = X.loc[valid]
    y = y.loc[valid]

    return X, y


def main():

    print("Loading market dataset...")
    print("-" * 60)

    raw_df = load_market_data(DATA_PATH)
    print(f"Raw rows: {len(raw_df):,}")

    standardized_df = standardize_market_data(raw_df)

    prepared_df = prepare_market_data(standardized_df)
    print(f"Prepared rows: {len(prepared_df):,}")

    print("\nBuilding forecasting dataset...")
    print("-" * 60)

    forecasting_df = build_forecasting_dataset(
        prepared_df,
        horizon=1
    )

    print(f"Forecasting rows: {len(forecasting_df):,}")

    forecasting_df = forecasting_df[
        forecasting_df[TARGET_COLUMN].notna()
    ].copy()

    print(
        f"Rows with available target: "
        f"{len(forecasting_df):,}"
    )

    print("\nCreating chronological split...")
    print("-" * 60)

    train_df, validation_df, test_df = chronological_split(
        forecasting_df
    )

    print_split_summary(
        train_df,
        validation_df,
        test_df
    )

    print("\nPreparing training data...")
    print("-" * 60)

    X_train, y_train = prepare_xy(train_df)
    X_validation, y_validation = prepare_xy(validation_df)
    X_test, y_test = prepare_xy(test_df)

    print(f"Training rows:   {len(X_train):,}")
    print(f"Validation rows: {len(X_validation):,}")
    print(f"Test rows:       {len(X_test):,}")

    print("\nTraining Global Random Forest...")
    print("-" * 60)

    model = build_model()

    model.fit(X_train, y_train)

    print("Training completed.")

    print("\nGenerating predictions...")
    print("-" * 60)

    train_predictions = model.predict(X_train)
    validation_predictions = model.predict(X_validation)
    test_predictions = model.predict(X_test)

    train_metrics = calculate_metrics(
        y_train,
        train_predictions,
        X_train["current_price"]
    )

    validation_metrics = calculate_metrics(
        y_validation,
        validation_predictions,
        X_validation["current_price"]
    )

    test_metrics = calculate_metrics(
        y_test,
        test_predictions,
        X_test["current_price"]
    )

    print_metrics(
        "TRAIN — Global Random Forest",
        train_metrics
    )

    print_metrics(
        "VALIDATION — Global Random Forest",
        validation_metrics
    )

    print_metrics(
        "TEST — Global Random Forest",
        test_metrics
    )

    print("\nComparison with Naive Baseline")
    print("-" * 60)

    naive_test_mae = 130.08
    random_forest_test_mae = test_metrics["MAE"]

    improvement = (
        (naive_test_mae - random_forest_test_mae)
        / naive_test_mae
    ) * 100

    print(f"Naive Test MAE:          ₹{naive_test_mae:.2f}")
    print(
        f"Random Forest Test MAE:  "
        f"₹{random_forest_test_mae:.2f}"
    )
    print(f"Improvement:             {improvement:.2f}%")

    if random_forest_test_mae < naive_test_mae:
        print(
            "\nRESULT: Random Forest BEATS "
            "the Naive baseline."
        )
    else:
        print(
            "\nRESULT: Random Forest does NOT "
            "beat the Naive baseline."
        )

    results = pd.DataFrame([
        {
            "model": "Global Random Forest",
            "split": "train",
            **train_metrics
        },
        {
            "model": "Global Random Forest",
            "split": "validation",
            **validation_metrics
        },
        {
            "model": "Global Random Forest",
            "split": "test",
            **test_metrics
        },
    ])

    results.to_csv(
        RESULT_PATH,
        index=False
    )

    print(
        f"\nResults saved to: {RESULT_PATH}"
    )

    print("\n" + "=" * 60)
    print("GLOBAL RANDOM FOREST TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()