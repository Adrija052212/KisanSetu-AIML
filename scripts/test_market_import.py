import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_access.supabase_client import get_supabase_client


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

EXCEL_FILE = PROJECT_ROOT / "SIH_Cleaned_Dataset.xlsx"

TABLE_NAME = "market_price_history"

COLUMN_MAPPING = {
    "State/UT": "state",
    "District": "district",
    "Market": "market",
    "Commodity Group": "commodity_group",
    "Commodity": "commodity",
    "Variety": "variety",
    "Grade": "grade",
    "Min Price": "min_price",
    "Max Price": "max_price",
    "Modal Price": "modal_price",
    "Price Unit": "price_unit",
    "Arrival Quantity": "arrival_quantity",
    "Arrival Unit": "arrival_unit",
    "Arrival Date": "date",
}

DB_COLUMNS = [
    "date",
    "state",
    "district",
    "market",
    "commodity_group",
    "commodity",
    "variety",
    "grade",
    "min_price",
    "max_price",
    "modal_price",
    "price_unit",
    "arrival_quantity",
    "arrival_unit",
]


def prepare_test_data():
    print("Reading first 10 rows from Excel...")

    data = pd.read_excel(
        EXCEL_FILE,
        nrows=10
    )

    print(f"Rows read: {len(data)}")

    # Rename Excel columns to database columns
    data = data.rename(columns=COLUMN_MAPPING)

    # Keep only database columns
    data = data[DB_COLUMNS].copy()

    # Convert date
    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # Convert numeric columns
    numeric_columns = [
        "min_price",
        "max_price",
        "modal_price",
        "arrival_quantity",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Convert NaN to None for Supabase/PostgreSQL
    data = data.where(
        pd.notna(data),
        None
    )

    return data


def main():
    load_dotenv()

    print("=" * 70)
    print("KisanSetu - Test Market Data Import")
    print("=" * 70)

    if not EXCEL_FILE.exists():
        print(f"\n❌ Excel file not found:")
        print(EXCEL_FILE)
        return

    try:
        data = prepare_test_data()
    except Exception as exc:
        print(f"\n❌ Failed to prepare Excel data:")
        print(exc)
        return

    print("\nPrepared data:")
    print(data.to_string(index=False))

    print("\nConnecting to Supabase...")

    try:
        supabase = get_supabase_client()
    except Exception as exc:
        print(f"\n❌ Supabase connection failed:")
        print(exc)
        return

    print("✅ Supabase connection created.")

    records = data.to_dict(orient="records")

    print(f"\nInserting {len(records)} records...")

    try:
        response = (
            supabase
            .table(TABLE_NAME)
            .insert(records)
            .execute()
        )

        inserted_rows = response.data

        print(f"✅ Insert successful.")
        print(f"Rows returned by Supabase: {len(inserted_rows)}")

    except Exception as exc:
        print("\n❌ Insert failed.")
        print(f"Error: {exc}")
        return

    print("\nInserted records:")
    for row in inserted_rows:
        print(
            f"  {row['date']} | "
            f"{row['state']} | "
            f"{row['district']} | "
            f"{row['market']} | "
            f"{row['commodity']} | "
            f"₹{row['modal_price']}"
        )

    print("\n" + "=" * 70)
    print("Test import complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()