import sys
from pathlib import Path

import pandas as pd

# Make sure the project root is importable when running this script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_access.market_data import get_market_price_history
from src.data_access.forecast_data import market_records_to_dataframe


STATE = "West Bengal"
DISTRICT = "Nadia"
MARKET = "Krishnanagar"
COMMODITY = "Tomato"
VARIETY = "Local"
GRADE = "A"


def main():
    print("=" * 70)
    print("KisanSetu - Live Market History Diagnostic")
    print("=" * 70)

    print("\nRequested series:")
    print(f"State     : {STATE}")
    print(f"District  : {DISTRICT}")
    print(f"Market    : {MARKET}")
    print(f"Commodity : {COMMODITY}")
    print(f"Variety   : {VARIETY}")
    print(f"Grade     : {GRADE}")

    print("\nFetching live data from data.gov.in...")
    print("This may take up to 30 seconds.\n")

    try:
        records = get_market_price_history(
            state=STATE,
            district=DISTRICT,
            market=MARKET,
            commodity=COMMODITY,
            variety=VARIETY,
            grade=GRADE,
            limit=1000,
        )

    except Exception as exc:
        print("❌ Failed to fetch live market data.")
        print(f"Error: {exc}")
        return

    print(f"Raw records returned: {len(records)}")

    if not records:
        print("\n❌ No records were returned.")
        print("The requested series may not be available through the current API.")
        return

    try:
        data = market_records_to_dataframe(records)
    except Exception as exc:
        print("\n❌ Records could not be converted for forecasting.")
        print(f"Error: {exc}")
        return

    if data.empty:
        print("\n❌ No valid rows remain after cleaning.")
        return

    # ------------------------------------------------------------
    # Basic information
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("1. BASIC DATA INFORMATION")
    print("-" * 70)

    print(f"Valid rows           : {len(data)}")
    print(f"Unique dates         : {data['Date'].nunique()}")
    print(f"First date           : {data['Date'].min().date()}")
    print(f"Last date            : {data['Date'].max().date()}")

    # ------------------------------------------------------------
    # Date continuity
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("2. DATE CONTINUITY")
    print("-" * 70)

    unique_dates = (
        data["Date"]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    date_gaps = unique_dates.diff().dropna()
    large_gaps = date_gaps[date_gaps > pd.Timedelta(days=1)]

    if large_gaps.empty:
        print("✅ No gaps greater than one day were found.")
    else:
        print(f"⚠️ Number of gaps greater than one day: {len(large_gaps)}")

        print("\nLargest gaps:")
        gap_table = pd.DataFrame({
            "previous_date": unique_dates.iloc[:-1].values,
            "next_date": unique_dates.iloc[1:].values,
            "gap": date_gaps.values,
        })

        gap_table = gap_table[
            gap_table["gap"] > pd.Timedelta(days=1)
        ]

        print(gap_table.head(10).to_string(index=False))

    # ------------------------------------------------------------
    # Series consistency
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("3. SERIES CONSISTENCY")
    print("-" * 70)

    expected = {
        "State": STATE,
        "District": DISTRICT,
        "Market": MARKET,
        "Commodity": COMMODITY,
        "Variety": VARIETY,
        "Grade": GRADE,
    }

    for column, expected_value in expected.items():
        values = data[column].dropna().astype(str).str.strip().unique()

        print(f"\n{column}:")
        print(f"  Requested : {expected_value}")
        print(f"  Returned  : {list(values[:10])}")

    # ------------------------------------------------------------
    # Forecast readiness
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("4. FORECAST READINESS")
    print("-" * 70)

    if len(data) >= 31:
        print("✅ At least 31 observations are available.")
        print("The series has enough rows for the 30-day lag/rolling features")
        print("used by the current forecasting pipeline, assuming dates are continuous.")
    else:
        print("⚠️ Fewer than 31 observations are available.")
        print("The current forecasting feature set may not have enough history.")

    if large_gaps.empty and len(data) >= 31:
        print("\n✅ This series looks suitable for an initial real-data forecast test.")
    else:
        print("\n⚠️ This series is NOT yet ideal for the current forecasting pipeline.")

    # ------------------------------------------------------------
    # Price information
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("5. PRICE DATA")
    print("-" * 70)

    print(f"Minimum modal price : ₹{data['Modal_Price'].min():.2f}")
    print(f"Maximum modal price : ₹{data['Modal_Price'].max():.2f}")
    print(f"Average modal price : ₹{data['Modal_Price'].mean():.2f}")

    # ------------------------------------------------------------
    # Samples
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("6. FIRST 5 RECORDS")
    print("-" * 70)

    print(
        data[
            [
                "Date",
                "State",
                "District",
                "Market",
                "Commodity",
                "Variety",
                "Grade",
                "Modal_Price",
                "Arrival_Quantity",
            ]
        ]
        .head(5)
        .to_string(index=False)
    )

    print("\n" + "-" * 70)
    print("7. LAST 5 RECORDS")
    print("-" * 70)

    print(
        data[
            [
                "Date",
                "State",
                "District",
                "Market",
                "Commodity",
                "Variety",
                "Grade",
                "Modal_Price",
                "Arrival_Quantity",
            ]
        ]
        .tail(5)
        .to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("Diagnostic complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()