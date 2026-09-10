from src.data.loader import load_market_data
from src.data.validator import validate_dataset


file_path = "data/sample/farming_market_prices_500_rows.csv"

df = load_market_data(file_path)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", list(df.columns))

is_valid = validate_dataset(df)

if is_valid:
    print("\nKisanSetu data is ready for the next stage.")
else:
    print("\nKisanSetu data needs attention before proceeding.")