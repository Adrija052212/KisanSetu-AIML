import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Add project root
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


# --------------------------------------------------
# Dataset path
# --------------------------------------------------

file_path = (
    project_root
    / "data"
    / "raw"
    / "SIH_Cleaned_Dataset.xlsx"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("\nLoading SIH dataset...")
print("-" * 60)

df = pd.read_excel(
    file_path,
    engine="openpyxl"
)

print(
    f"Loaded {len(df):,} rows."
)


# --------------------------------------------------
# Standardize column names
# --------------------------------------------------

from src.data.standardizer import standardize_market_data

df = standardize_market_data(df)


# --------------------------------------------------
# Selected series
# --------------------------------------------------

selected_state = "Tamil Nadu"
selected_district = "Coimbatore"
selected_market = "Pollachi(Uzhavar Sandhai )"
selected_commodity = "Cabbage"
selected_variety = "Cabbage"
selected_grade = "Local"


# --------------------------------------------------
# Filter selected series
# --------------------------------------------------

series = df[
    (df["State"] == selected_state)
    & (df["District"] == selected_district)
    & (df["Market"] == selected_market)
    & (df["Commodity"] == selected_commodity)
    & (df["Variety"] == selected_variety)
    & (df["Grade"] == selected_grade)
].copy()


# --------------------------------------------------
# Sort by date
# --------------------------------------------------

series["Date"] = pd.to_datetime(
    series["Date"]
)

series = (
    series
    .sort_values("Date")
    .reset_index(drop=True)
)


# --------------------------------------------------
# Display information
# --------------------------------------------------

print("\nSelected Series")
print("-" * 60)

print(f"State:       {selected_state}")
print(f"District:    {selected_district}")
print(f"Market:      {selected_market}")
print(f"Commodity:   {selected_commodity}")
print(f"Variety:     {selected_variety}")
print(f"Grade:       {selected_grade}")


# --------------------------------------------------
# Basic statistics
# --------------------------------------------------

print("\nSeries Statistics")
print("-" * 60)

print(
    f"Observations: {len(series):,}"
)

print(
    f"Start date:   {series['Date'].min().date()}"
)

print(
    f"End date:     {series['Date'].max().date()}"
)

print(
    f"Minimum price: ₹{series['Modal_Price'].min():,.2f}"
)

print(
    f"Maximum price: ₹{series['Modal_Price'].max():,.2f}"
)

print(
    f"Average price: ₹{series['Modal_Price'].mean():,.2f}"
)

print(
    f"Median price:  ₹{series['Modal_Price'].median():,.2f}"
)

print(
    f"Price std:     ₹{series['Modal_Price'].std():,.2f}"
)


# --------------------------------------------------
# Check date continuity
# --------------------------------------------------

date_difference = (
    series["Date"]
    .diff()
    .dt.days
    .dropna()
)

print("\nDate Continuity")
print("-" * 60)

print(
    f"Minimum gap: {date_difference.min()} day"
)

print(
    f"Maximum gap: {date_difference.max()} days"
)

print(
    f"Average gap: {date_difference.mean():.2f} days"
)

print(
    f"Missing calendar days: "
    f"{(date_difference - 1).clip(lower=0).sum():.0f}"
)


# --------------------------------------------------
# Display first 10 observations
# --------------------------------------------------

print("\nFirst 10 observations")
print("-" * 60)

print(
    series[
        [
            "Date",
            "Min_Price",
            "Max_Price",
            "Modal_Price",
            "Arrival_Quantity"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# --------------------------------------------------
# Display last 10 observations
# --------------------------------------------------

print("\nLast 10 observations")
print("-" * 60)

print(
    series[
        [
            "Date",
            "Min_Price",
            "Max_Price",
            "Modal_Price",
            "Arrival_Quantity"
        ]
    ]
    .tail(10)
    .to_string(index=False)
)


# --------------------------------------------------
# Save selected series
# --------------------------------------------------

output_path = (
    project_root
    / "data"
    / "processed"
    / "selected_cabbage_series.csv"
)

series.to_csv(
    output_path,
    index=False
)


print("\n")
print("-" * 60)

print(
    f"Selected series saved to:\n"
    f"{output_path}"
)

print("\nAnalysis completed successfully.")