import pandas as pd
import requests


# ============================================================
# Configuration
# ============================================================

DATA_PATH = "data/raw/SIH_Cleaned_Dataset.xlsx"
API_URL = "http://127.0.0.1:8000/decision/buy"


# ============================================================
# Load Dataset
# ============================================================

print("Loading dataset...")

df = pd.read_excel(DATA_PATH)

df["Arrival Date"] = pd.to_datetime(
    df["Arrival Date"],
    errors="coerce",
)


# ============================================================
# Find a Suitable Real Market Series
# ============================================================

series_columns = [
    "State/UT",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
]

series_counts = (
    df.groupby(series_columns)
    .size()
    .reset_index(name="count")
)

candidate = (
    series_counts[
        series_counts["count"] >= 60
    ]
    .sort_values("count", ascending=False)
    .iloc[0]
)


# ============================================================
# Select the Real Series
# ============================================================

mask = pd.Series(True, index=df.index)

for column in series_columns:
    mask &= df[column].eq(candidate[column])

series = (
    df.loc[mask]
    .sort_values("Arrival Date")
    .copy()
)

# Use the latest 60 historical observations
series = series.tail(60)


# ============================================================
# Display Selected Series
# ============================================================

print("\nSelected real series:")

for column in series_columns:
    print(f"{column}: {candidate[column]}")

print(f"\nHistorical records sent: {len(series)}")

print(
    f"Latest date: "
    f"{series['Arrival Date'].max().date()}"
)

print(
    f"Latest modal price: "
    f"₹{series['Modal Price'].iloc[-1]:.2f}"
)


# ============================================================
# Convert Records to API Format
# ============================================================

records = []

for _, row in series.iterrows():

    records.append(
        {
            "Date": row["Arrival Date"].strftime(
                "%Y-%m-%d"
            ),
            "State": row["State/UT"],
            "District": row["District"],
            "Market": row["Market"],
            "Commodity": row["Commodity"],
            "Variety": row["Variety"],
            "Grade": row["Grade"],
            "Modal_Price": float(
                row["Modal Price"]
            ),
            "Arrival_Quantity": (
                None
                if pd.isna(
                    row["Arrival Quantity"]
                )
                else float(
                    row["Arrival Quantity"]
                )
            ),
        }
    )


# ============================================================
# Build Sell Decision Request
# ============================================================

payload = {
    "historical_data": records,
    "quantity": 10,
    "min_change_percent": 2.0,
}


# ============================================================
# Call FastAPI
# ============================================================

print("\nCalling KisanSetu AI API...")

response = requests.post(
    API_URL,
    json=payload,
)


# ============================================================
# Display Result
# ============================================================

print("\nAPI status:", response.status_code)

print("\nAPI response:")

try:
    print(response.json())

except Exception:
    print(response.text)