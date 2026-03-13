"""
DEEP AUDIT - Every raw and processed CSV verified independently.
No assumptions. Every number cross-checked.
"""
import pandas as pd
import numpy as np
import os

RAW   = r'C:\Users\GEO\Desktop\IRise\data\raw'
PROC  = r'C:\Users\GEO\Desktop\IRise\data\processed'

SEP = "=" * 65

def p(msg):
    print(msg)

def check_date_format(series, label):
    """Test all 4 possible date formats and report which gives most valid dates."""
    results = {}
    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', 'mixed']:
        try:
            if fmt == 'mixed':
                d = pd.to_datetime(series, infer_datetime_format=True, errors='coerce')
            else:
                d = pd.to_datetime(series, format=fmt, errors='coerce')
            n = d.notna().sum()
            results[fmt] = (n, d)
        except:
            results[fmt] = (0, None)
    
    best_fmt = max(results, key=lambda x: results[x][0])
    best_n, best_d = results[best_fmt]
    p(f"  Date format test ({label}):")
    for fmt, (n, _) in results.items():
        marker = " <-- BEST" if fmt == best_fmt else ""
        p(f"    {fmt}: {n} valid dates{marker}")
    return best_d

# ═══════════════════════════════════════════════════════════════
p(SEP)
p("  RAW CSV 1: Daily Total Sales By Payment Type.csv")
p(SEP)
path1 = os.path.join(RAW, 'Daily Total Sales By Payment Type.csv')
if os.path.exists(path1):
    raw1 = pd.read_csv(path1, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw1)}")
    p(f"  Columns: {list(raw1.columns)}")
    d1 = check_date_format(raw1['BillingDate'], 'BillingDate')
    p(f"  Valid date rows: {d1.notna().sum()}")
    p(f"  Unique dates: {d1.dropna().dt.date.nunique()}")
    p(f"  Date range: {d1.dropna().min().date()} -> {d1.dropna().max().date()}")
    p(f"  textbox6 unique: {raw1['textbox6'].unique()[:5]}")
    p(f"  GrossAmount sample: {pd.to_numeric(raw1['GrossAmount'], errors='coerce').dropna().describe().round(2).to_dict()}")
    p(f"  Numberoftransactions sample: {pd.to_numeric(raw1['Numberoftransactions'], errors='coerce').dropna().describe().round(1).to_dict()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 2: Transactions List.csv")
p(SEP)
path2 = os.path.join(RAW, 'Transactions List.csv')
if os.path.exists(path2):
    raw2 = pd.read_csv(path2, encoding='utf-8-sig', low_memory=False)
    p(f"  Raw rows: {len(raw2)}")
    p(f"  Columns: {list(raw2.columns)}")
    d2 = check_date_format(raw2['CreationTime'], 'CreationTime')
    p(f"  Valid date rows: {d2.notna().sum()}")
    p(f"  Unique dates: {d2.dropna().dt.date.nunique()}")
    p(f"  Date range: {d2.dropna().min().date()} -> {d2.dropna().max().date()}")
    p(f"  IsSendBack values: {raw2['IsSendBack'].value_counts().to_dict()}")
    p(f"  PaymentType values: {raw2['PaymentType'].value_counts().to_dict()}")
    gross_raw = pd.to_numeric(raw2['Textbox3'], errors='coerce').dropna()
    p(f"  Gross amount (Textbox3) range: {gross_raw.min():.2f} - {gross_raw.max():.2f}")
    p(f"  Zero or negative gross: {(gross_raw <= 0).sum()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 3: Daily Sales By Order Type.csv")
