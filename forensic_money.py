import pandas as pd
import numpy as np

RAW = r'C:\Users\GEO\Desktop\IRise\data\raw'

def forensic_investigation():
    df = pd.read_csv(os.path.join(RAW, 'Transactions List.csv'), encoding='utf-8-sig', low_memory=False)
    
    # Clean numeric columns
    for col in ['Textbox3', 'Textbox15', 'Textbox17']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Filter only valid ones
    valid = df[df['IsSendBack'].str.lower() == 'no']
    
    # Investigation 1: Is Gross = Net + Tax?
    calc_gross = valid['Textbox15'] + valid['Textbox17']
    diff = (valid['Textbox3'] - calc_gross).abs()
    bad_math = valid[diff > 0.05]
    
    print(f"Transactions with Internal Math Mismatch (>0.05 AED): {len(bad_math)}")
    if len(bad_math) > 0:
        print(f"Total internal difference sum: AED {bad_math['Textbox3'].sum() - (bad_math['Textbox15'].sum() + bad_math['Textbox17'].sum()):,.2f}")
        print("\nSample Mismatch Rows:")
        print(bad_math[['Name', 'Textbox3', 'Textbox15', 'Textbox17']].head(5))

    # Investigation 2: Are there 'Unknown' payment types or blank ones?
    print("\nPayment Type Breakdown:")
    print(valid['PaymentType'].value_counts(dropna=False))

    # Investigation 3: What are columns 11, 19, 25?
    print("\nSample values for mystery columns:")
    print(valid[['Textbox11', 'Textbox19', 'Textbox25']].dropna().head(10))

    # Investigation 4: Compare a single day exactly.
    # From daily_sales: 2025-09-13 has a 12 order gap.
    valid['date'] = pd.to_datetime(valid['CreationTime']).dt.date
    day_target = pd.to_datetime('2025-09-13').date()
    day_data = valid[valid['date'] == day_target]
    
    print(f"\n--- Deep Dive: 2025-09-13 ---")
    print(f"Transaction Count in Log : {len(day_data)}")
    print(f"Total Net in Log         : AED {day_data['Textbox15'].sum():,.2f}")
    
    # Load daily sales raw to check official total for that day
    raw_daily = pd.read_csv(os.path.join(RAW, 'Daily Total Sales By Payment Type.csv'), encoding='utf-8-sig')
    raw_daily['date'] = pd.to_datetime(raw_daily['BillingDate']).dt.date
    summary_day = raw_daily[raw_daily['date'] == day_target]
    
    if not summary_day.empty:
        s_net = pd.to_numeric(summary_day['NetAmount'], errors='coerce').sum()
        s_txn = pd.to_numeric(summary_day['Numberoftransactions'], errors='coerce').sum()
        print(f"Transactions in Summary  : {s_txn}")
        print(f"Net Revenue in Summary   : AED {s_net:,.2f}")
        print(f"NET GAP FOR DAY          : AED {s_net - day_data['Textbox15'].sum():,.2f}")

if __name__ == "__main__":
    import os
    forensic_investigation()
