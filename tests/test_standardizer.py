import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd

from src.data.standardizer import standardize_market_data


file_path = (
    "data/raw/SIH_Cleaned_Dataset.xlsx"
)


print("\nLoading dataset...")
print("-" * 50)

df = pd.read_excel(
    file_path,
    engine="openpyxl"
)

print(
    f"Loaded {len(df):,} rows."
)


print("\nStandardizing columns...")
print("-" * 50)

df = standardize_market_data(df)


print("\nStandardized columns:")
for column in df.columns:
    print(f"  - {column}")


print("\nDataset shape:")
print(df.shape)


print("\nSample:")
print(
    df.head().to_string(index=False)
)


print("\nDate range:")
print(f"Earliest: {df['Date'].min()}")
print(f"Latest:   {df['Date'].max()}")


print("\nStandardization completed successfully.")