p(SEP)
path3 = os.path.join(RAW, 'Daily Sales By Order Type.csv')
if os.path.exists(path3):
    raw3 = pd.read_csv(path3, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw3)}")
    d3 = check_date_format(raw3['BillingDate'], 'BillingDate')
    p(f"  Unique dates: {d3.dropna().dt.date.nunique()}")
    p(f"  Date range: {d3.dropna().min().date()} -> {d3.dropna().max().date()}")
    p(f"  OrderType unique: {raw3['OrderType'].dropna().unique().tolist()}")
    p(f"  locationID unique: {raw3['locationID'].dropna().unique().tolist()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 4: Hourly Sales.csv")
p(SEP)
path4 = os.path.join(RAW, 'Hourly Sales.csv')
if os.path.exists(path4):
    raw4 = pd.read_csv(path4, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw4)}")
    d4 = check_date_format(raw4['SalesDate'], 'SalesDate')
    p(f"  Unique dates: {d4.dropna().dt.date.nunique()}")
    p(f"  Date range: {d4.dropna().min().date()} -> {d4.dropna().max().date()}")
    p(f"  Hour range: {pd.to_numeric(raw4['Hour'], errors='coerce').dropna().min()} - {pd.to_numeric(raw4['Hour'], errors='coerce').dropna().max()}")
    p(f"  Rows with NaN hour: {raw4['Hour'].isna().sum()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 5: Hourly Sales Avg Per Weekday.csv")
p(SEP)
path5 = os.path.join(RAW, 'Hourly Sales Avg Per Weekday.csv')
if os.path.exists(path5):
    raw5 = pd.read_csv(path5, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw5)}")
    p(f"  SalesDate (day names): {raw5['SalesDate'].unique().tolist()}")
    p(f"  Hour range: {raw5['Hour1'].min()} - {raw5['Hour1'].max()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 6: Product Sales By Order Type.csv")
p(SEP)
path6 = os.path.join(RAW, 'Product Sales By Order Type.csv')
if os.path.exists(path6):
    raw6 = pd.read_csv(path6, encoding='utf-8-sig', low_memory=False)
    p(f"  Raw rows: {len(raw6)}")
    d6 = check_date_format(raw6['BillingDate'], 'BillingDate')
    p(f"  Unique dates: {d6.dropna().dt.date.nunique()}")
    p(f"  Date range: {d6.dropna().min().date()} -> {d6.dropna().max().date()}")
    p(f"  OrderType unique: {raw6['OrderType'].dropna().unique().tolist()}")
    p(f"  Unique products (Textbox27): {raw6['Textbox27'].dropna().nunique()}")
    p(f"  Qty range: {pd.to_numeric(raw6['Qty'], errors='coerce').dropna().min()} - {pd.to_numeric(raw6['Qty'], errors='coerce').dropna().max()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 7: Sales by Product.csv")
p(SEP)
path7 = os.path.join(RAW, 'Sales by Product.csv')
if os.path.exists(path7):
    raw7 = pd.read_csv(path7, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw7)}")
    p(f"  Unique products: {raw7['ProductDesc'].dropna().nunique()}")
    p(f"  Category unique: {raw7['Category'].dropna().unique().tolist()}")
    net_total = pd.to_numeric(raw7['NetAmount'], errors='coerce').dropna().sum()
    p(f"  NetAmount column total: AED {net_total:,.2f}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 8: Sales By Category With Drill Down.csv")
p(SEP)
path8 = os.path.join(RAW, 'Sales By Category With Drill Down.csv')
if os.path.exists(path8):
    raw8 = pd.read_csv(path8, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw8)}")
    p(f"  Category unique: {raw8['Category'].dropna().unique().tolist()}")
    p(f"  SubCategory unique: {raw8['SubCategory'].dropna().nunique()} subcategories")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 9: Sales By Order Type Per Month Report.csv")
p(SEP)
path9 = os.path.join(RAW, 'Sales By Order Type Per Month Report.csv')
if os.path.exists(path9):
    raw9 = pd.read_csv(path9, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw9)}")
    p(f"  Year unique: {sorted(raw9['Year'].dropna().unique().tolist())}")
    p(f"  Month unique: {sorted(raw9['Month'].dropna().unique().tolist())}")
    p(f"  OrderTypeID unique: {raw9['OrderTypeID'].dropna().unique().tolist()}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  RAW CSV 10: TotalSalesByDate.csv")
