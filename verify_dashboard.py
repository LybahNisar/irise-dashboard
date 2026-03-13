
import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Starting Verification...")

try:
    # 1. Total Revenue Check (Supabase vs Local transactions)
    # Get daily sales from Supabase
    print("Fetching data from Supabase...")
    res = supabase.table("daily_sales").select("net_amount").execute()
    sb_total_rev = sum(item['net_amount'] for item in res.data)
    
    # Load transactions.csv
    local_tx = pd.read_csv("data/processed/transactions.csv")
    loc_total_rev = local_tx['net_amount'].sum()
    
    print(f"Total Revenue from Supabase: AED {sb_total_rev:,.2f}")
    print(f"Total Revenue from Raw Source: AED {loc_total_rev:,.2f}")
    print(f"Discrepancy: AED {abs(sb_total_rev - loc_total_rev):,.2f}")
    
    # 2. Number of transaction records 
    sb_days = len(res.data)
    loc_days = len(pd.read_csv("data/processed/daily_sales.csv"))
    print(f"\\nDays captured in Supabase: {sb_days}")
    print(f"Days captured locally: {loc_days}")
    
    # 3. Best selling product check
    prod_res = supabase.table("product_summary").select("product_name,total_net").order("total_net", desc=True).limit(5).execute()
    print("\nTop 5 Products in Supabase:")
    for p in prod_res.data:
        print(f" - {p['product_name']}: AED {p['total_net']:,.2f}")
        
    print("\nSUCCESS: Data Verification Complete")
        
except Exception as e:
    print(f"Error during verification: {e}")
