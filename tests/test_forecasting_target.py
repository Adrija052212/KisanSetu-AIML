import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.data.loader import load_market_data
from src.data.cleaner import clean_market_data
from src.features.price_features import create_forecasting_target


def test_create_forecasting_target():
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

    # Create 1-day forecasting target
    df = create_forecasting_target(
        df,
        horizon=1,
    )

    # Check that target column was created
    assert "target_1d" in df.columns, (
        "Expected column 'target_1d' was not created."
    )

    # Check that target column is numeric
    assert pd.api.types.is_numeric_dtype(df["target_1d"]), (
        "Column 'target_1d' should contain numeric values."
    )

    # There should be some non-missing target values
    # if the dataset contains valid next-day observations.
    assert df["target_1d"].notna().sum() > 0

    # The target should have at least some missing values
    # because the final observation(s) cannot have a future target.
    assert df["target_1d"].isna().sum() > 0