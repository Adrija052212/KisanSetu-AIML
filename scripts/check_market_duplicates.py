import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

EXCEL_FILE = PROJECT_ROOT / "SIH_Cleaned_Dataset.xlsx"

SERIES_COLUMNS = [
    "State/UT",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
    "Arrival Date",
]


def main():
    print("=" * 70)
    print("KisanSetu - Historical Market Data Duplicate Check")
    print("=" * 70)

    print("\nReading Excel file...")

    data = pd.read_excel(EXCEL_FILE)

    print(f"Total rows: {len(data):,}")

    # Normalize text fields
    text_columns = [
        "State/UT",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade",
    ]

    for column in text_columns:
        data[column] = (
            data[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    data["Arrival Date"] = pd.to_datetime(
        data["Arrival Date"],
        errors="coerce"
    )

    print("\nChecking series/date uniqueness...")

    duplicate_mask = data.duplicated(
        subset=SERIES_COLUMNS,
        keep=False
    )

    duplicate_rows = data[duplicate_mask]

    print(
        f"Rows involved in duplicate series/date records: "
        f"{len(duplicate_rows):,}"
    )

    duplicate_groups = (
        duplicate_rows
        .groupby(SERIES_COLUMNS, dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    print(
        f"Duplicate series/date groups: "
        f"{len(duplicate_groups):,}"
    )

    if duplicate_groups.empty:
        print("\n✅ No duplicate series/date combinations found.")
    else:
        print("\n⚠️ Duplicate combinations found.")

        print("\nTop 20 duplicate groups:")
        print(
            duplicate_groups
            .head(20)
            .to_string(index=False)
        )

    print("\n" + "=" * 70)
    print("Duplicate check complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()