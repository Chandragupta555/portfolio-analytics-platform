from pathlib import Path
from src.data.market_data import MarketDataService

cache_dir = Path("src/data/cache")

# 1. Delete existing cache files if any
for ticker in ["AAPL", "MSFT"]:
    csv_file = cache_dir / f"{ticker}_2024-01-01_2024-01-10.csv"
    if csv_file.exists():
        csv_file.unlink()

service = MarketDataService()

# 2. First call (Live fetch)
df1 = service.fetch_prices(
    tickers=["AAPL", "MSFT"], start_date="2024-01-01", end_date="2024-01-10"
)
print("=== First Call (Live Fetch) ===")
print(df1)

# 3. Second call (Cache hit)
df2 = service.fetch_prices(
    tickers=["AAPL", "MSFT"], start_date="2024-01-01", end_date="2024-01-10"
)
print("\n=== Second Call (Cache Hit) ===")
print(df2)

# 4. Equality check
print("\n=== Equality Check (df1.equals(df2)) ===")
print(f"df1.equals(df2): {df1.equals(df2)}")

# 5. Raw first 3 lines of AAPL CSV
aapl_csv = cache_dir / "AAPL_2024-01-01_2024-01-10.csv"
print("\n=== Raw First 3 Lines of AAPL Cached CSV ===")
if aapl_csv.exists():
    with open(aapl_csv, "r", encoding="utf-8") as f:
        for _ in range(3):
            print(f.readline(), end="")
else:
    print("AAPL CSV file not found!")
