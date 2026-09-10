import sys
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------
# Make project root importable
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_access.supabase_client import get_supabase_client


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
DATASET_PATH = PROJECT_ROOT / "SIH_Cleaned_Dataset.xlsx"

TABLE_NAME = "market_price_history"

BATCH_SIZE = 1000


# ------------------------------------------------------------
# Source → Supabase column mapping
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Required fields
# ------------------------------------------------------------
REQUIRED_COLUMNS = [
    "state",
    "district",
    "market",
    "commodity",
    "variety",
    "grade",
    "date",
    "modal_price",
    "price_unit",
]


# ------------------------------------------------------------
# Clean a batch
# ------------------------------------------------------------
def prepare_batch(batch: pd.DataFrame) -> list[dict]:

    batch = batch.rename(
        columns=COLUMN_MAPPING
    ).copy()

    # Convert date
    batch["date"] = pd.to_datetime(
        batch["date"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "min_price",
        "max_price",
        "modal_price",
        "arrival_quantity",
    ]

    for column in numeric_columns:
        batch[column] = pd.to_numeric(
            batch[column],
            errors="coerce"
        )

    # Clean text columns
    text_columns = [
        "state",
        "district",
        "market",
        "commodity_group",
        "commodity",
        "variety",
        "grade",
        "price_unit",
        "arrival_unit",
    ]

    for column in text_columns:
        batch[column] = (
            batch[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Remove rows missing date/modal price
    batch = batch.dropna(
        subset=["date", "modal_price"]
    )

    # Remove rows missing required text
    for column in [
        "state",
        "district",
        "market",
        "commodity",
        "variety",
        "grade",
        "price_unit",
    ]:
        batch = batch[
            batch[column] != ""
        ]

    # Remove invalid prices
    batch = batch[
        batch["modal_price"] >= 0
    ]

    # Convert date to JSON-safe string
    batch["date"] = batch["date"].dt.strftime(
        "%Y-%m-%d"
    )

    # Convert DataFrame → dictionaries
    records = batch.to_dict(
        orient="records"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Convert NaN / NaT / infinity into JSON-safe None
    # --------------------------------------------------------
    clean_records = []

    for record in records:

        clean_record = {}

        for key, value in record.items():

            if pd.isna(value):
                clean_record[key] = None

            elif isinstance(value, float):
                if not pd.api.types.is_number(value):
                    clean_record[key] = None
                else:
                    clean_record[key] = value

            else:
                clean_record[key] = value

        clean_records.append(
            clean_record
        )

    return clean_records


# ------------------------------------------------------------
# Main import
# ------------------------------------------------------------
def main():

    print("=" * 60)
    print("KisanSetu Market History Import")
    print("=" * 60)

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    print(
        f"\nDataset: {DATASET_PATH}"
    )

    print(
        "Reading Excel file..."
    )

    df = pd.read_excel(
        DATASET_PATH
    )

    print(
        f"Rows found: {len(df):,}"
    )

    # --------------------------------------------------------
    # Check source columns
    # --------------------------------------------------------
    missing_columns = [
        column
        for column in COLUMN_MAPPING
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing source columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Connect to Supabase
    # --------------------------------------------------------
    print(
        "\nConnecting to Supabase..."
    )

    supabase = get_supabase_client()

    print(
        "Supabase connection created."
    )

    # --------------------------------------------------------
    # Import
    # --------------------------------------------------------
    total_rows = len(df)

    total_processed = 0
    total_valid = 0
    total_errors = 0

    print(
        "\nStarting import..."
    )

    print(
        f"Batch size: {BATCH_SIZE:,}"
    )

    print("-" * 60)

    for start in range(
        0,
        total_rows,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total_rows
        )

        batch_number = (
            start // BATCH_SIZE
        ) + 1

        print(
            f"\nBatch {batch_number}: "
            f"rows {start + 1:,}–{end:,}"
        )

        raw_batch = df.iloc[
            start:end
        ]

        records = prepare_batch(
            raw_batch
        )

        total_processed += (
            end - start
        )

        if not records:

            print(
                "No valid records in this batch."
            )

            continue

        total_valid += len(records)

        try:

            response = (
                supabase
                .table(TABLE_NAME)
                .upsert(
                    records,
                    on_conflict=(
                        "state,"
                        "district,"
                        "market,"
                        "commodity,"
                        "variety,"
                        "grade,"
                        "date"
                    ),
                    ignore_duplicates=True,
                )
                .execute()
            )

            inserted_count = len(
                response.data
            )

            print(
                f"Successful records: "
                f"{inserted_count:,}"
            )

        except Exception as error:

            total_errors += len(records)

            print(
                f"ERROR in batch "
                f"{batch_number}:"
            )

            print(error)

            print(
                "\nImport stopped safely."
            )

            break

        progress = (
            end / total_rows
        ) * 100

        print(
            f"Progress: {progress:.2f}%"
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------
    print(
        "\n" + "=" * 60
    )

    print(
        "IMPORT FINISHED"
    )

    print(
        "=" * 60
    )

    print(
        f"Dataset rows:       "
        f"{total_rows:,}"
    )

    print(
        f"Rows processed:     "
        f"{total_processed:,}"
    )

    print(
        f"Valid records:      "
        f"{total_valid:,}"
    )

    print(
        f"Errors encountered: "
        f"{total_errors:,}"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()