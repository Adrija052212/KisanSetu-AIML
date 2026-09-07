from src.data.loader import load_market_data
from src.data.cleaner import clean_market_data
from src.features.price_features import create_time_features


# Load the sample dataset
file_path = "data/sample/farming_market_prices_500_rows.csv"

df = load_market_data(file_path)

# Clean the dataset
df = clean_market_data(df)

# Create time-based features
df = create_time_features(df)

print("\nTime features created successfully.")

print("\nColumns:")
print(df.columns.tolist())

print("\nSample:")
print(
    df[
        [
            "Date",
            "day",
            "month",
            "year",
            "day_of_week",
            "week_of_year"
        ]
    ].head(10)
)