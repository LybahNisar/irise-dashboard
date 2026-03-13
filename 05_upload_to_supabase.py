
import pandas as pd
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY not found in .env file.")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'

def upload_file(file_name, table_name, date_col=None):
    path = os.path.join(PROC, file_name)
    if not os.path.exists(path):
        print(f"⚠️ Skipping {file_name} - not found.")
        return

    print(f"🚀 Uploading {file_name} to {table_name}...")
    df = pd.read_csv(path)
    
    # Clean NaN values for JSON compatibility
    df = df.replace({np.nan: None})
    
    # Convert dataframe to list of dicts
    records = df.to_dict('records')
    
    # Chunked upload (Supabase/Postgres limits)
    chunk_size = 1000
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            # UPSERT to prevent duplicates if script is re-run
            # Note: Requires a primary key or unique constraint set in Supabase
            supabase.table(table_name).upsert(chunk).execute()
            print(f"  ✅ Uploaded rows {i} to {i + len(chunk)}")
        except Exception as e:
            print(f"  ❌ Error uploading chunk {i}: {e}")

if __name__ == "__main__":
    print("="*60)
    print("  IRise Chaiiwala - Supabase Cloud Migration")
    print("="*60)
    
    # Table Mapping
    # 1. Daily Sales
    upload_file('daily_sales.csv', 'daily_sales')
    
    # 2. Hourly Sales
    upload_file('hourly_sales.csv', 'hourly_sales')
    
    # 3. Product Sales (Large file - will be chunked)
    upload_file('product_sales.csv', 'product_sales')
    
    # 4. Order Type Daily
    upload_file('order_type_daily.csv', 'order_type_daily')
    
    # 5. Transactions
    upload_file('transactions.csv', 'transactions')

    # 6. Summaries
    upload_file('product_summary.csv', 'product_summary')
    upload_file('category_summary.csv', 'category_summary')

    print("\n" + "="*60)
    print("  Migration Complete!")
    print("="*60)
