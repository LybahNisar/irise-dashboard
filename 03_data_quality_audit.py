"""
IRise Chaiiwala - Data Quality Audit
Checks every processed CSV for:
  - Missing values
  - Duplicates
  - Outliers (IQR method)
  - Logical inconsistencies (negative amounts, future dates, etc.)
  - Cross-file validation (totals matching)
"""

import pandas as pd
import numpy as np
import os

PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'
REPORTS = r'C:\Users\GEO\Desktop\IRise\reports'
issues = []   # collect all problems found

def flag(file, col, problem, detail):
    issues.append({'file': file, 'column': col, 'problem': problem, 'detail': detail})
    print(f"  [FLAG] {problem} in '{col}': {detail}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─────────────────────────────────────────────────────────────────
# HELPER: generic checks for any dataframe
# ─────────────────────────────────────────────────────────────────
def generic_checks(df, name, numeric_cols=None, date_col=None):
    print(f"\n--- {name} ({len(df)} rows) ---")

    # 1. Shape
    print(f"  Shape: {df.shape}")

    # 2. Missing values
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if nulls.empty:
        print("  Missing values: NONE")
    else:
        for col, n in nulls.items():
            pct = n / len(df) * 100
            flag(name, col, 'Missing values', f"{n} ({pct:.1f}%)")

    # 3. Duplicates
    dups = df.duplicated().sum()
    if dups == 0:
        print("  Duplicates: NONE")
    else:
        flag(name, 'ALL', 'Duplicate rows', f"{dups} duplicate rows found")

    # 4. Numeric column checks
    if numeric_cols:
        for col in numeric_cols:
            if col not in df.columns:
                continue
            s = pd.to_numeric(df[col], errors='coerce')

            # Negative values
            neg = (s < 0).sum()
            if neg > 0:
                flag(name, col, 'Negative values', f"{neg} rows with negative {col}")

            # Zero values
            zeros = (s == 0).sum()
            if zeros > 0:
                print(f"  Note: {zeros} zero values in '{col}' (may be expected)")

            # Outliers (IQR method)
            Q1 = s.quantile(0.25)
            Q3 = s.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 3 * IQR
            upper = Q3 + 3 * IQR
            outliers = s[(s < lower) | (s > upper)]
            if not outliers.empty:
                flag(name, col,
                     'Statistical outliers (3xIQR)',
                     f"{len(outliers)} rows | range [{s.min():.2f} - {s.max():.2f}] | "
                     f"expected [{lower:.2f} - {upper:.2f}]")
            else:
                print(f"  Outliers in '{col}': NONE  (range: {s.min():.2f} - {s.max():.2f})")

    # 5. Date checks
    if date_col and date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors='coerce')
        future = (dates > pd.Timestamp('2026-03-05')).sum()
        past   = (dates < pd.Timestamp('2023-01-01')).sum()
        if future > 0:
            flag(name, date_col, 'Future dates', f"{future} dates after today (2026-03-05)")
        if past > 0:
            flag(name, date_col, 'Unexpectedly old dates', f"{past} dates before 2023")
        print(f"  Date range: {dates.min().date()} -> {dates.max().date()}")

    return df


# ─────────────────────────────────────────────────────────────────
# 1. DAILY SALES
# ─────────────────────────────────────────────────────────────────
section("1. DAILY SALES (daily_sales.csv)")
daily = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])

generic_checks(
    daily, 'daily_sales',
    numeric_cols=['transactions', 'gross_amount', 'net_amount', 'tax_amount', 'cash', 'card', 'other', 'aov'],
    date_col='date'
)

# Logical: gross should be >= net
inconsistent = daily[daily['gross_amount'] < daily['net_amount']]
if len(inconsistent) > 0:
    flag('daily_sales', 'gross_amount/net_amount',
         'Logical error', f"{len(inconsistent)} rows where gross < net")
