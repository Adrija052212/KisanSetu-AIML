import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.data.loader import load_market_data
from src.data.cleaner import clean_market_data
from src.features.price_features import create_price_change_features


def test_create_price_change_features():
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

    # Create price-change features
    df = create_price_change_features(df)

    # Check that all expected price-change columns were created
    expected_columns = [
        "price_change_1d",
        "price_change_7d",
        "price_change_30d",
    ]

    for column in expected_columns:
        assert column in df.columns, (
            f"Expected column '{column}' was not created."
        )

    # Check that price-change columns contain numeric values
    for column in expected_columns:
        assert pd.api.types.is_numeric_dtype(df[column]), (
            f"Column '{column}' should contain numeric values."
        )

    # Price changes should have missing values at the beginning
    # because previous observations are required.
    assert df["price_change_1d"].isna().sum() > 0
    assert df["price_change_7d"].isna().sum() > 0
    assert df["price_change_30d"].isna().sum() > 0