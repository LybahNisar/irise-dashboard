
import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("product_summary").select("*").execute()
df = pd.DataFrame(res.data)
print("Product Summary Tail:")
print(df.sort_values('total_net', ascending=False).tail(10))