else:
    print("  Gross >= Net check: OK")

# Logical: gross ~ net + tax (allow 1 AED rounding)
diff = (daily['gross_amount'] - (daily['net_amount'] + daily['tax_amount'])).abs()
bad = (diff > 1).sum()
if bad > 0:
    flag('daily_sales', 'gross/net/tax', 'Reconciliation mismatch',
         f"{bad} rows where gross != net + tax (diff > AED 1)")
else:
    print("  Gross = Net + Tax reconciliation: OK")

# Logical: AOV within sensible range (AED 5 - 500)
aov_bad = daily[(daily['aov'] < 5) | (daily['aov'] > 500)]
if len(aov_bad) > 0:
    flag('daily_sales', 'aov', 'AOV out of expected range',
         f"{len(aov_bad)} days with AOV outside AED 5-500")
else:
    print("  AOV range check (AED 5-500): OK")

# Date continuity: check for missing trading days
all_days = pd.date_range(daily['date'].min(), daily['date'].max(), freq='D')
missing_days = all_days.difference(daily['date'])
if len(missing_days) > 0:
    print(f"  Note: {len(missing_days)} calendar days with no sales record (closures/holidays):")
    print(f"    First few: {[str(d.date()) for d in missing_days[:5]]}")
else:
    print("  Date continuity: No gaps")


# ─────────────────────────────────────────────────────────────────
# 2. HOURLY SALES
# ─────────────────────────────────────────────────────────────────
section("2. HOURLY SALES (hourly_sales.csv)")
hourly = pd.read_csv(os.path.join(PROC, 'hourly_sales.csv'), parse_dates=['date'])

generic_checks(
    hourly, 'hourly_sales',
    numeric_cols=['net_amount', 'transactions', 'aov'],
    date_col='date'
)

# Hour range check
invalid_hours = hourly[~hourly['hour'].between(0, 23)]
if len(invalid_hours) > 0:
    flag('hourly_sales', 'hour', 'Invalid hour values', f"{len(invalid_hours)} rows")
else:
    print("  Hour range (0-23): OK")

# Every day should have at least some hourly records
daily_hour_counts = hourly.groupby('date')['hour'].count()
low_hour_days = (daily_hour_counts < 5).sum()
if low_hour_days > 0:
    print(f"  Note: {low_hour_days} dates have fewer than 5 hourly records (possible partial data)")


# ─────────────────────────────────────────────────────────────────
# 3. PRODUCT SALES
# ─────────────────────────────────────────────────────────────────
section("3. PRODUCT SALES (product_sales.csv)")
products = pd.read_csv(os.path.join(PROC, 'product_sales.csv'), parse_dates=['date'])

generic_checks(
    products, 'product_sales',
    numeric_cols=['quantity', 'net_amount', 'gross_amount'],
    date_col='date'
)

# Check for blank product names
blank_names = products['product_name'].str.strip().eq('').sum()
if blank_names > 0:
    flag('product_sales', 'product_name', 'Blank product names', f"{blank_names} rows")
else:
    print("  Blank product names: NONE")

# Check order type values
valid_types = {'Delivery', 'Eat In', 'Take Out', 'Collection', 'Staff', 'On The Fly'}
bad_types = products[~products['order_type'].isin(valid_types)]['order_type'].unique()
if len(bad_types) > 0:
    flag('product_sales', 'order_type', 'Unexpected order type values', str(bad_types))
else:
    print("  Order type values: OK")

print(f"  Unique products: {products['product_name'].nunique()}")
print(f"  Unique order types: {products['order_type'].unique().tolist()}")


# ─────────────────────────────────────────────────────────────────
# 4. ORDER TYPE DAILY
# ─────────────────────────────────────────────────────────────────
section("4. ORDER TYPE DAILY (order_type_daily.csv)")
order_d = pd.read_csv(os.path.join(PROC, 'order_type_daily.csv'), parse_dates=['date'])

