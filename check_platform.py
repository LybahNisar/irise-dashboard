import pandas as pd
import os

RAW = r'C:\Users\GEO\Desktop\IRise\data\raw'

def platform_gap():
    df = pd.read_csv(os.path.join(RAW, 'Transactions List.csv'), encoding='utf-8-sig', low_memory=False)
    df['date'] = pd.to_datetime(df['CreationTime']).dt.date
    
    day_target = pd.to_datetime('2025-09-13').date()
    day_data = df[(df['date'] == day_target) & (df['IsSendBack'].str.lower() == 'no')]
    
    print("Payment Type counts for 2025-09-13 in Transactions List:")
    print(day_data['PaymentType'].value_counts())
    print(f"Total Net: {pd.to_numeric(day_data['Textbox15'], errors='coerce').sum():.2f}")

if __name__ == "__main__":
    platform_gap()
