import pandas as pd
import os

PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'
RAW = r'C:\Users\GEO\Desktop\IRise\data\raw'

def deep_audit_gaps():
    print("=== PROFESSIONAL DATA ANALYST GAP ANALYSIS ===")
    
    # Load processed data
    daily = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])
    txn = pd.read_csv(os.path.join(PROC, 'transactions.csv'), parse_dates=['created_at'])
    
    # 1. Date Continuity Check
    expected_range = pd.date_range(start='2024-01-01', end='2026-02-28')
    missing_trading_days = expected_range.difference(daily['date'])
    if len(missing_trading_days) == 0:
        print(f"[OK] All {len(expected_range)} calendar days are present in daily_sales.")
    else:
        print(f"[ALERT] {len(missing_trading_days)} days are MISSING from the daily sales report!")
        print(f"First 10 missing: {missing_trading_days[:10].tolist()}")

    # 2. Transaction Count Reconciliation (Daily Summary vs Order List)
    # Create daily counts from the transaction-level file
    txn['date_only'] = txn['created_at'].dt.date
    txn_daily_counts = txn.groupby('date_only').size().reset_index(name='txn_count')
    txn_daily_counts['date_only'] = pd.to_datetime(txn_daily_counts['date_only'])
    
    # Merge with the official daily sales report
    recon = pd.merge(daily[['date', 'transactions']], txn_daily_counts, left_on='date', right_on='date_only', how='left')
    recon['diff'] = recon['transactions'] - recon['txn_count'].fillna(0)
    
    gaps = recon[recon['diff'] != 0]
    
    if gaps.empty:
        print("[OK] Transaction counts match exactly between summary and detail files.")
    else:
        print(f"[ALERT] Found {len(gaps)} days where transaction counts do not match!")
        print(f"Total missing orders in detail file: {gaps['diff'].sum():.0f}")
        print("\nTop 10 Discrepancy Days:")
        print(gaps.sort_values('diff', ascending=False).head(10)[['date', 'transactions', 'txn_count', 'diff']])

    # 3. Raw Data Integrity Check
    print("\n--- Raw File Inventory ---")
    files = os.listdir(RAW)
    required = [
        'Daily Total Sales By Payment Type.csv',
        'Transactions List.csv',
        'Daily Sales By Order Type.csv',
        'Hourly Sales.csv',
        'Product Sales By Order Type.csv', # This was missing earlier
        'Sales by Product.csv'
    ]
    for req in required:
        status = "PRESENT" if req in files else "MISSING"
        size = f"({os.path.getsize(os.path.join(RAW, req)):,} bytes)" if status == "PRESENT" else ""
        print(f"{req:40} : {status} {size}")

    # 4. Filtered Row Analysis (Why are 635 orders missing?)
    raw_txn_path = os.path.join(RAW, 'Transactions List.csv')
    if os.path.exists(raw_txn_path):
        raw_txn = pd.read_csv(raw_txn_path, encoding='utf-8-sig', low_memory=False)
        print(f"\nRaw Transactions in CSV: {len(raw_txn)}")
        print(f"Processed Transactions : {len(txn)}")
        print(f"Difference (Potential Lost Data): {len(raw_txn) - len(txn)}")
        
        # Check why they were removed in clean_data.py
        # Filter 1: is_void Check
        if 'IsSendBack' in raw_txn.columns:
            voids = (raw_txn['IsSendBack'].str.lower() == 'yes').sum()
            print(f"  - Voided orders (IsSendBack=Yes): {voids}")
        
        # Filter 2: Amount < 1 Check (from 04_fix_data.py)
        # Textbox3 is Gross in this file
        gross_vals = pd.to_numeric(raw_txn['Textbox3'], errors='coerce').fillna(0)
        low_amt = (gross_vals < 1).sum()
        print(f"  - Low amount / Zero orders (< 1 AED): {low_amt}")

if __name__ == "__main__":
    deep_audit_gaps()
