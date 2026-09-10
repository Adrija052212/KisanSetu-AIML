import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.data.loader import load_market_data
from src.data.cleaner import clean_market_data
from src.features.price_features import create_lag_features


def test_create_lag_features():
    # Load the sample dataset
    file_path = "data/sample/farming_market_prices_500_rows.csv"

    df = load_market_data(file_path)

    # Clean the dataset
    df = clean_market_data(df)

    # The current forecasting series includes Grade.
    # The older sample dataset does not contain this column,
    # so use a default grade for this feature test.
    if "Grade" not in df.columns:
        df["Grade"] = "Local"

    # Create lag features
    df = create_lag_features(df)

    # Check that all expected lag columns were created
    expected_columns = [
        "lag_1",
        "lag_3",
        "lag_7",
        "lag_14",
        "lag_30",
    ]

    for column in expected_columns:
        assert column in df.columns, (
            f"Expected column '{column}' was not created."
        )

    # Check that the lag columns contain numeric values
    for column in expected_columns:
        assert pd.api.types.is_numeric_dtype(df[column]), (
            f"Column '{column}' should contain numeric values."
        )

    # There should be some missing values because
    # lag features require previous observations.
    assert df["lag_1"].isna().sum() > 0
    assert df["lag_3"].isna().sum() > 0
    assert df["lag_7"].isna().sum() > 0
    assert df["lag_14"].isna().sum() > 0
    assert df["lag_30"].isna().sum() > 0