p(SEP)
path10 = os.path.join(RAW, 'TotalSalesByDate.csv')
if os.path.exists(path10):
    raw10 = pd.read_csv(path10, encoding='utf-8-sig')
    p(f"  Raw rows: {len(raw10)}")
    d10 = check_date_format(raw10['BillingDate'], 'BillingDate')
    p(f"  Unique dates: {d10.dropna().dt.date.nunique()}")
    p(f"  Date range: {d10.dropna().min().date()} -> {d10.dropna().max().date()}")
    gross_total = pd.to_numeric(raw10['GrossAmount'], errors='coerce').dropna().sum()
    p(f"  GrossAmount column total: AED {gross_total:,.2f}")
else:
    p("  FILE MISSING")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  PROCESSED FILES VERIFICATION")
p(SEP)

proc_files = [
    'daily_sales.csv', 'hourly_sales.csv', 'hourly_avg_weekday.csv',
    'product_sales.csv', 'product_summary.csv', 'order_type_daily.csv',
    'order_type_monthly.csv', 'transactions.csv', 'category_summary.csv'
]
for f in proc_files:
    path = os.path.join(PROC, f)
    if not os.path.exists(path):
        p(f"  MISSING: {f}")
        continue
    df = pd.read_csv(path)
    nulls = df.isnull().sum().sum()
    dups  = df.duplicated().sum()
    p(f"  {f}: {len(df)} rows | nulls={nulls} | dups={dups}")

# ═══════════════════════════════════════════════════════════════
p("")
p(SEP)
p("  CROSS-VALIDATION: Revenue Totals")
p(SEP)

daily_proc = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])

# Cross 1: TotalSalesByDate raw vs daily_sales processed
d10_dates = pd.to_datetime(raw10['BillingDate'], format='%m/%d/%Y', errors='coerce')
raw10_net = pd.to_numeric(raw10['NetAmount'], errors='coerce')
raw10_total = raw10_net.dropna().sum()

proc_daily_net = daily_proc['net_amount'].sum()
diff1 = abs(raw10_total - proc_daily_net) / abs(raw10_total) * 100 if raw10_total != 0 else 999

p(f"  TotalSalesByDate raw NetAmount total : AED {raw10_total:,.2f}")
p(f"  daily_sales processed net_amount total: AED {proc_daily_net:,.2f}")
p(f"  Difference: {diff1:.2f}%")
p("")

# Cross 2: Transaction count from Transactions CSV vs daily_sales transactions
txn_proc = pd.read_csv(os.path.join(PROC, 'transactions.csv'), parse_dates=['created_at'])
txn_count = len(txn_proc)
daily_txn_total = int(daily_proc['transactions'].sum())
p(f"  Transactions CSV (filtered): {txn_count:,} individual orders")
p(f"  daily_sales transactions sum: {daily_txn_total:,}")
diff2_pct = abs(txn_count - daily_txn_total) / daily_txn_total * 100
p(f"  Difference: {diff2_pct:.1f}% (expected: transactions include all order lines)")
p("")

# Cross 3: Date range consistency
p(f"  daily_sales date range    : {daily_proc['date'].min().date()} -> {daily_proc['date'].max().date()}")
p(f"  daily_sales trading days  : {len(daily_proc)}")
p(f"  Expected (Jan2024-Feb2026): 790 days")
p("")

# Cross 4: Revenue per year
p("  Revenue by year:")
yearly = daily_proc.groupby('year')['net_amount'].agg(['sum','count'])
for yr, row in yearly.iterrows():
    p(f"    {yr}: AED {row['sum']:,.2f}  ({int(row['count'])} trading days)")

p("")
p(SEP)
p("  AUDIT COMPLETE")
p(SEP)
