import sys
from pathlib import Path

import pandas as pd

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data


file_path = (
    project_root
    / "data"
    / "raw"
    / "SIH_Cleaned_Dataset.xlsx"
)


print("Loading dataset...")

df = load_market_data(file_path)

print("Original columns:")
print(df.columns.tolist())


print("\nStandardizing columns...")

df = standardize_market_data(df)

print("Standardized columns:")
print(df.columns.tolist())


print("\nPreparing dataset...")

prepared_df = prepare_market_data(df)


print("\nFirst 5 rows:")
print(prepared_df.head())


print("\nFinal column names:")
print(prepared_df.columns.tolist())