from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# 1. LOAD SELECTED SERIES
# =========================================================

file_path = Path("data/processed/selected_cabbage_series.csv")

if not file_path.exists():
    raise FileNotFoundError(
        f"Dataset not found: {file_path}"
    )

print("Loading selected cabbage series...")
print("-" * 60)

df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = (
    df.dropna(subset=["Date"])
      .sort_values("Date")
      .reset_index(drop=True)
)

print(f"Loaded {len(df):,} observations.")


# =========================================================
# 2. BASIC SERIES INFORMATION
# =========================================================

print("\nSeries Information")
print("-" * 60)

print(f"Start date: {df['Date'].min().date()}")
print(f"End date:   {df['Date'].max().date()}")
print(f"Observations: {len(df):,}")

print("\nColumns:")
print(df.columns.tolist())


# =========================================================
# 3. PRICE STATISTICS
# =========================================================

print("\nModal Price Statistics")
print("-" * 60)

print(
    df["Modal_Price"].describe().to_string()
)


# =========================================================
# 4. PRICE CHANGES
# =========================================================

df["Price_Change"] = df["Modal_Price"].diff()

df["Price_Change_Pct"] = (
    df["Modal_Price"].pct_change() * 100
)


print("\nPrice Change Statistics")
print("-" * 60)

print(
    df["Price_Change"].describe().to_string()
)


# =========================================================
# 5. LARGEST PRICE MOVEMENTS
# =========================================================

print("\nLargest Price Increases")
print("-" * 60)

largest_increases = (
    df.nlargest(10, "Price_Change")[
        [
            "Date",
            "Modal_Price",
            "Price_Change",
            "Price_Change_Pct"
        ]
    ]
)

print(largest_increases.to_string(index=False))


print("\nLargest Price Decreases")
print("-" * 60)

largest_decreases = (
    df.nsmallest(10, "Price_Change")[
        [
            "Date",
            "Modal_Price",
            "Price_Change",
            "Price_Change_Pct"
        ]
    ]
)

print(largest_decreases.to_string(index=False))


# =========================================================
# 6. PRICE AUTOCORRELATION
# =========================================================

print("\nPrice Autocorrelation")
print("-" * 60)

for lag in [1, 3, 7, 14, 30]:

    correlation = df["Modal_Price"].autocorr(
        lag=lag
    )

    print(
        f"Lag {lag:>2} day(s): {correlation:.4f}"
    )


# =========================================================
# 7. ARRIVAL QUANTITY RELATIONSHIP
# =========================================================

if "Arrival_Quantity" in df.columns:

    df["Arrival_Quantity"] = pd.to_numeric(
        df["Arrival_Quantity"],
        errors="coerce"
    )

    correlation = df["Modal_Price"].corr(
        df["Arrival_Quantity"]
    )

    print("\nArrival Quantity vs Price")
    print("-" * 60)

    print(
        f"Correlation: {correlation:.4f}"
    )


# =========================================================
# 8. ROLLING STATISTICS
# =========================================================

df["Rolling_Mean_7"] = (
    df["Modal_Price"]
    .rolling(window=7)
    .mean()
)

df["Rolling_Mean_30"] = (
    df["Modal_Price"]
    .rolling(window=30)
    .mean()
)


# =========================================================
# 9. PRICE TREND PLOT
# =========================================================

plt.figure(figsize=(14, 6))

plt.plot(
    df["Date"],
    df["Modal_Price"],
    label="Modal Price"
)

plt.plot(
    df["Date"],
    df["Rolling_Mean_7"],
    label="7-Day Moving Average"
)

plt.plot(
    df["Date"],
    df["Rolling_Mean_30"],
    label="30-Day Moving Average"
)

plt.title(
    "Cabbage Modal Price - Pollachi Uzhavar Sandhai"
)

plt.xlabel("Date")
plt.ylabel("Price (₹/quintal)")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()


price_plot_path = Path(
    "data/processed/cabbage_price_trend.png"
)

plt.savefig(
    price_plot_path,
    dpi=150,
    bbox_inches="tight"
)

print("\nPrice trend plot saved to:")
print(price_plot_path)

plt.show()


# =========================================================
# 10. ARRIVAL QUANTITY PLOT
# =========================================================

if "Arrival_Quantity" in df.columns:

    plt.figure(figsize=(14, 5))

    plt.plot(
        df["Date"],
        df["Arrival_Quantity"]
    )

    plt.title(
        "Cabbage Arrival Quantity - Pollachi Uzhavar Sandhai"
    )

    plt.xlabel("Date")
    plt.ylabel("Arrival Quantity")

    plt.grid(True, alpha=0.3)

    plt.tight_layout()


    arrival_plot_path = Path(
        "data/processed/cabbage_arrival_quantity.png"
    )

    plt.savefig(
        arrival_plot_path,
        dpi=150,
        bbox_inches="tight"
    )

    print("\nArrival quantity plot saved to:")
    print(arrival_plot_path)

    plt.show()


# =========================================================
# 11. WEEKLY PRICE ANALYSIS
# =========================================================

df["Day_of_Week"] = df["Date"].dt.day_name()

weekly_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekly_analysis = (
    df.groupby("Day_of_Week")["Modal_Price"]
      .agg(["mean", "median", "std", "count"])
      .reindex(weekly_order)
)

print("\nPrice by Day of Week")
print("-" * 60)

print(
    weekly_analysis.to_string()
)


# =========================================================
# 12. MONTHLY PRICE ANALYSIS
# =========================================================

df["Month"] = df["Date"].dt.to_period("M")

monthly_analysis = (
    df.groupby("Month")["Modal_Price"]
      .agg(["mean", "median", "min", "max", "std", "count"])
)

print("\nMonthly Price Analysis")
print("-" * 60)

print(
    monthly_analysis.to_string()
)


# =========================================================
# 13. CHECK FOR MISSING VALUES
# =========================================================

print("\nMissing Values")
print("-" * 60)

missing_values = df.isna().sum()

print(
    missing_values[missing_values > 0].to_string()
    if (missing_values > 0).any()
    else "No missing values."
)


# =========================================================
# 14. FINAL SUMMARY
# =========================================================

print("\n" + "=" * 60)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 60)

print(f"Observations analyzed: {len(df):,}")
print(
    f"Price range: ₹{df['Modal_Price'].min():,.2f}"
    f" - ₹{df['Modal_Price'].max():,.2f}"
)

print(
    f"Average price: ₹{df['Modal_Price'].mean():,.2f}"
)

print(
    f"Median price: ₹{df['Modal_Price'].median():,.2f}"
)

print(
    f"Latest price: ₹{df.iloc[-1]['Modal_Price']:,.2f}"
)

print("\nEDA output files:")
print(f"1. {price_plot_path}")

if "Arrival_Quantity" in df.columns:
    print(f"2. {arrival_plot_path}")

print("\nReady for forecasting feature engineering.")