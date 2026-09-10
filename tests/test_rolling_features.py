import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.data.loader import load_market_data
from src.data.cleaner import clean_market_data
from src.features.price_features import create_rolling_features


def test_create_rolling_features():
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

    # Create rolling features
    df = create_rolling_features(df)

    # Check that all expected rolling columns were created
    expected_columns = [
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_30",
        "rolling_std_7",
        "rolling_std_14",
        "rolling_std_30",
    ]

    for column in expected_columns:
        assert column in df.columns, (
            f"Expected column '{column}' was not created."
        )

    # Check that rolling columns contain numeric values
    for column in expected_columns:
        assert pd.api.types.is_numeric_dtype(df[column]), (
            f"Column '{column}' should contain numeric values."
        )

    # Rolling features should have missing values at the beginning
    # because there are not enough previous observations.
    assert df["rolling_mean_7"].isna().sum() > 0
    assert df["rolling_mean_14"].isna().sum() > 0
    assert df["rolling_mean_30"].isna().sum() > 0