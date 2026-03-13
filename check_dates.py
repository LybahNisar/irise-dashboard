
import pandas as pd

df = pd.read_csv('data/processed/daily_sales.csv')
df['date'] = pd.to_datetime(df['date'])
full_range = pd.date_range('2024-01-01', '2026-02-28')
missing = full_range.difference(df['date'])

print(f"Total rows: {len(df)}")
print(f"Date range in data: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Expected days (1 Jan 2024 → 28 Feb 2026): {len(full_range)}")
print(f"Missing days count: {len(missing)}")
if len(missing) > 0:
    print(f"Missing dates: {[str(d.date()) for d in missing]}")
else:
    print("✅ PERFECT: All days present — no gaps in data!")
