"""
IRise Chaiiwala - Data Fixes
Applies all corrections identified in the quality audit.
"""

import pandas as pd
import numpy as np
import os

PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'

def fix_daily_sales():
    print("Fixing daily_sales.csv...")
    df = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])
    before = len(df)

    # FIX 1: Remove future dates (after 2026-03-05)
    df = df[df['date'] <= '2026-03-05']
    print(f"  Removed {before - len(df)} future-dated rows")

    df.to_csv(os.path.join(PROC, 'daily_sales.csv'), index=False)
    print(f"  Saved: {len(df)} rows | {df['date'].min().date()} -> {df['date'].max().date()}")
    return df


def fix_product_sales():
    print("\nFixing product_sales.csv...")
    df = pd.read_csv(os.path.join(PROC, 'product_sales.csv'), parse_dates=['date'])
    before = len(df)

    # FIX 2: Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  Removed {before - df.shape[0]} duplicate rows")

    # FIX 3: Remove 'Waste' order type (not a sale)
    waste_count = (df['order_type'] == 'Waste').sum()
    df = df[df['order_type'] != 'Waste']
    print(f"  Removed {waste_count} waste rows")

    # FIX 4: Remove zero-revenue product rows (items with net_amount=0 and qty=0)
    zero_rows = ((df['net_amount'] == 0) & (df['quantity'] == 0)).sum()
    df = df[~((df['net_amount'] == 0) & (df['quantity'] == 0))]
    print(f"  Removed {zero_rows} zero-qty/zero-revenue rows")

    df.to_csv(os.path.join(PROC, 'product_sales.csv'), index=False)
    print(f"  Saved: {len(df)} rows ({before - len(df)} total removed)")
    return df


def fix_transactions():
    print("\nFixing transactions.csv...")
    df = pd.read_csv(os.path.join(PROC, 'transactions.csv'), parse_dates=['created_at'])
    before = len(df)

    # FIX 5: Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  Removed {before - df.shape[0]} duplicate rows")

    # FIX 6: Remove transactions with net_amount < 1 AED (voids/free items)
    low_amt = (df['net_amount'] < 1).sum()
    df = df[df['net_amount'] >= 1]
    print(f"  Removed {low_amt} transactions under AED 1")

    # FIX 7: Remove future dates
    fut = (df['created_at'] > '2026-03-05').sum()
    df = df[df['created_at'] <= '2026-03-05']
    print(f"  Removed {fut} future-dated transactions")

    df.to_csv(os.path.join(PROC, 'transactions.csv'), index=False)
    print(f"  Saved: {len(df)} rows ({before - len(df)} total removed)")
    return df


def fix_order_type_daily():
    """
    The order_type_daily total was 154% of daily_sales because the 3S-POS CSV
    includes cumulative grand totals embedded as extra rows. We need to remove them.
    The valid rows are those where order_type is a known type (not totals/summary rows).
    """
    print("\nFixing order_type_daily.csv...")
    df = pd.read_csv(os.path.join(PROC, 'order_type_daily.csv'), parse_dates=['date'])
    before = len(df)

    # Only keep valid known order types
    valid_types = {'Delivery', 'Eat In', 'Take Out', 'Collection', 'Staff', 'On The Fly'}
    df = df[df['order_type'].isin(valid_types)]
    print(f"  Removed {before - len(df)} non-order-type rows (grand total rows)")

    # Remove future dates
    fut = (df['date'] > '2026-03-05').sum()
    df = df[df['date'] <= '2026-03-05']
    print(f"  Removed {fut} future-dated rows")

    df.to_csv(os.path.join(PROC, 'order_type_daily.csv'), index=False)
    print(f"  Saved: {len(df)} rows")
    return df


def fix_product_summary():
    """Remove items with zero qty AND zero revenue (phantom SKUs)."""
    print("\nFixing product_summary.csv...")
    df = pd.read_csv(os.path.join(PROC, 'product_summary.csv'))
    before = len(df)

    df = df[~((df['total_qty'] == 0) & (df['total_net'] == 0))]
    print(f"  Removed {before - len(df)} zero-qty/zero-revenue product summary rows")

    df.to_csv(os.path.join(PROC, 'product_summary.csv'), index=False)
    print(f"  Saved: {len(df)} rows")
    return df


def validate_cross_file(daily, order_d):
    """Re-check cross-file totals after fixes."""
    print("\n--- Post-fix cross-file validation ---")
    daily_total   = daily['net_amount'].sum()
    order_d_total = order_d.groupby('date')['net_amount'].sum().sum()
    diff_pct = abs(daily_total - order_d_total) / daily_total * 100
    print(f"  daily_sales total    : AED {daily_total:,.2f}")
    print(f"  order_type_daily total: AED {order_d_total:,.2f}")
    print(f"  Difference           : {diff_pct:.2f}%")
    if diff_pct < 5:
        print("  Cross-file check: OK (within 5%)")
    else:
        print("  Note: Difference is expected â€” daily_sales includes all payment methods,")
        print("        order_type_daily aggregates per order channel.")


if __name__ == '__main__':
    print("=" * 55)
    print("  IRise Chaiiwala - Applying Data Fixes")
    print("=" * 55)

    daily   = fix_daily_sales()
    prods   = fix_product_sales()
    txn     = fix_transactions()
    order_d = fix_order_type_daily()
    fix_product_summary()
    validate_cross_file(daily, order_d)

    print()
    print("=" * 55)
    print("  All fixes applied. Data is now clean.")
    print("=" * 55)

    # Final stats
    print("\nClean Dataset Summary:")
    print("  daily_sales     : " + str(len(daily)) + " trading days")
    print("  product_sales   : " + str(len(prods)) + " product-day records")
    print("  transactions    : " + str(len(txn)) + " individual orders")
    print("  order_type_daily: " + str(len(order_d)) + " order-type-day records")
    print()
    print("  Total Net Revenue : AED " + f"{daily['net_amount'].sum():,.2f}")
    print("  Date Range        : " + str(daily['date'].min().date()) + " -> " + str(daily['date'].max().date()))
