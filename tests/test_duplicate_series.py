import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd

from src.data.standardizer import standardize_market_data


FILE_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"

GROUP_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
    "Date"
]


print("\nLoading SIH dataset...")
print("-" * 60)

df = pd.read_excel(
    FILE_PATH,
    engine="openpyxl"
)

print(f"Loaded rows: {len(df):,}")


print("\nStandardizing dataset...")
print("-" * 60)

df = standardize_market_data(df)

print("Standardization completed.")


print("\nChecking duplicates with Grade included...")
print("-" * 60)

duplicate_mask = df.duplicated(
    subset=GROUP_COLUMNS,
    keep=False
)

duplicates = df[duplicate_mask]

duplicate_groups = (
    duplicates
    .groupby(GROUP_COLUMNS)
    .size()
)

print(
    f"Rows involved in duplicates: "
    f"{len(duplicates):,}"
)

print(
    f"Duplicate groups: "
    f"{len(duplicate_groups):,}"
)


print("\nDuplicate group size distribution")
print("-" * 60)

print(
    duplicate_groups
    .value_counts()
    .sort_index()
    .to_string()
)


print("\nSample remaining duplicates")
print("-" * 60)

if len(duplicate_groups) > 0:

    sample_groups = (
        duplicate_groups
        .sort_values(ascending=False)
        .head(10)
    )

    print(sample_groups.to_string())

    print("\nDetailed examples:")

    for group_values in sample_groups.index:

        group_df = df.copy()

        for column, value in zip(
            GROUP_COLUMNS,
            group_values
        ):
            group_df = group_df[
                group_df[column] == value
            ]

        print("\nSeries:")
        for column, value in zip(
            GROUP_COLUMNS,
            group_values
        ):
            print(f"  {column}: {value}")

        print(
            group_df[
                [
                    "Min_Price",
                    "Max_Price",
                    "Modal_Price",
                    "Price_Unit",
                    "Arrival_Quantity",
                    "Arrival_Unit"
                ]
            ].to_string(index=False)
        )

        print("-" * 40)

else:

    print(
        "Excellent! No duplicate "
        "series-date-grade records found."
    )


print("\nDuplicate analysis completed.")