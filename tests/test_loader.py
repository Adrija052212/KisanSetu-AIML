from src.data.loader import load_market_data


file_path = "data/sample/farming_market_prices_500_rows.csv"

df = load_market_data(file_path)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", list(df.columns))
print(df.head())