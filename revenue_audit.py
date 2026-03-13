import pandas as pd
import os

RAW = r'C:\Users\GEO\Desktop\IRise\data\raw'
PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'

def revenue_audit():
    daily = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])
    daily_net = daily['net_amount'].sum()
    
    raw_txn = pd.read_csv(os.path.join(RAW, 'Transactions List.csv'), encoding='utf-8-sig', low_memory=False)
    raw_txn['is_void'] = raw_txn['IsSendBack'].str.lower() == 'yes'
    valid_txn = raw_txn[~raw_txn['is_void']]
    
    # Textbox15 is Net Amount
    txn_net = pd.to_numeric(valid_txn['Textbox15'], errors='coerce').sum()
    
    print(f"Revenue in Summary Reported : AED {daily_net:,.2f}")
    print(f"Revenue in Transaction List: AED {txn_net:,.2f}")
    print(f"Difference                  : AED {abs(daily_net - txn_net):,.2f}")

if __name__ == "__main__":
    revenue_audit()
