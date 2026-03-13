import pandas as pd
import os

RAW = r'C:\Users\GEO\Desktop\IRise\data\raw'
PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'

def final_reconciliation():
    # 1. Load Summary
    daily = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])
    total_expected = daily['transactions'].sum()
    
    # 2. Load Raw Detail
    raw_txn = pd.read_csv(os.path.join(RAW, 'Transactions List.csv'), encoding='utf-8-sig', low_memory=False)
    
    # Analyze Raw Detail per type
    raw_txn['is_void'] = raw_txn['IsSendBack'].str.lower() == 'yes'
    raw_txn['is_low'] = pd.to_numeric(raw_txn['Textbox3'], errors='coerce').fillna(0) < 1
    
    valid_txn = raw_txn[(~raw_txn['is_void']) & (~raw_txn['is_low'])]
    
    print(f"Total Transactions in Summary  : {total_expected}")
    print(f"Raw Rows in Transactions List  : {len(raw_txn)}")
    print(f"  - Minus Voids                : {raw_txn['is_void'].sum()}")
    print(f"  - Minus Low Amt (<1 AED)     : {raw_txn[(~raw_txn['is_void']) & (raw_txn['is_low'])].shape[0]}")
    print(f"Remaining Valid Rows           : {len(valid_txn)}")
    
    discrepancy = total_expected - len(valid_txn)
    print(f"Missing Orders                 : {discrepancy}")
    
    if discrepancy > 0:
        print("\nIdentifying days with missing orders...")
        daily['date_dt'] = daily['date'].dt.date
        valid_txn['date_dt'] = pd.to_datetime(valid_txn['CreationTime']).dt.date
        
        v_counts = valid_txn.groupby('date_dt').size().reset_index(name='v_count')
        recon = pd.merge(daily[['date_dt', 'transactions']], v_counts, left_on='date_dt', right_on='date_dt', how='left')
        recon['diff'] = recon['transactions'] - recon['v_count'].fillna(0)
        
        miss = recon[recon['diff'] > 0]
        print(miss[['date_dt', 'transactions', 'v_count', 'diff']].sort_values('diff', ascending=False).head(10))

if __name__ == "__main__":
    final_reconciliation()
