from src.data.loader import load_market_data
from src.data.validator import validate_dataset
from src.data.cleaner import clean_market_data


file_path = "data/sample/farming_market_prices_500_rows.csv"


# Load
df = load_market_data(file_path)

print(f"Loaded {len(df)} rows.")


# Validate before cleaning
print("\n--- BEFORE CLEANING ---")

is_valid = validate_dataset(df)


# Clean
cleaned_df = clean_market_data(df)


# Validate after cleaning
print("\n--- AFTER CLEANING ---")

validate_dataset(cleaned_df)


# Show final information
print("\nFinal dataset shape:")
print(cleaned_df.shape)

print("\nFirst 5 rows:")
print(cleaned_df.head())