generic_checks(
    order_d, 'order_type_daily',
    numeric_cols=['transactions', 'net_amount', 'gross_amount'],
    date_col='date'
)


# ─────────────────────────────────────────────────────────────────
# 5. TRANSACTIONS
# ─────────────────────────────────────────────────────────────────
section("5. TRANSACTIONS (transactions.csv)")
txn = pd.read_csv(os.path.join(PROC, 'transactions.csv'), parse_dates=['created_at'])

generic_checks(
    txn, 'transactions',
    numeric_cols=['gross_amount', 'net_amount', 'tax_amount'],
    date_col='created_at'
)

# Order amount range: each order should be AED 1 - 2000
amt_bad = txn[(txn['net_amount'] < 1) | (txn['net_amount'] > 2000)]
print(f"  Transactions outside AED 1-2000: {len(amt_bad)} rows")
if len(amt_bad) > 0:
    print(f"    Min: {txn['net_amount'].min():.2f}  Max: {txn['net_amount'].max():.2f}")

# Payment type check
print(f"  Unique payment types: {txn['payment_type'].nunique()}")
print(f"  Payment types: {sorted(txn['payment_type'].unique().tolist())}")


# ─────────────────────────────────────────────────────────────────
# 6. PRODUCT SUMMARY
# ─────────────────────────────────────────────────────────────────
section("6. PRODUCT SUMMARY (product_summary.csv)")
prod_sum = pd.read_csv(os.path.join(PROC, 'product_summary.csv'))

generic_checks(
    prod_sum, 'product_summary',
    numeric_cols=['total_qty', 'total_net', 'total_gross']
)


# ─────────────────────────────────────────────────────────────────
# 7. CROSS-FILE VALIDATION
# ─────────────────────────────────────────────────────────────────
section("7. CROSS-FILE VALIDATION")

# Compare daily_sales total vs order_type total
daily_total    = daily['net_amount'].sum()
order_d_total  = order_d['net_amount'].sum()
diff_pct = abs(daily_total - order_d_total) / daily_total * 100
print(f"  daily_sales total    : AED {daily_total:,.2f}")
print(f"  order_type_daily total: AED {order_d_total:,.2f}")
print(f"  Difference           : {diff_pct:.2f}%")
if diff_pct > 2:
    flag('cross-file', 'net_amount',
         'Daily vs Order Type total mismatch', f"{diff_pct:.2f}% difference")
else:
    print("  Cross-file revenue reconciliation: OK (within 2%)")

# Transaction count comparison
daily_txn_total = daily['transactions'].sum()
order_d_txn     = order_d['transactions'].sum()
diff_txn_pct = abs(daily_txn_total - order_d_txn) / daily_txn_total * 100
print(f"\n  daily_sales transactions    : {daily_txn_total:,.0f}")
print(f"  order_type_daily transactions: {order_d_txn:,.0f}")
print(f"  Difference                  : {diff_txn_pct:.2f}%")


# ─────────────────────────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────────────────────────
section("AUDIT SUMMARY")

if not issues:
    print("\n  *** ALL CHECKS PASSED — Data is clean and ready ***")
else:
    print(f"\n  Total issues found: {len(issues)}")
    print()
    df_issues = pd.DataFrame(issues)
    print(df_issues.to_string(index=False))
    df_issues.to_csv(os.path.join(REPORTS, 'data_quality_issues.csv'), index=False)
    print(f"\n  Issues saved to reports/data_quality_issues.csv")

print()
print(f"  Records audited:")
print(f"    daily_sales     : {len(daily):,} rows")
print(f"    hourly_sales    : {len(hourly):,} rows")
print(f"    product_sales   : {len(products):,} rows")
print(f"    order_type_daily: {len(order_d):,} rows")
print(f"    transactions    : {len(txn):,} rows")
print(f"    product_summary : {len(prod_sum):,} rows")
